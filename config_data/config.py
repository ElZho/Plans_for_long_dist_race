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


# Admins ids
# @dataclass
# class Admin_ids:
#     admin_ids: int


@dataclass
class Config:
    tg_bot: TgBot
    db: DB


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'), admin_ids=env('ADMIN_IDS')), db=DB(db_address=env('DB_ADDRESS')))
