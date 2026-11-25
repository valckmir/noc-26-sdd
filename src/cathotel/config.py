from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_path: Path = Path("cathotel.db")
    hotel_timezone: str

    @field_validator("hotel_timezone")
    @classmethod
    def validate_hotel_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as error:
            raise ValueError("HOTEL_TIMEZONE must be a valid IANA timezone") from error
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
