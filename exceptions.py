class StatusResponseNotOKError(Exception):
    """Код ответа страницы отличен от 200."""


class AccessApiError(Exception):
    """Ошибка при запросе к эндпоинту."""


class MissingExpectedKeysError(Exception):
    """Ошибка при отсутствие в словаре ожидаемого ключа."""


class KeyAcquisitionError(KeyError):
    """Ошибка получения значения по ключу."""


class TypeIsNotListError(TypeError):
    """Ошибка - тип данных не список."""


class TypeIsNotDictError(TypeError):
    """Ошибка - тип данных не словарь."""


class NoStatusInResponse(Exception):
    """отсутствует ключ "status" в словаре."""


class SendMessageError(Exception):
    """Ошибка отправки сообщения."""