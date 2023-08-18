import inspect
from pathlib import Path
try:
    from src import constants
except ModuleNotFoundError:
    assert False, 'Убедитесь что в директории `src` есть файл `constants.py`'
except ImportError:
    assert False, 'Убедитесь что в директории `src` есть файл `constants.py`'


def test_costants_file():
    assert hasattr(constants.URLConstants, 'MAIN_DOC_URL'), (
        'В модуле `constants.py` нет переменной `MAIN_DOC_URL`'
    )
    assert isinstance(constants.URLConstants.MAIN_DOC_URL, str), (
        'В модуле `constants.py` тип переменной `MAIN_DOC_URL` '
        'должен быть `str`'
    )
    variables = [
        code for var, code in inspect.getmembers(constants.URLConstants)
        if not var.startswith('__')
    ]
    assert 'https://peps.python.org/' in variables, (
        'В модуле `constants.py` нет переменной для PEP страницы'
    )
    assert hasattr(constants.PathConstants, 'BASE_DIR'), (
        'В модуле `constants.py` нет переменной `BASE_DIR`'
    )
    assert isinstance(constants.PathConstants.BASE_DIR, Path), (
        'В модуле `constants.py` тип переменной `BASE_DIR` должен быть `Path`'
    )
    assert hasattr(constants.StatusConstants, 'EXPECTED_STATUS'), (
        'В модуле `constants.py` нет переменной `EXPECTED_STATUS`'
    )
    assert isinstance(constants.StatusConstants.EXPECTED_STATUS, dict), (
        'В модуле `constants.py` тип переменной `EXPECTED_STATUS` '
        'должен быть `dict`'
    )
