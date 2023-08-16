from itertools import chain
from typing import Dict, List, Tuple
from collections import defaultdict
import re

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tqdm import tqdm
import requests_cache
import logging

from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_response, find_tag, find_all_tags
from constants import BASE_DIR, DOWNLOAD_PATH, MAIN_DOC_URL, MAIN_PEP_URL,\
    NAME_DIR_DOWNLOADS, PREFIX_PEP, SECTIONS_PEP,\
    EXPECTED_STATUS, WHATS_NEW_PATH


def whats_new(
    session: requests_cache.CachedSession
) -> List[Tuple[str, str, str]]:
    """
    Получает список новых возможностей Python с их заголовками
    и ссылками на статьи.

    :param session: Сессия для отправки запросов.
    :type session: requests_cache.CachedSession
    :return: Список кортежей вида
    (ссылка на статью, заголовок, редактор/автор).
    """
    whats_new_url = urljoin(MAIN_DOC_URL, WHATS_NEW_PATH)
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(
        main_div, 'div', attrs={'class': 'toctree-wrapper'}
    )
    sections_by_python = find_all_tags(
        div_with_ul,
        'li', attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]

    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        link = urljoin(whats_new_url, href)
        response = get_response(session, link)
        if response is None:
            return
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((link, h1.text, dl_text))
    return results


def latest_versions(
    session: requests_cache.CachedSession
) -> List[Tuple[str, str, str]]:
    """
    Получает список последних версий Python с их статусами
    и ссылками на документацию.

    :param session: Сессия для отправки запросов.
    :type session: requests_cache.CachedSession
    :return: Список кортежей вида (ссылка на документацию, версия, статус).
    """
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in tqdm(ul_tags):
        if 'All versions' in ul.text:
            a_tags = find_all_tags(ul, 'a')
            break
    else:
        raise Exception('Не найден список c версиями Python')

    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    results = [('Ссылка на документацию', 'Версия', 'Статус')]

    for a_tag in tqdm(a_tags):
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session: requests_cache.CachedSession) -> None:
    """
    Скачивает архив с документацией Python.

    :param session: Сессия для отправки запросов.
    :type session: requests_cache.CachedSession
    """
    downloads_url = urljoin(MAIN_DOC_URL, DOWNLOAD_PATH)
    response = get_response(session, downloads_url)
    if response is None:
        return
    html = BeautifulSoup(response.text, features='lxml')
    table = find_tag(html, 'table')
    pdf_a4_tag = find_tag(
        table, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, a4_link)

    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / NAME_DIR_DOWNLOADS
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(
    session: requests_cache.CachedSession
) -> List[Tuple[str, int]]:
    """
    Получает статусы PEP документов и их количество.

    :param session: Сессия для отправки запросов.
    :type session: requests_cache.CachedSession
    :return: Список кортежей, содержащих статусы
    и количество PEP документов с соответствующим статусом.
    """

    response = get_response(session, MAIN_PEP_URL)
    if response is None:
        return
    status_links = []
    soup = BeautifulSoup(response.text, features='lxml')
    sections = find_all_tags(soup, 'section', {'id': SECTIONS_PEP})
    tbodys = [find_tag(section, 'tbody') for section in sections]
    tr_tags = chain.from_iterable(
        find_all_tags(tbody, 'tr') for tbody in tbodys
    )

    for tr in tqdm(tr_tags):
        status = tr.find('td').text[1:]
        status = EXPECTED_STATUS.get(status)
        if status is None:
            logging.info(f'Получен неизвестный статус')
            continue
        link = tr.find('a').text
        status_links.append((status, PREFIX_PEP + link))

    result_status = get_count_status(session, status_links)
    return [item for item in result_status.items()]


def get_count_status(
    session: requests_cache.CachedSession,
    status_links: List[Tuple[str, str]]
) -> Dict[str, int]:
    """
    Получает URLs PEP с каждым статусом.

    :param session: Сессия для отправки запросов.
    :type session: requests_cache.CachedSession
    :return: Словарь, содержащий количество PEP документов
    с каждым статусом и общее количество документов.
    """
    result_status = defaultdict(int)
    for status, link in tqdm(status_links):
        url = urljoin(MAIN_PEP_URL, link)
        response = get_response(session, url)
        if response is None:
            return
        soup = BeautifulSoup(response.text, features='lxml')
        new_status = find_tag(
            soup, 'section', {'id': 'pep-content'}
        ).find('abbr').text

        if new_status not in status:
            logging.info(
                f'\nНесовпадающие статусы:\n'
                f'{url}\nСтатус в карточке: {new_status}\n'
                f'Ожидаемые статусы: {status}'
            )
        result_status[new_status] += 1
    result_status['Total'] = sum(result_status.values())
    return result_status


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main() -> None:
    """
    Основная функция парсера PEP документов.
    Парсит PEP документы в зависимости от выбранного режима
    и выводит результаты в заданном формате.

    :return: None
    """
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession(expire_after=None)
    session.max_redirects
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    try:
        results = MODE_TO_FUNCTION[parser_mode](session)
    except Exception as e:
        logging.error(str(e))
        results = None

    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
