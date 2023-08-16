import logging
from typing import Any, Dict, Optional

from bs4 import BeautifulSoup, NavigableString, ResultSet
from requests import RequestException
import requests_cache

from exceptions import ParserFindTagException


def get_response(
    session: requests_cache.CachedSession, url: str
) -> Optional[requests_cache.AnyResponse]:
    """
    Отправляет GET-запрос на указанный URL с помощью переданной сессии
    и возвращает ответ в виде объекта Response.
    Если возникает ошибка при загрузке страницы,
    функция записывает информацию об ошибке в лог.

    :param session: объект сессии
    :param url: URL страницы
    :return: объект Response или None,
    если возникла ошибка при загрузке страницы
    """
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def find_tag(
    soup: BeautifulSoup, tag: str, attrs: Optional[Dict[str, str]] = None
) -> NavigableString:
    """
    Ищет тег с указанным именем и атрибутами в объекте BeautifulSoup.
    Если тег не найден, функция записывает информацию об ошибке в лог
    и выбрасывает исключение ParserFindTagException.

    :param soup: объект BeautifulSoup
    :param tag: имя тега
    :param attrs: словарь атрибутов тега (по умолчанию None)
    :return: найденный тег
    """
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag


def find_all_tags(
    soup: BeautifulSoup, tag: str, attrs: Optional[Dict[str, str]] = None
) -> ResultSet[Any]:
    """
    Ищет все теги с указанным именем и атрибутами в объекте BeautifulSoup.
    Если теги не найдены, функция записывает информацию об ошибке в лог
    и выбрасывает исключение ParserFindTagException.

    :param soup: объект BeautifulSoup
    :param tag: имя тега
    :param attrs: словарь атрибутов тега (по умолчанию None)
    :return: список найденных тегов
    """
    searched_tags = soup.find_all(tag, attrs=(attrs or {}))
    if searched_tags is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tags
