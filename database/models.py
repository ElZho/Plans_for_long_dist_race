import logging
from datetime import datetime


from sqlalchemy import Column, Integer, ForeignKey, DateTime, BigInteger, String, Float, Time, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


logger = logging.getLogger(__name__)
Base = declarative_base()


class User(Base):
    """ create class User with Column connection_date - date, when user started bot, user_id - telegram id
    User has connection to profile"""

    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    connection_date = Column(DateTime, default=datetime.now, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    user_name = Column(String)
    gender = Column(String)

    profiles = relationship('Profile', backref='profile', lazy=True, cascade='all, delete-orphan')
    race_reports = relationship('RaceReport', backref='race_report', lazy=True, cascade='all, delete-orphan')
    training_plans = relationship('TrainingPlan', backref='training_plan', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return self.user_id


class Profile(Base):
    """Users data - weight, height, age, imt, max pulse, photo"""

    __tablename__ = 'Profile'
    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey('Users.id'), nullable=False)
    profile_date = Column(DateTime, default=datetime.now, nullable=False)
    photo = Column(String)
    weight = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    age = Column(Float, nullable=False)
    imt = Column(Float, nullable=False)
    max_pulse = Column(Integer, nullable=False)

    def __repr__(self):
        return self.profile_date


class RaceReport(Base):
    """Data of users race results - distance, race_time, vdot"""

    __tablename__ = 'RaceReport'
    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey('Users.id'), nullable=False)
    report_date = Column(DateTime, default=datetime.now, nullable=False)
    distance = Column(String, nullable=False)
    race_time = Column(Time, nullable=False)
    vdot = Column(Integer, nullable=False)

    def __repr__(self):
        return self.result_date


class TrainingPlan(Base):
    """Data of users race results - plan_name, plan_data, active, completed"""

    __tablename__ = 'TrainingPlan'
    id = Column(BigInteger, primary_key=True)
    owner = Column(Integer, ForeignKey('Users.id'), nullable=False)
    plan_name = Column(String)
    plan_date = Column(DateTime, default=datetime.now, nullable=False)
    active = Column(Boolean, default=False, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    plan_details = relationship('PlanDetails', backref='plan_detail', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return self.plan_id


class PlanDetails(Base):
    """Data of users race results - week, first_train, second_train, third_train, completed"""

    __tablename__ = 'PlanDetails'
    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey('Users.id'), nullable=False)
    plan_id = Column(BigInteger, ForeignKey('TrainingPlan.id'), nullable=False)
    week = Column(Integer, nullable=False)
    first_train = Column(String, nullable=False)
    second_train = Column(String, nullable=False)
    third_train = Column(String, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return self.plan_id
