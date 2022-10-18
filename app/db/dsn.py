from typing import Optional


def generate_dsn_postgres(
    user: str,
    password: str,
    host: str,
    port: int,
    database_name: str,
    drivers: Optional[str] = None,
) -> str:
    if not drivers:
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database_name}"
    return f"{drivers}://{user}:{password}@{host}:{port}/{database_name}"
