from datetime import datetime


def generate_app_version(v: int) -> str:
    cur_date = datetime.now()
    base_fmt = cur_date.strftime("%Y.%m.%d%H%M")

    return f"{v}.{base_fmt}"
