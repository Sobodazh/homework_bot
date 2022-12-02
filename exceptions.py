class HTTPStatusError(Exception):
    """Вызывается в отсутствие соединения с сервером."""

    pass


class TokenError(Exception):
    """Вызывается в случае отсутствия одного из токенов."""

    pass


class ErrorFromAPI(Exception):
    """Вызывается при отсутствии ответа с сервера API."""

    pass
