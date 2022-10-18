from phonenumbers import NumberParseException
from phonenumbers import PhoneNumberType
from phonenumbers import is_valid_number
from phonenumbers import number_type
from phonenumbers import parse as parse_phone_number

MOBILE_NUMBER_TYPES = PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE_OR_MOBILE


class Phone(str):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> None | str:
        if v is None:
            return v

        try:
            n = parse_phone_number(number=v)

        except NumberParseException as e:
            raise ValueError('Please provide a valid mobile phone number') from e

        if not is_valid_number(n) or number_type(n) not in MOBILE_NUMBER_TYPES:
            raise ValueError('Please provide a valid mobile phone number')

        return f"{n.country_code}{n.national_number}"
