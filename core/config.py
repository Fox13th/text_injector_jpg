from functools import lru_cache

from pydantic_settings import BaseSettings

from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    input_dir: str
    out_folder: str

    class Config:
        env_file = "../.env"
        extra = "ignore"


@lru_cache(maxsize=None)
def get_settings(env_file: str = None):
    """Получаем настройки приложения, сохраняя в кэш."""
    return Settings(_env_file=env_file)
