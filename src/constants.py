from pathlib import Path


MAIN_DOC_URL = 'https://docs.python.org/3/'
MAIN_PEP_URL = 'https://peps.python.org/'
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
SECTIONS_PEP = [
    'index-by-category',
    'numerical-index',
    'reserved-pep-numbers'
]
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
PREFIX_PEP = 'pep-'
NAME_DIR_DOWNLOADS = 'downloads'
DOWNLOAD_PATH = 'download.html'
WHATS_NEW_PATH = 'whatsnew/'
