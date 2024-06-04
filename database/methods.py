from typing import Any

from sqlalchemy import create_engine, func, update
from sqlalchemy.orm import sessionmaker
from datetime import time, datetime

import logging

from config_data.config import Config, load_config
from database.models import Base, User, Profile, RaceReport, TrainingPlan, PlanDetails

config: Config = load_config()

# initiate modul's logger 
logger = logging.getLogger(__name__)


def add_user(tg_id: int, user_name: str, gender: str):
    """Add new user in database"""
    # create database engine
    engine = create_engine(config.db.db_address, echo=True)
    # create tables if they have not created yet
    Base.metadata.create_all(engine)
    # create database session
    Session = sessionmaker(bind=engine)
    session = Session()
    # select data from database relevant to current user
    user = session.query(User).filter(User.user_id == tg_id).first()
    # create new user if current user not in database
    if user is None:
        new_user = User(user_id=tg_id, user_name=user_name, gender=gender)
        session.add(new_user)
        session.commit()


def create_profile(tg_id: int, weight: float, height: float, age: float, imt: float, max_pulse: int, photo: str):
    """Add new profile for user"""
    # func to write game report into database
    engine = create_engine(config.db.db_address, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter(User.user_id == tg_id).first()
    profile = session.query(Profile).filter(Profile.owner == user.id).first()
    last_profile_id = session.query(func.max(Profile.id)).where(Profile.owner == user.id).first()
    # profile = session.query(Profile).where(Profile.owner == user.user_id).first()
    if last_profile_id:
        print('Профиль', last_profile_id, profile.id)
    else:
        print('Профиля нет!!!')
    if last_profile_id is None:
        print('Что-то пошло не так')
        new_profile = Profile(weight=weight, height=height, age=age, imt=imt, owner=user.id, max_pulse=max_pulse,
                              photo=photo)
        session.add(new_profile)
    else:
        print('Пока все так')
        session.execute(update(Profile).where(Profile.id == last_profile_id[0]).values(weight=weight, height=height,
                                                                               age=age, imt=imt,
                                                                               max_pulse=max_pulse,
                                                                               photo=photo,
                                                                               profile_date=datetime.now()))
    session.commit()


def create_race_report(tg_id: int, distance: str, race_time: time, vdot: int):
    """Add new race report for user"""
    # func to write game report into database
    engine = create_engine(config.db.db_address, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter(User.user_id == tg_id).first()
    new_report = RaceReport(distance=distance, race_time=race_time, owner=user.id, vdot=vdot)
    session.add(new_report)
    session.commit()


def create_training_plan(tg_id: int, plan_name: str, id: int):
    """Create new training plan"""
    # func to write game report into database
    engine = create_engine(config.db.db_address, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter(User.user_id == tg_id).first()
    new_plan = TrainingPlan(id=id, plan_name=plan_name, owner=user.id)
    session.add(new_plan)
    session.commit()


def create_plan_details(tg_id: int, plan_id: int, week: str, first_train: str, second_train: str,
                        third_train: str):
    """Add new training plan details"""
    # func to write game report into database
    engine = create_engine(config.db.db_address, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter(User.user_id == tg_id).first()
    new_plan_details = PlanDetails(owner=user.id, plan_id=plan_id, week=week, first_train=first_train,
                                   second_train=second_train, third_train=third_train)
    session.add(new_plan_details)
    session.commit()


def check_user(tg_id: int) -> bool:
    """Check if user exist"""
    # create database engine
    engine = create_engine(config.db.db_address, echo=True)
    # create tables if they have not created yet
    Base.metadata.create_all(engine)
    # create database session
    Session = sessionmaker(bind=engine)
    session = Session()
    # select data from database relevant to current user
    user = session.query(User).filter(User.user_id == tg_id).first()
    if user:
        return True
    else:
        return False


def make_plan_active(tg_id, plan_id):
    """Change the value of the field 'active' on True """
    engine = create_engine(config.db.db_address, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter(User.user_id == tg_id).first()
    plans = session.query(TrainingPlan).filter(TrainingPlan.owner==user.id, TrainingPlan.completed==False)
    result = 0
    for p in plans:
        if p.active == True:
            return result
    plan = session.query(TrainingPlan).filter(TrainingPlan.id == plan_id, TrainingPlan.owner==user.id,
                                              TrainingPlan.completed==False).first()
    if plan:
        plan.active = True
        result = 1
    session.commit()
    return result


def delete_plan(tg_id, plan_id):
    """Delet the plan and details of the plan """
    engine = create_engine(config.db.db_address, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter(User.user_id == tg_id).first()
    if session.query(TrainingPlan).filter(TrainingPlan.id==plan_id, TrainingPlan.owner==user.id):
        i = session.query(TrainingPlan).filter(TrainingPlan.id==plan_id).one()
        session.delete(i)

    plan_details=session.query(PlanDetails).filter(PlanDetails.plan_id==plan_id, PlanDetails.owner==user.id)
    for detail in plan_details:
        session.delete(detail)
    session.commit()


def make_week_completed(tg_id):
    """Change the value of the field 'completed' on True """
    engine = create_engine(config.db.db_address, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter(User.user_id==tg_id).first()
    plan = session.query(TrainingPlan).filter(TrainingPlan.owner==user.id,
                                              TrainingPlan.active==True).first()
    week = session.query(PlanDetails).filter(PlanDetails.owner==user.id,
                                             PlanDetails.plan_id==plan.id,
                                             PlanDetails.completed==False).first()
    result = 0
    if week:
        week.completed = True
        result = week.week
    if not session.query(PlanDetails).filter(PlanDetails.owner==user.id,
                                             PlanDetails.plan_id==plan.id,
                                             PlanDetails.completed==False).first():
        plan.completed = True
        plan.active = False
        result = 1
    session.commit()

    return result


def get_my_plans(tg_id: int) -> tuple[int, int, int, int] | int:
    """func to get all users plans
    0 - user not exist
    1 - there is no one plan
    """

    engine = create_engine(config.db.db_address, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter(User.user_id == tg_id).first()
    if user is None:
        return 0
    plans = session.query(TrainingPlan).filter(TrainingPlan.owner == user.id)
    if plans is None:
        return 1
    return plans


def get_plan_name(plan_id) -> int:
    engine = create_engine(config.db.db_address, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    plan = session.query(TrainingPlan).filter(TrainingPlan.id == plan_id).first()
    return plan.plan_name


def get_my_plan_details(tg_id: int, plan_id: int) -> tuple[int, int, int, int] | int:
    """ func to get details of selected plan
    0 - user not exist
    1 - plan is not exist """

    engine = create_engine(config.db.db_address, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter(User.user_id == tg_id).first()
    if user is None:
        return 0

    details = session.query(PlanDetails).filter( PlanDetails.owner == user.id, PlanDetails.plan_id == plan_id)

    if details is None:
        return 1
    return details


def get_next_week_plan(tg_id: int) -> int | list:
    """ func to get week plan returns first week which has completed False
    0 - user not exist
    1 - plan is not exist
    2 - plan is completed """

    engine = create_engine(config.db.db_address, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter(User.user_id == tg_id).first()
    plan = session.query(TrainingPlan).filter(TrainingPlan.owner == user.id,
                                              TrainingPlan.active == True).first()

    if plan is None:
        return 0
    detail = session.query(PlanDetails).filter(PlanDetails.owner == user.id, PlanDetails.plan_id == plan.id,
                                                PlanDetails.completed == False).first()
    if detail is None:
        return 1

    return detail


def get_my_race_reports(tg_id: int) -> tuple[int, int, int, int] | int:
    """func to get all users plans
    0 - user not exist
    1 - there is no one plan
    """

    engine = create_engine(config.db.db_address, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter(User.user_id == tg_id).first()
    if user is None:
        return 0
    reports = session.query(RaceReport).filter(RaceReport.owner == user.id)
    if reports is None:
        return 1
    return reports


def get_my_profile(tg_id: int) -> tuple:
    """func to get all users plans
    0 - user not exist
    1 - there is no one plan
    """

    engine = create_engine(config.db.db_address, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter(User.user_id == tg_id).first()
    if user is None:
        return 0
    last_profile_id = session.query(func.max(Profile.id)).where(Profile.owner==user.id).first()

    actual_profile = session.query(Profile).where(Profile.id==last_profile_id[0]).first()

    if actual_profile is None:
        return 1
    return user.user_name, actual_profile, user.gender


def change_profile_data(tg_id: int, **kwargs) -> bool:
    """Changes data which takes in input"""

    engine = create_engine(config.db.db_address, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter(User.user_id == tg_id).first()

    if user is None:
        return False

    else:
        last_profile_id = (
            session.query(func.max(Profile.id)).where(Profile.owner == user.id).one())
        session.execute(update(Profile).where(Profile.id == last_profile_id[0]).values(kwargs))
        # session.execute(update(Profile).where(Profile.id==last_profile_id[0]).values(age= val))
        session.commit()
        return True
