from fastapi import Form


class OAuth2PhonePasswordRequestForm:
    def __init__(
        self,
        grant_type: str = Form(default=None, regex="password"),
        phone: str = Form(),
        password: str = Form()
    ):
        self.grant_type = grant_type
        self.phone = phone
        self.password = password
