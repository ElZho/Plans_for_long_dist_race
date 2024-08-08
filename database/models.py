import logging
from datetime import datetime

from sqlalchemy.orm import relationship

from database.base import Base
from sqlalchemy import Column, Integer, DateTime, BigInteger, String, Boolean, ForeignKey, Time, PrimaryKeyConstraint, \
    Float

logger = logging.getLogger(__name__)



class User(Base):
    """ create class User with Column connection_date - date, when user started bot, user_id - telegram id
    Users data - weight, height, age, imt, max pulse, photo"""

    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    connection_date = Column(DateTime, default=datetime.now, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    user_name = Column(String)
    gender = Column(String)
    age = Column(Integer)
    weight = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    imt = Column(Float, nullable=False)
    max_pulse = Column(Integer, nullable=False)
    photo = Column(String)
    race_reports = relationship('RaceReport', backref='race_report', lazy=True, cascade='all, delete-orphan')
    training_plans = relationship('TrainingPlan', backref='training_plan', lazy=True, cascade='all, delete-orphan')
    train_paces = relationship('TrainPaces', backref='train_pace', lazy=True, cascade='all, delete-orphan')
    train_results = relationship('TrainingResult', backref='train_result', lazy=True,
                                 cascade='all, delete-orphan')


class RaceReport(Base):
    """ """

    __tablename__ = 'RaceReport'
    id = Column(Integer, primary_key=True)
    race_date = Column(DateTime, default=datetime.now, nullable=False)
    owner = Column(Integer, ForeignKey('Users.id'), nullable=False)
    distance = Column(String, nullable=False)
    race_time = Column(Time, nullable=False)
    vdot = Column(Integer, nullable=False)
    time5k = Column(Time, nullable=False)

    paces = relationship('TrainPaces', backref='pace', lazy=True, cascade='all, delete-orphan')


class TrainPaces(Base):
    """ """

    __tablename__ = 'TrainPaces'

    id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey('RaceReport.id'), nullable=False)
    owner = Column(Integer, ForeignKey('Users.id'), nullable=False)
    m400 = Column(Time, nullable=False)
    m600 = Column(Time, nullable=False)
    m800 = Column(Time, nullable=False)
    m1000 = Column(Time, nullable=False)
    m1200 = Column(Time, nullable=False)
    m1600 = Column(Time, nullable=False)
    m2000 = Column(Time, nullable=False)
    ST = Column(Time, nullable=False)
    MT = Column(Time, nullable=False)
    LT = Column(Time, nullable=False)
    HMP = Column(Time, nullable=False)
    MP = Column(Time, nullable=False)
    train_plans = relationship('TrainingPlan', backref='train_plan', lazy=True, cascade='all, delete-orphan')


class TrainingPlan(Base):
    """ """

    __tablename__ = 'TrainingPlan'

    id = Column(Integer, primary_key=True)
    plan_date = Column(DateTime, default=datetime.now, nullable=False)
    owner = Column(Integer, ForeignKey('Users.id'), nullable=False)
    pace_id = Column(Integer, ForeignKey('TrainPaces.id'), nullable=False)
    plan = Column(String)
    active = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)
    active_week = Column(Integer)
    # train_results = relationship('TrainingResult', backref='train_result', lazy=True,
    #                              cascade='all, delete-orphan')


class TrainingResult(Base):
    """ """

    __tablename__ = 'TrainingResult'

    id = Column(Integer, primary_key=True)
    result_date = Column(DateTime, default=datetime.now, nullable=False)
    owner = Column(Integer, ForeignKey('Users.id'), nullable=False)
    plan_id = Column(Integer, ForeignKey('TrainingPlan.id'), nullable=False)
    week = Column(Integer, nullable=False)
    train = Column(String, nullable=False)
    distance = Column(String, nullable=False)
    goal_time = Column(Time, nullable=False)
    fact_time = Column(Time, nullable=False) # this is best result of the distance
    fact_difference = Column(Time) # this column will be used when there are same intervals during the train

