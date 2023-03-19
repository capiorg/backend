import datetime

from pytz import timezone
from sqlalchemy import DateTime
from sqlalchemy import TypeDecorator

MOSCOW_TIMEZONE = timezone('Europe/Moscow')


class TZDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not value.tzinfo:
                raise TypeError("tzinfo is required")
            value = value.astimezone(datetime.timezone.max).replace(tzinfo=MOSCOW_TIMEZONE)
        else:
            value = datetime.datetime.now() + datetime.timedelta(hours=3)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = value.replace(tzinfo=datetime.timezone.utc)
        return value
