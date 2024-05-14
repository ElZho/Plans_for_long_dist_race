from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str            # telegram bot access token 


# @dataclass
# class DB:
#     db_address: str       # Database address


@dataclass
class Config:
    tg_bot: TgBot
    # db: DB


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')))
