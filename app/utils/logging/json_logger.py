import datetime
import json
import logging
import traceback
from typing import Union

from opencensus.trace import execution_context, Span

from config import settings_app
from config import settings_sensus_app
from app.utils.logging.helper import mask_string
from app.utils.logging.schemas import BaseJsonLogSchema

LEVEL_TO_NAME = {
    logging.CRITICAL: "Critical",
    logging.ERROR: "Error",
    logging.WARNING: "Warning",
    logging.INFO: "Information",
    logging.DEBUG: "Debug",
    logging.NOTSET: "Trace",
}
EMPTY_VALUE = ""


class JSONLogFormatter(logging.Formatter):
    """
    Кастомизированный класс-форматер для логов в формате json
    """

    def format(
        self, record: logging.LogRecord, *args, **kwargs
    ) -> Union[dict, str]:
        """
        Преобразование объект журнала в json

        :param record: объект журнала
        :return: строка журнала в JSON формате
        """
        to_mask: bool = getattr(record, "to_mask", False)
        log_object: dict = self._format_log_object(record)

        if settings_sensus_app.AUTO_MASK_LOGS and to_mask:
            return mask_string(
                source_string=json.dumps(log_object, ensure_ascii=False),
            )
        else:
            return log_object

    @staticmethod
    def _format_log_object(record: logging.LogRecord) -> dict:
        """
        Перевод записи объекта журнала
        в json формат с необходимым перечнем полей

        :param record: объект журнала
        :return: Словарь с объектами журнала
        """
        now = (
            datetime.datetime.fromtimestamp(record.created)
            .astimezone()
            .replace(microsecond=0)
            .isoformat()
        )
        message = record.getMessage()
        duration = (
            record.duration if hasattr(record, "duration") else record.msecs
        )

        json_log_fields = BaseJsonLogSchema(
            thread=record.process,
            timestamp=now,
            level=record.levelno,
            level_name=LEVEL_TO_NAME[record.levelno],
            message=message,
            source=record.name,
            duration=duration,
            app_name=settings_app.APP_NAME,
            app_version=settings_app.APP_VERSION,
        )

        if hasattr(record, "props"):
            json_log_fields.props = record.props

        if record.exc_info:
            json_log_fields.exceptions = traceback.format_exception(
                *record.exc_info
            )

        elif record.exc_text:
            json_log_fields.exceptions = record.exc_text

        # Работа с телеметрией и трассировкой
        span: Span = (
            execution_context.get_current_span()
            if settings_sensus_app.ENABLE_TELEMETRY
            else EMPTY_VALUE
        )

        if span:
            json_log_fields.trace_id = span.context_tracer.trace_id
            json_log_fields.span_id = span.span_id
            json_log_fields.parent_id = (
                span.parent_span.span_id if span.parent_span else None
            )

        json_log_object = json_log_fields.dict(
            exclude_unset=True,
            by_alias=True,
        )
        # Соединение дополнительных полей логирования
        if hasattr(record, "request_json_fields"):
            json_log_object.update(record.request_json_fields)

        return json_log_object


def write_log(msg):
    print(msg)
