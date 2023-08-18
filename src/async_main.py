from itertools import chain
from typing import Dict, List, Tuple
from collections import defaultdict
import re
import asyncio
import aiohttp

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tqdm import tqdm
import requests_cache
import logging

from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import async_get_response,\
    find_tag, find_all_tags, get_soup
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
    soup = get_soup(session, whats_new_url)
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
        soup = get_soup(session, link)
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
    soup = get_soup(session, MAIN_DOC_URL)
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
    soup = get_soup(session, downloads_url)
    table = find_tag(soup, 'table')
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


async def pep(
    session: requests_cache.CachedSession
) -> List[Tuple[str, int]]:
    """
    Получает статусы PEP документов и их количество.

    :param session: Сессия для отправки запросов.
    :type session: requests_cache.CachedSession
    :return: Список кортежей, содержащих статусы
    и количество PEP документов с соответствующим статусом.
    """
    status_links = []
    soup = get_soup(session, MAIN_PEP_URL)
    sections = find_all_tags(soup, 'section', {'id': SECTIONS_PEP})
    tbodys = [find_tag(section, 'tbody') for section in sections]
    tr_tags = chain.from_iterable(
        find_all_tags(tbody, 'tr') for tbody in tbodys
    )

    for tr in tr_tags:
        status = tr.find('td').text[1:]
        status = EXPECTED_STATUS.get(status)
        if status is None:
            logging.info('Получен неизвестный статус')
            continue
        link = tr.find('a').text
        status_links.append((status, PREFIX_PEP + link))

    result_status = await get_count_status(status_links)
    return [item for item in result_status.items()]


async def process_link(
        session: aiohttp,
        result_status: Dict[str, int],
        status: str, link: str
) -> None:
    """
    Обрабатывает одну ссылку на страницу PEP и обновляет счетчики статусов.

    :param session: Сессия aiohttp для выполнения запросов.
    :param result_status: Словарь счетчиков статусов.
    :param status: ожидаемый статусов.
    :param link: Ссылка на страницу PEP.
    :return: None.
    """
    url = urljoin(MAIN_PEP_URL, link)
    response = await async_get_response(session, url)
    if response is None:
        return
    soup = BeautifulSoup(response, features='lxml')
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


async def get_count_status(
    status_links: List[Tuple[str, str]]
) -> Dict[str, int]:
    """
    Получает список ссылок на страницы PEP
    и возвращает словарь счетчиков статусов.

    :param status_links: Список кортежей (статус, ссылка на страницу PEP).
    :return: Словарь счетчиков статусов.
    """
    result_status = defaultdict(int)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for status, link in status_links:
            task = process_link(session, result_status, status, link)
            tasks.append(task)

        await asyncio.gather(*tasks)

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

    session = requests_cache.CachedSession()

    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    try:
        if parser_mode == 'pep':
            results = asyncio.run(MODE_TO_FUNCTION[parser_mode](session))
        else:
            results = MODE_TO_FUNCTION[parser_mode](session)
    except Exception as e:
        logging.error(str(e), e)
        results = None

    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
