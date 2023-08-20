import argparse
from typing import List
import logging
from logging.handlers import RotatingFileHandler

from constants import BASE_DIR, NAME_DIR_LOGS, NAME_FILE_LOGS,\
    OUTPUT_FILE, OUTPUT_TABLE, LOG_FORMAT, DT_FORMAT


def configure_argument_parser(
    available_modes: List[str]
) -> argparse.ArgumentParser:
    """
    Создает парсер аргументов командной строки для работы парсера.
    Парсер принимает режимы работы, флаг для очистки кеша
    и дополнительные способы вывода данных.

    :param available_modes: список доступных режимов работы
    :return: объект ArgumentParser
    """
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
            '-c',
            '--clear-cache',
            action='store_true',
            help='Очистка кеша'
        )
    parser.add_argument(
        '-o',
        '--output',
        choices=(OUTPUT_TABLE, OUTPUT_FILE),
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging():
    """
    Настраивает логирование для парсера документации Python.
    Создается директория для логов, файл логов и обработчик логов.
    Форматирование логов происходит в соответствии с заданным форматом.

    :return: None
    """
    log_dir = BASE_DIR / NAME_DIR_LOGS
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / NAME_FILE_LOGS
    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=10 ** 6, backupCount=5
    )
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
