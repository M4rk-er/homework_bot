import telegram.error


class StatusResponseNotOKError(Exception):
    pass


class AccessApiError(Exception):
    pass


class SendMessageError(telegram.error.TelegramError):
    pass


class MissingExpectedKeysError(Exception):
    pass


class KeyAcquisitionError(KeyError):
    pass


class TypeIsNotListError(TypeError):
    pass


class TypeIsNotDictError(TypeError):
    pass


class NoStatusInResponse(Exception):
    pass
