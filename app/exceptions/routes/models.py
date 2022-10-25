class IncorrectAuthCodeError(Exception):
    code = 403

    def __init__(self, detail: str):
        self.detail = detail


class RepeatedAuthCodeError(Exception):
    code = 403

    def __init__(self, detail: str):
        self.detail = detail
