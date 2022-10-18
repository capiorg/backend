import phonenumbers
from phonenumbers import PhoneNumberFormat
from phonenumbers import format_number

x = phonenumbers.parse("+79189781008", "RU")
print(f"{x.country_code}{x.national_number}")
print(format_number(
            x,
            PhoneNumberFormat.NATIONAL
            ))
