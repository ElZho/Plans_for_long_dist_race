from dataclasses import dataclass
from environs import Env


# telegram bot access token
@dataclass
class TgBot:
    token: str
    admin_ids: list[int]


# Database address
@dataclass
class DB:
    db_address: str


@dataclass
class PATH:
    file_path: str


@dataclass
class Config:
    tg_bot: TgBot


@dataclass
class DBConfig:
    db: DB


@dataclass
class PathConfig:
    file_path: PATH


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'), admin_ids=env('ADMIN_IDS')))


def load_db_config(path: str | None = None) -> DBConfig:
    env = Env()
    env.read_env(path)
    return DBConfig(db=DB(db_address=env('DB_ADDRESS')))


def load_path(path: str | None = None) -> PathConfig:
    env = Env()
    env.read_env(path)
    return PathConfig(file_path=PATH(file_path=env('PATH')))
