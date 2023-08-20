from pathlib import Path


# URLConstants:
MAIN_DOC_URL = 'https://docs.python.org/3/'
MAIN_PEP_URL = 'https://peps.python.org/'
DOWNLOAD_PATH = 'download.html'
WHATS_NEW_PATH = 'whatsnew/'


# PathConstants:
BASE_DIR = Path(__file__).parent
NAME_DIR_DOWNLOADS = 'downloads'
NAME_DIR_LOGS = 'logs'
NAME_FILE_LOGS = 'parser.log'
NAME_DIR_RESULTS = 'results'


# FormatConstants:
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'


# PEPConstants:
SECTIONS = [
    'index-by-category',
    'numerical-index',
    'reserved-pep-numbers'
]
PREFIX = 'pep-'


# StatusConstants:
EXPECTED_STATUS = {
    'A': ['Active', 'Accepted'],
    'D': ['Deferred'],
    'F': ['Final'],
    'P': ['Provisional'],
    'R': ['Rejected'],
    'S': ['Superseded'],
    'W': ['Withdrawn'],
    '': ['Draft', 'Active'],
}


# ConfigOutputConstants:
OUTPUT_FILE = 'file'
OUTPUT_TABLE = 'pretty'
