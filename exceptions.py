class HTTPStatusError(Exception):
    """Вызывается в отсутствие соединения с сервером."""


class TokenError(Exception):
    """Вызывается в случае отсутствия одного из токенов."""


class ErrorFromAPI(Exception):
    """Вызывается при отсутствии ответа с сервера API."""


class APIError(TypeError):
    """Вызывается при отсутствиии необходимых выходных данных."""
