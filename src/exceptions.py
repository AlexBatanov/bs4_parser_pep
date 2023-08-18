class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class NotFoundVersionList(Exception):
    """Вызывается, когда не найден список с версиями Python"""
    pass
