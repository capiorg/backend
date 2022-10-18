import re
from config import settings_sensus_app


def mask_string(
    source_string: str,
) -> str:
    """
    Маскирование уязвимых данных по ключам в строке.
    :param source_string: Оригинал строки,
    :return: Строка со скрытыми уязвимыми данными
    """
    # Подготовка паттерна поиска

    regex_str = r'("[^"]*?(?={keywords})[^"]*":\s*")[^"]*"'
    regex_with_keys = regex_str.format(
        keywords="|".join(settings_sensus_app.DEFAULT_SENSITIVE_KEY_WORDS)
    )
    regex_pattern = re.compile(regex_with_keys)
    subst = r'\1***"'

    result = re.sub(
        regex_pattern,
        repl=subst,
        string=source_string,
    )
    return result
