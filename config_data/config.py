import json
from dataclasses import dataclass
from environs import Env


# telegram bot access token
@dataclass
class TgBot:
    token: str
    admin_ids: int


# Database address
@dataclass
class DB:
    db_address: str


@dataclass
class Config:
    tg_bot: TgBot


@dataclass
class DBConfig:
    db: DB


@dataclass
class GuidesConfig:
    plans: list
    vdot_guid: list
    koef: list



def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'), admin_ids=int(env('ADMIN_IDS'))))


def load_db_config(path: str | None = None) -> DBConfig:
    env = Env()
    env.read_env(path)
    return DBConfig(db=DB(db_address=env('DB_ADDRESS')))


def load_guides_config(path: str | None = None):
    """This func loads plans in project"""

    with open(path + '/guides/train_for_race_plans.json', encoding='utf-8') as file:
        plan = json.load(file)
    with open(path + "/guides/vdot.json", encoding='utf-8') as file:
        vdot_guid = json.load(file)
    with open(path + "/guides/base_koef.json", encoding='utf-8') as file:
        koef = json.load(file)
    return GuidesConfig(plans=plan, vdot_guid=vdot_guid, koef=koef)
