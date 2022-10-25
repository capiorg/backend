from phonenumbers import NumberParseException
from phonenumbers import is_valid_number
from phonenumbers import parse as parse_phone_number


class Phone(str):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> None | str:
        try:
            n = parse_phone_number(number=v)
        except NumberParseException as e:
            raise ValueError('Please provide a valid mobile phone number') from e

        if not is_valid_number(n):
            raise ValueError('Please provide a valid mobile phone number')
        return f"{n.country_code}{n.national_number}"
