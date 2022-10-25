from pydantic import BaseSettings, Field
from app.db.dsn import generate_dsn_postgres
from app.services.utils import generate_app_version


class Settings(BaseSettings):
    DB_USERNAME: str = Field(env="POSTGRES_USER", default="postgres")
    DB_PASSWORD: str = Field(env="POSTGRES_PASSWORD", default="password")
    DB_PORT: int = Field(env="POSTGRES_PORT", default=5432)
    DB_HOST: str = Field(env="POSTGRES_HOST", default="127.0.0.1")
    DB_BASENAME: str = Field(env="POSTGRES_DB", default="test_db")

    JWT_SECRET: str = Field(
        env="JWT_SECRET", default=""
    )
    JWT_ALGORITHM: str = Field(env="JWT_ALGORITHM", default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES", default=525600
    )

    BASE_DOMAIN: str = Field(env="BASE_DOMAIN", default="0.0.0.0")

    FILES_API: str = Field(
        env="FILES_API", default="", description="Внутренний контейнер"
    )
    FILES_API_DOMAIN: str = Field(
        env="FILES_API_DOMAIN", default="", description="Домен сервиса файлов"
    )
    PORT: int = Field(env="PORT", default=80)

    DEBUG: bool = Field(env="DEBUG", default=False)
    LOGGING: bool = Field(env="LOGGING", default=True)
    BENCHMARK: bool = Field(env="BENCHMARK", default=False)

    APP_NAME: str = Field(env="APP_NAME")
    APP_VERSION: str = Field(
        env="APP_VERSION",
        default=generate_app_version(v=1),
    )

    DEFAULT_LOCALE = "ru_RU"

    @property
    def dsn(self):
        return generate_dsn_postgres(
            user=self.DB_USERNAME,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database_name=self.DB_BASENAME,
        )

    @property
    def sync_dns(self):
        return generate_dsn_postgres(
            drivers="postgresql",
            user=self.DB_USERNAME,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database_name=self.DB_BASENAME,
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class SettingsOpenSensus(Settings):

    AUTO_MASK_LOGS: bool = Field(env="AUTO_MASK_LOGS", default=True)
    ENABLE_TELEMETRY: bool = Field(env="ENABLE_TELEMETRY", default=True)
    LOG_DATE_FMT: str = Field(env="LOG_DATE_FMT", default="%Y-%m-%d %H:%M:%S")

    @property
    def log_config(self):
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "logging.Formatter",
                    "fmt": "%(levelname)s %(asctime)s %(message)s %(requests)s",
                    "datefmt": self.LOG_DATE_FMT,
                },
                "json": {
                    "()": "app.utils.logging.json_logger.JSONLogFormatter",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "json": {
                    "formatter": "json",
                    "class": "asynclog.AsyncLogDispatcher",
                    "func": "app.utils.logging.json_logger.write_log",
                },
            },
            "loggers": {
                "app": {
                    "handlers": ["json"],
                    "level": "DEBUG" if self.DEBUG else "INFO",
                    "propagate": False,
                },
                "sqlalchemy.engine.Engine": {
                    "handlers": ["json"],
                    "level": "INFO" if self.DEBUG else "ERROR",
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": ["json"],
                    "level": "INFO",
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["json"],
                    "level": "ERROR",
                    "propagate": False,
                },
                "main": {
                    "handlers": ["json"],
                    "level": "DEBUG" if self.DEBUG else "INFO",
                    "propagate": False,
                },
            },
        }

    DEFAULT_SENSITIVE_KEY_WORDS = (
        "password",
        "email",
        "token",
        "Authorization",
        "first_name",
        "last_name",
        "csrftoken",
        "api_key",
        "ctn",
        "phone",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class RedisSettings(BaseSettings):
    REDIS_HOST: str = Field(env="REDIS_HOST", default="localhost")
    REDIS_PORT: str = Field(env="REDIS_PORT", default="6379")
    REDIS_PWD: str = Field(env="REDIS_PWD", default="")
    REDIS_USER: str = Field(env="REDIS_USER", default="default")
    REDIS_DB: int = Field(env="REDIS_DB", default=2)

    @property
    def dsn(self):
        return (
            f"redis://{self.REDIS_USER}:"
            f"{self.REDIS_PWD}@"
            f"{self.REDIS_HOST}:"
            f"{self.REDIS_PORT}/"
            f"{self.REDIS_DB}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class HTTPAuthSettings(BaseSettings):
    USERNAME: str = Field(env="HTTP_AUTH_USERNAME", default="admin")
    PASSWORD: str = Field(env="HTTP_AUTH_PASSWORD", default="admin")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class OtherServicesSettings(BaseSettings):
    SMSAERO_EMAIL: str = Field(env="SMSAERO_EMAIL")
    SMSAERO_API_KEY: str = Field(env="SMSAERO_APIKEY")
    IPWHOIS_API: str = Field(env="IPWHOIS_API")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class HTTPAuthSettingsMarker:
    pass


class BaseSettingsMarker:
    pass


class OtherServicesSettingsMarker:
    pass


settings_app = Settings()
settings_sensus_app = SettingsOpenSensus()
settings_redis = RedisSettings()
settings_services = OtherServicesSettings()
