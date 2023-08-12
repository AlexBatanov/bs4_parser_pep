import re

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tqdm import tqdm
import requests_cache
import logging

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL, MAIN_PEP_URL
from outputs import control_output
from utils import get_response, find_tag, find_all_tags


def whats_new(session):
    # Вместо константы WHATS_NEW_URL, используйте переменную whats_new_url.
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        # Если основная страница не загрузится, программа закончит работу.
        return
    # Создание "супа".
    soup = BeautifulSoup(response.text, features='lxml')

    # Шаг 1-й: поиск в "супе" тега section с нужным id. Парсеру нужен только 
    # первый элемент, поэтому используется метод find().
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})

    # Шаг 2-й: поиск внутри main_div следующего тега div с классом toctree-wrapper.
    # Здесь тоже нужен только первый элемент, используется метод find().
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})

    # Шаг 3-й: поиск внутри div_with_ul всех элементов списка li с классом toctree-l1.
    # Нужны все теги, поэтому используется метод find_all().
    sections_by_python = div_with_ul.find_all('li', attrs={'class': 'toctree-l1'})
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]


    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        link = urljoin(whats_new_url, href)

        response = get_response(session, link)
        if response is None:
            # Если страница не загрузится, программа перейдёт к следующей ссылке.
            continue  
        soup = BeautifulSoup(response.text, features='lxml')

        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (link, h1.text, dl_text)
        )

    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Не найден список c версиями Python')

    # Инициализация списка для хранения результатов.
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    results = [('Ссылка на документацию','Версия', 'Статус')]
    # Цикл для перебора тегов <a>, полученных ранее.
    for a_tag in a_tags:
        # Извлечение ссылки.
        link = a_tag['href']
        # Поиск паттерна в ссылке.
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:  
            # Если строка соответствует паттерну,
            # переменным присываивается содержимое групп, начиная с первой.
            version, status = text_match.groups()
        else:  
            # Если строка не соответствует паттерну,
            # первой переменной присваивается весь текст, второй — пустая строка.
            version, status = a_tag.text, ''  
        # Добавление полученных переменных в список в виде кортежа.
        results.append(
            (link, version, status)
        )

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    html = BeautifulSoup(response.text, features='lxml')
    table = find_tag(html, 'table')
    pdf_a4_tag = find_tag(table, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')}) 
    a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, a4_link)

    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'download'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')

def pep(session):
    response = get_response(session, MAIN_PEP_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    section = find_tag(soup, 'section', {'id': 'pep-content'})
    tr_tags = section.find_all('tr')
    for tr in tr_tags:
        print(tr)
    # else:
    #     raise Exception('Не найден список c версиями Python')

    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    results = [('Ссылка на документацию','Версия', 'Статус')]

    # for a_tag in a_tags:
    #     link = a_tag['href']
    #     text_match = re.search(pattern, a_tag.text)
    #     if text_match is not None:  
    #         version, status = text_match.groups()
    #     else:  
    #         version, status = a_tag.text, ''  
    #     results.append(
    #         (link, version, status)
    #     )

    # return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}

def main():
    # Запускаем функцию с конфигурацией логов.
    configure_logging()
    # Отмечаем в логах момент запуска программы.
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    # Логируем переданные аргументы командной строки.
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)
    # Логируем завершение работы парсера.
    logging.info('Парсер завершил работу.') 

if __name__ == '__main__':
    main()
