import logging
from collections import defaultdict
from datetime import timedelta, datetime, time

from fluentogram import TranslatorRunner

logger = logging.getLogger(__name__)


def calculate_pulse_zones(max_pulse: int) -> list:
    """This func takes max_pulse and calculates pulse_zones"""

    pulse_zone_koef = [(0.5, 0.6), (0.6, 0.75), (0.75, 0.85), (0.85, 0.95), (0.95, 1)]
    pulse_zone = [(round(v[0] * max_pulse), round(v[1] * max_pulse))
                  for v in pulse_zone_koef]

    return pulse_zone


def calculate_imt(weight: float, height: float) -> float:
    """Returns imt, takes weight and height"""
    imt = round(weight * 1000 /
                height ** 2, 2)
    return imt


def calculate_max_pulse(gender: str, age: float) -> tuple[int, str]:
    """calculates max_pulse, takes gender and age. Uses
    Martha Gulati formula for women and  Tanaka's formula"""

    if gender == 'female':
        max_pulse = round(206. - 0.88 * age)
        physiologist = 'Tanaka'
    else:
        max_pulse = round(208. - 0.7 * age)
        physiologist = 'Martha Gulati'
    return max_pulse, physiologist


def find_vdot(vdot_guides: list, dist: str, my_time: datetime) -> tuple:
    """this func is looking in guide nearest time for selected distance and gets VDOT"""

    vdot = '85'
    level = None

    for index, row in enumerate(vdot_guides):
        # looking for fist faster time in selected distance

        ref_time = datetime.strptime(row[dist].split('.')[0], '%H:%M:%S')
        if ref_time <= my_time:
            if index > 0:
                hl = [my_time - ref_time, ref_time - my_time]
                level = index - hl.index(min(hl))
                correct_vdot = 0
            # if first row has time slower than users time, user has to low VDOT level, so VDOT from guid needs to
            # be corrected
            else:
                level = index
                correct_vdot = round(100 / 3 * (my_time - ref_time).total_seconds() / timedelta(seconds=ref_time.second,
                                                                                                minutes=ref_time.minute,
                                                                                                hours=ref_time.hour).total_seconds(),
                                     0)
            break

    vdot = int(vdot_guides[level]['VD0T']) - correct_vdot

    if dist != 'km5' and int(vdot) < 30:
        h, m, s = list(map(float, vdot_guides[level]['km5'].split(':')))
        time5k = timedelta(hours=int(h), minutes=int(m), seconds=int(s),
                           milliseconds=1000 * (s - int(s))).total_seconds() * (1 + 0.03 * correct_vdot)

        time5k = time(time5k // 3600, (time5k // 60) % 60, time5k % 3600 % 60)

    elif dist != 'km5':
        h, m, s = list(map(float, vdot_guides[level]['km5'].split(':')))
        time5k = time(int(h), int(m), int(s))

    else:
        time5k = my_time

    return vdot, vdot_guides[level], time5k


def get_paces(time5k: time|datetime|timedelta, koef: list):
        """This function takes the results on 5K and VO2max level and calculates paces for different training runs
            interval runs, """
        if not isinstance(time5k, timedelta):
            time5k = timedelta(hours=time5k.hour, minutes=time5k.minute, seconds=time5k.second)
        difference = (time5k - timedelta(minutes=16)).total_seconds()
        paces = dict()

        for row in koef:
            target = datetime.strptime(row['base'], '%H:%M:%S') + timedelta(
                seconds=float(row['koef']) * difference / 10)
            target = timedelta(minutes=target.minute, seconds=target.second, microseconds=target.microsecond)
            target = target / float(row['dist'])
            pace = timedelta(seconds=round(target.total_seconds()))
            pace = time(minute=(pace.seconds // 60) % 60, second=pace.seconds - 60 * ((pace.seconds // 60) % 60))
            paces.update({row['name']: pace})

        return paces

# Function to format time in messages
def time_formatting(td: timedelta|time) -> str:
    if isinstance(td, timedelta):

        if td.seconds // 3600 == 0:
            pace = time(minute=(td.seconds // 60) % 60, second=(td.seconds - 60 * ((td.seconds // 60) % 60)))
            res = pace.strftime('%M:%S')

        else:
            pace = time(hour=td.seconds // 3600, minute=(td.seconds // 60) % 60,
                        second=(td.seconds - 3600 * (td.seconds // 3600) - 60 * ((td.seconds // 60) % 60)))
            res = pace.strftime('%H:%M:%S')

    elif isinstance(td, (time, datetime)):

        if td.hour == 0:
            res = td.strftime('%M:%S')

        else:
            res = td.strftime('%H:%M:%S')

    return res


def __convert_to_timedelta(time_to_convert):

    if isinstance(time_to_convert, (datetime, time)):

        convert_time = timedelta(hours=time_to_convert.hour, minutes=time_to_convert.minute,
                                 seconds=time_to_convert.second)

    else:
        convert_time = time_to_convert
    return convert_time


def __count_week_plan(weekly_train: dict, paces: dict, i18n: TranslatorRunner):

    paces = dict((key, __convert_to_timedelta(value)) for key, value in paces.items())
    weekly_plan = []

    t1 = ''.join([i18n.get('first-train', selectvar=1, count=item[0], dist=int(1000 * item[1]),
                     pace = time_formatting(paces['m' + str(int(1000 * item[1]))]),
                     inttime = time_formatting(paces['m' + str(int(1000 * item[1]))] * item[1])
                     ) if item[1] != 'rest' else i18n.get('first-train', selectvar=2,
                     rest=item[0]) for item in weekly_train['train1']])

    weekly_plan.append(t1)

    t2 = ''.join([i18n.get('second-train', selectvar=1, dist=item[0], pace=time_formatting(paces[item[1]]),
    inttime=time_formatting(paces[item[1]] * item[0])) if item[1] not in ['easy', 'min warm-up', 'min cool-down'] else
                  i18n.get('second-train', selectvar=2, dist=item[0], pace=item[1]) for item in weekly_train['train2']])

    weekly_plan.append(t2)

    t3 = ''.join([i18n.get('third-train', selectvar=1, dist=item[0],
                           pace=time_formatting(paces[item[1]]+timedelta(seconds=item[2])),
                inttime=time_formatting(item[0]*(paces[item[1]]+timedelta(seconds=item[2])))) if item[1]
                not in ['easy', 'Race'] else i18n.get('third-train', selectvar=2, dist=item[0],
                pace=item[1]) for item in weekly_train['train3']])

    weekly_plan.append(t3)

    return weekly_plan


def format_plan_details(plan_id, weekly_train: dict, page: int, paces: dict,
                        i18n: TranslatorRunner, case: int=2) -> str:
    """Extract users plan details"""

    weekly_plan = __count_week_plan(weekly_train, paces, i18n)

    comm = i18n.commands_.name(case=case)

    text = i18n.raceplanformatting(dist=plan_id, week=page, firsttrain=weekly_plan[0],
                                   secondtrain=weekly_plan[1], thirdtrain=weekly_plan[2],
                                   additiontext=comm
                                   )
    return  text


def calculate_save(profile, **kwargs) -> dict:
    """Gets as input profile data: age, weight, height, photo. Calculates
    imt and max_pulse and save result in profile"""

    data = dict({'age': profile.age, 'height': profile.height, 'weight': profile.weight,
                 'imt': profile.imt, 'max_pulse': profile.max_pulse, 'photo': profile.photo})
    for k, v in kwargs.items():
        if k == 'age':
            max_pulse, _ = calculate_max_pulse(profile.gender, v)
            data.update(age=v, max_pulse=max_pulse)
        elif k == 'height':
            imt = calculate_imt(profile.weight, v)
            data.update(height=v, imt=imt)
        elif k == 'weight':
            imt = calculate_imt(v, profile.height)
            data.update(weight=v, imt=imt)
        elif k == 'photo_id':
            data.update(photo=v)

    return data


def count_race_plan(dist: int | float, plan_time: timedelta) -> list:
    """func calculates plan for race. return times for each km"""
    pace = plan_time / dist
    plan = [time_formatting(i * pace) for i in range(1, int(dist) + 1)]

    if isinstance(dist, float) and (dist - int(dist)) > 0:
        plan.append(time_formatting(plan_time))

    return "\n🔸 " + "\n🔸 ".join(plan)


def get_trainintervals(train: list, train_number: str, train_tempo: dict) -> dict:
    """makes dict for train. the keys are distances, values are quantity of each interval"""

    interval_dict = defaultdict(int)

    if train_number == 'train1':

        for t in train:
            if t[1] not in ['rest', 'easy', 'min warm-up', 'min cool-down']:
                interval_dict[t[1]] += int(t[0])
        goal_time = dict([(key, key * __convert_to_timedelta(train_tempo['m' + str(int(1000 * key))])) for key in interval_dict.keys()])

    else:
        goal_time = dict()
        for t in train:
            if t[1] not in ['rest', 'easy', 'min warm-up', 'min cool-down']:
                interval_dict[t[0]] += 1

                if train_number == 'train2':

                    goal_time.update({t[0]: t[0] *__convert_to_timedelta(train_tempo[t[1]])})
                else:
                    goal_time.update({t[0]: t[0] * (__convert_to_timedelta(train_tempo[t[1]])+timedelta(seconds=t[2]))})

    return interval_dict, goal_time


def convert_times(times: list[str], goal_time: time) -> list[datetime]:
    """func convert results in timeformat and count difference"""
    # convert str in timedelta
    results = [time_formatting(goal_time),]
    res_times = list(map(lambda x: timedelta(hours=int(x[:2]), minutes=int(x[2:4]), seconds=int(x[4:])), times))
    results.append(time_formatting(sorted(res_times)[0]))

    if len(res_times) > 1:
          delta = abs(res_times[1] - res_times[0])
          results.append(time_formatting(delta))

          results = list(map(lambda x: datetime.strptime(x, '%H:%M:%S')
                                     if len(x) == 8 else  datetime.strptime(x, '%M:%S'), results))
    else:
        results = list(map(lambda x: datetime.strptime(x, '%H:%M:%S')
                              if len(x) == 8 else datetime.strptime(x, '%M:%S'), results))
        results.append(None)

    return results
