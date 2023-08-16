import datetime as dt
import csv
import logging
from typing import Any, Dict, List

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


def control_output(
    results: List[List[str]] | Dict[str, str], cli_args: Any
) -> None:
    """
    Определяет тип вывода результатов парсинга PEP документов в зависимости
    от выбранного режима и вызывает соответствующую функцию вывода.
    Если тип вывода не задан, то используется функция default_output.

    :param results: список результатов парсинга
    :param cli_args: аргументы командной строки
    :return: None
    """
    output = cli_args.output
    print(type(results))
    print(results)
    if output == 'pretty':
        pretty_output(results)
    elif output == 'file':
        file_output(results, cli_args)
    else:
        default_output(results)


def default_output(results: List[List[str]] | Dict[str, str]) -> None:
    """
    Выводит результаты парсинга в консоль в формате,
    где каждый элемент строки разделен пробелом.

    :param results: список результатов парсинга
    :return: None
    """
    for row in results:
        print(*row)


def pretty_output(results: List[List[str]]) -> None:
    """
    Выводит результаты парсинга в консоль в виде таблицы
    с помощью библиотеки PrettyTable.

    :param results: список результатов парсинга
    :return: None
    """
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(
    results: List[List[str]] | Dict[str, str], cli_args: Any
) -> None:
    """
    Сохраняет результаты парсинга в файл формата csv в директории results
    с названием, содержащим текущую дату и время и выбранный режим работы.
    Также функция записывает информацию о сохранении файла в лог.

    :param results: список результатов парсинга
    :param cli_args: аргументы командной строки
    :return: None
    """
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    now = dt.datetime.now().strftime(DATETIME_FORMAT)
    file_name = f'{cli_args.mode}_{now}.csv'
    file_path = results_dir / file_name

    with open(file_path, 'w', encoding='UTF-8') as file:
        writer = csv.writer(file, dialect='unix')
        writer.writerows(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}')
