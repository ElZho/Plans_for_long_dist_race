"""Database function. Inserts, deletes, selects records in and from db"""
import logging
from datetime import time
from typing import Tuple, Sequence, Any

from sqlalchemy import select, Row, ScalarResult, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query
# from sqlalchemy.orm.sync import update

from database.models import User, RaceReport, TrainPaces, TrainingPlan, TrainingResult


class Database:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def add_user(self, tg_id: int, user_name: str, age: int, gender: str, weight: float, height: float, imt:float,
                       max_pulse: int, photo_id: str) -> None:

        user = await self.session.execute(select(User).where(User.user_id == tg_id))
        if not user.one_or_none():
            user = User(
                user_id=tg_id, user_name=user_name, age=age, gender=gender, weight=weight, height=height, imt=imt,
                max_pulse=max_pulse, photo=photo_id)
            self.session.add(user)
        await self.session.commit()


    async def get_users_data(self, tg_id: int) -> User:

        user = await self.session.execute(select(User).where(User.user_id == tg_id))

        return user.scalar_one_or_none()


    # async def get_users(self):
    #     users_info = await self.session.execute(select(User.user_name, User.age, User.gender))
    #     return users_info


    async def create_race_report(self, tg_id: int, distance: str, race_time: time, time5k: time,
                                 vdot: int):
        """Add new race report for user"""

        user_id = await self.session.execute(select(User.id).where(User.user_id == tg_id))
        new_report = RaceReport(distance=distance, race_time=race_time, owner=user_id.scalar(), time5k=time5k, vdot=vdot)
        self.session.add(new_report)
        await self.session.commit()
        return new_report.id


    async def add_paces_data(self, tg_id: int, race_id: int, **kwargs) -> TrainPaces:
        user = await self.session.execute(select(User).where(User.user_id == tg_id))
        user_id = user.scalar().id
        pace_id = await self.session.execute(select(TrainPaces.id).where(TrainPaces.owner==user_id,
                                                                   TrainPaces.race_id==race_id))
        pace_id = pace_id.scalar_one_or_none()
        if pace_id:
            return pace_id
        else:
            new_paces = TrainPaces(owner=user_id, race_id=race_id, **kwargs)

            self.session.add(new_paces)
            await self.session.commit()
            return new_paces.id


    async def get_my_race_reports(self, tg_id: int) -> Sequence[Row[Any]]|int:
        """func to get all users race reports
        0 - user not exist
        1 - there is no one plan
        """

        user = await self.session.execute(select(User).where(User.user_id == tg_id))

        # reports = await self.session.execute(select(RaceReport.id, RaceReport.race_date, RaceReport.race_time,
        #                                             RaceReport.time5k, RaceReport.distance,
        #                                             RaceReport.vdot).where(RaceReport.owner==
        #                                             user.scalar().id).order_by(RaceReport.race_date.desc()))
        reports = await self.session.execute(select(RaceReport).where(RaceReport.owner==user.scalar().id).order_by(
                                                    RaceReport.race_date.desc()))
        reports = reports.scalars()

        if not reports:
            return 1
        return reports


    async def get_race_from_id(self, tg_id: int, race_id: id):
        """func to get users race reports having race id
                returns False if wrong user or wrong race id
                """

        user = await self.session.execute(select(User).where(User.user_id == tg_id))

        report = await self.session.execute(select(RaceReport.id, RaceReport.race_date, RaceReport.race_time,
                                                    RaceReport.time5k, RaceReport.distance,
                                                    RaceReport.vdot).where(RaceReport.owner==
                                                     user.scalar().id, RaceReport.id==race_id))

        if report is None:
            return False
        return report.first()


    async def add_plan_data(self, tg_id: int, pace_id: int, plan_name: str, active_week: int) -> tuple:
        """func to save users run plan. If there is the same plan, then result is False, else True."""

        user = await self.session.execute(select(User).where(User.user_id == tg_id))
        user_id = user.scalar().id

        plan = await self.session.execute(select(TrainingPlan).where(TrainingPlan.owner==user_id,
                                                                   TrainingPlan.pace_id==pace_id,
                                                                   TrainingPlan.plan==plan_name,
                                                                   TrainingPlan.completed==False))
        plan = plan.scalar_one_or_none()
        if plan:
            return False, plan.id, plan.plan_date, plan.active
        else:

            new_plan = TrainingPlan(owner=user_id, pace_id=pace_id, plan=plan_name, active_week=active_week)

            self.session.add(new_plan)
            await self.session.commit()
        return True, new_plan.id


    async def get_paces_data(self, tg_id: int, race_id: int|None = None, pace_id: int|None = None, **kwargs) -> \
    ScalarResult[TrainPaces] | bool:
        """return False if there is no same pace and pace data if there is"""
        user = await self.session.execute(select(User).where(User.user_id == tg_id))
        pace = None
        if pace_id:
            pace = await self.session.execute(select(TrainPaces).where(TrainPaces.owner == user.scalar().id,
                                                                       TrainPaces.id == pace_id))
            pace = pace.scalar_one_or_none()
        elif race_id:
            pace = await self.session.execute(select(TrainPaces).where(TrainPaces.owner==user.scalar().id,
                                                                   TrainPaces.race_id==race_id))
            pace = pace.scalar_one_or_none()

        if pace:
            return pace
        else:
            return False


    async def get_my_plans(self, tg_id: int) -> ScalarResult[Any]|bool:
        """func to get all users race reports
        0 - user not exist
        1 - there is no one plan
        """

        user = await self.session.execute(select(User).where(User.user_id == tg_id))

        plans = await self.session.execute(select(TrainingPlan).where(TrainingPlan.owner==
                                                    user.scalar().id).order_by(TrainingPlan.plan_date.desc()))
        plans = plans.scalars()
        if plans:
            return plans
        return False


    async def get_my_plans_ids(self, tg_id: int) -> ScalarResult[Any]|bool:
        """func to get all users race reports
        0 - user not exist
        1 - there is no one plan
        """

        user = await self.session.execute(select(User).where(User.user_id == tg_id))

        plans = await self.session.execute(select(TrainingPlan.id).where(TrainingPlan.owner==
                                                    user.scalar().id).order_by(TrainingPlan.plan_date.desc()))
        plans = plans.scalars()
        if plans is None:
            return False
        return plans


    async def get_plan(self, tg_id: int, plan_id) -> Sequence[Row[Any]]|int:
        """func to get all users race reports
        0 - user not exist
        1 - there is no one plan
        """

        user = await self.session.execute(select(User).where(User.user_id == tg_id))

        plan = await self.session.execute(select(TrainingPlan).where(TrainingPlan.owner==
                                                    user.scalar().id, TrainingPlan.id==plan_id))
        plan = plan.scalar_one_or_none()
        if plan:
            return plan
        return False


    async def make_plan_active(self, tg_id: int, plan_id) -> TrainingPlan | bool:
        """Func makes plan active and returns True if success, or False if there is already active plan
        User can have only one activa plan"""
        user = await self.session.execute(select(User).where(User.user_id == tg_id))
        user = user.scalar()

        plans = await self.session.execute(select(TrainingPlan).where(TrainingPlan.owner == user.id,
                                    TrainingPlan.completed == False,
                                    TrainingPlan.active == True))
        plans = plans.scalar_one_or_none()

        if plans:
            return plans
        else:
            plan = await self.session.get(TrainingPlan, plan_id)
            plan.active = True
            await self.session.commit()
            return True


    async def delete_plan(self, tg_id: int, plan_id) -> bool:
        """func delets plan when id is given"""

        user = await self.session.execute(select(User).where(User.user_id == tg_id))

        plan = await self.session.get(TrainingPlan, plan_id)
        # plan = plan.scalar()

        if plan:
            if plan.owner == user.scalar().id:
                print('План', plan.owner)
                await self.session.delete(plan)
                await self.session.commit()

                return True

        return False


    async def get_active_plan(self, tg_id: int) -> TrainingPlan | bool:
        """func to get active users plan
        if plan returns plan, else returns False
        """

        user = await self.session.execute(select(User).where(User.user_id == tg_id))

        plan = await self.session.execute(select(TrainingPlan).where(TrainingPlan.owner ==
                                                                     user.scalar().id, TrainingPlan.active == True))
        plan = plan.scalar_one_or_none()

        if plan:
            return plan

        return False


    async def make_week_completed(self, plan_id, week) -> bool:
        """Makes week completed. If it is the last week of the plan makes plan completed
        Returns True if success, False if plan is completed"""

        plan = await self.session.get(TrainingPlan, plan_id)
        if week == 1:
            plan.completed = True
            plan.active = False
            result = 0

        else:
            plan.active_week = week - 1
            result = 1

        await self.session.commit()
        return result


    async def change_profile_data(self, tg_id, **data):
        """Changes users profile some data or all (age, weight, height and photo)"""
        # user = await self.session.execute(select(User).where(User.user_id == tg_id))
        await self.session.execute(update(User).where(User.user_id == tg_id).values(data))
        # user.update(data)
        await self.session.commit()


    async  def get_users_profile(self):

        users_info = await self.session.execute(select(User.user_name, User.gender, User.age,
                                            func.count(TrainingPlan.id).label("tp_quant")
                                            ).join_from(User, TrainingPlan, isouter=True).group_by(User.id,
                                                                                         User.user_name,
                                                                                         User.gender,
                                                                                         User.age))
        return users_info.all()


    async  def get_last_race(self, tg_id):

        user = await self.session.execute(select(User).where(User.user_id==tg_id))
        user = user.scalar()
        races = await self.session.execute(select(RaceReport).where(RaceReport.owner==user.id).order_by(RaceReport.race_date.desc()).limit(1))
        res = races.one_or_none()
        if res:
            return res
        return 1


    async def get_my_race_id(self, tg_id: int) -> ScalarResult[Any]|int:
        """func gets all users race reports
        0 - user not exist
        1 - there is no one plan
        """

        user = await self.session.execute(select(User).where(User.user_id == tg_id))

        reports = await self.session.execute(select(RaceReport.id).where(RaceReport.owner==user.scalar().id).order_by(
                                                    RaceReport.race_date.desc()))
        reports = reports.scalars()

        if not reports:
            return 1
        return reports


    async def get_list_oftrains(self, plan_id: int, week: int):
        """func look for the trains, which don't have train results"""

        trains = await self.session.execute(select(TrainingResult).where(TrainingResult.plan_id==plan_id,
                                                                          TrainingResult.week==week))
        return trains.scalars()


    async def add_train_results(self, tg_id: int, plan_id: int, week: int, train, results):
        """func to save train results"""
        # get users profile
        user = await self.session.execute(select(User).where(User.user_id == tg_id))

        print('Результаты', results)
        # add results
        for key, value in results.items():

            train_result = TrainingResult(owner=user.scalar().id,
                                      plan_id=plan_id,
                                      week=week,
                                      train=train,
                                      distance=key,
                                      goal_time=value[0],
                                      fact_time=value[1],
                                      fact_difference=value[2])

            self.session.add(train_result)

        await self.session.commit()