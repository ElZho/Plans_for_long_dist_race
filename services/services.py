import logging
from datetime import time, timedelta

from aiogram.utils import formatting

from database.methods import get_my_plans, get_my_plan_details, get_my_race_reports, get_my_profile, change_profile_data
from lexicon import lexicon_ru
from services.calculations import count_target_tempo

logger = logging.getLogger(__name__)


def show_my_plans(user_id) -> dict:
    """Extract users plans from database and represent them in dictionary for keybords buttons"""

    plans = get_my_plans(user_id)
    buttons_name = dict()
    for plan in plans:
        buttons_name.update({str(plan.id): '{}\n\n-{}\n\n{}'.format(lexicon_ru.LEXICON_SELECT_DIST[
                                                                        str(plan.plan_name)],
                                                                    lexicon_ru.PLAN_CONDITIONS[
                                                                        (plan.active, plan.completed)],
                                                                    plan.plan_date.strftime('%d.%m.%y')
                                                                    )})
    return buttons_name


def get_plan_id(user_id) -> list:
    """Extract users plans ids for filters"""

    plans = get_my_plans(user_id)
    plan_id = []
    for plan in plans:
        plan_id.append(plan.id)

    return plan_id


def get_plan_details(user_id, plan_id) -> dict[int: list[str, str, str]]:
    """Extract users plan details"""
    details = get_my_plan_details(user_id, plan_id)

    training = dict()
    for detail in details:
        training.update({detail.week: [detail.first_train, detail.second_train, detail.third_train]})

    return training


def format_plan_details(weekly_train: list, plan_id: int, page, bot_commands: list) -> formatting.Text:
    """Extract users plan details"""
    bot_command = [formatting.BotCommand(bc) for bc in bot_commands]
    page_text = lexicon_ru.LEXICON_RU['process_calculate_plan_command'][0].format(page)
    training = [formatting.as_key_value(formatting.as_line(
        lexicon_ru.LEXICON_RU[
            'process_calculate_plan_command'][
            1].format(i + 1),
        end='\n------------------------------\n'),
        weekly_train[i], ) for i in range(3)]
    content = formatting.as_list(
        formatting.Underline(
            formatting.as_line(lexicon_ru.LEXICON_RU['process_calculate_plan_command'][2],
                               lexicon_ru.LEXICON_SELECT_DIST[str(plan_id)])),
        formatting.as_marked_section(
            formatting.Bold(page_text),
            *training,
            marker="\n🔸 ",
        ), *bot_command
        # formatting.BotCommand(bot_command)
    )
    return content


def collect_my_race_report(user_id):
    reports = get_my_race_reports(user_id)
    if reports:
        my_races = dict()
        for report in reports:
            my_races.update({str(report.id): [report.report_date.strftime('%d/%m/%y'), report.distance,
                                              report.race_time, report.vdot]})
        return my_races
    else:
        return None


def calculate_pulse_zones(max_pulse: int) -> list:
    """This func takes max_pulse and calculates pulse_zones"""
    pulse_zone = [formatting.as_line(k, round(v[0] * max_pulse), '-',
                                     round(v[1] * max_pulse), sep=' ')
                  for k, v in lexicon_ru.SHOW_DATA['pulse_zone'].items()]
    return pulse_zone


def calculate_imt(weight: float, height: float) -> float:
    """Returns imt, takes weight and height"""
    imt = round(weight * 1000 /
                height ** 2, 2)
    return imt


def calculate_max_pulse(gender: str, age: float) -> int:
    """calculates max_pulse, takes gender and age. Uses
    Martha Gulati formula for women and  Tanaka's formula"""

    if gender == 'Женский':
        max_pulse = round(206. - 0.88 * age)
    else:
        max_pulse = round(208. - 0.7 * age)
    return max_pulse


def calculate_save(user_id: int, **kwargs) -> bool:
    """Gets as input profile data: age, weight, height, photo. Calculates
    imt and max_pulse and save result in profile"""
    _, profile, gender = get_my_profile(user_id)

    data = dict({'age': profile.age, 'height': profile.height, 'weight': profile.weight,
                 'imt': profile.imt, 'max_pulse': profile.max_pulse, 'photo': profile.photo})
    for k, v in kwargs.items():
        if k == 'age':
            max_pulse = calculate_max_pulse(gender, v)
            data.update(age=v, max_pulse=max_pulse)
        elif k == 'height':
            imt = calculate_imt(profile.weight, v)
            data.update(height=v, imt=imt)
        elif k == 'weight':
            imt = calculate_imt(v, profile.height)
            data.update(weight=v, imt=imt)
        elif k == 'photo_id':
            data.update(photo=v)
    res = change_profile_data(user_id, **data)
    return res


def time_formatting(td: timedelta) -> str:

    if td.seconds // 3600 == 0:
        pace = time(minute=(td.seconds // 60) % 60, second=(td.seconds - 60 * ((td.seconds // 60) % 60)))
        res = pace.strftime('%M:%S')
    else:
        pace = time(hour=td.seconds // 3600, minute=(td.seconds // 60) % 60,
                    second=(td.seconds - 3600 * (td.seconds // 3600) - 60 * ((td.seconds // 60) % 60)))
        res = pace.strftime('%H:%M:%S')
    return res


def count_race_plan(dist: int | float, plan_time: timedelta) -> list:
    pace = plan_time / dist
    plan = [time_formatting(i * pace) for i in range(1, int(dist) + 1)]
    if isinstance(dist, float) and (dist - int(dist)) > 0:
        plan.append(plan_time)
    return plan


def calculate_vdot(result_5k, vdot, results):
    logger.error('Лог ERROR')
    count_paces = (count_target_tempo(result_5k, vdot))
    # await state.update_data(count_tempo=user_dict['count_tempo'],
    #                         vdot=user_dict['vdot'])
    # оформляем достижимые результаты
    target_results = [formatting.as_line(k, formatting.Italic(v), sep=' ')
                      for k, v in results.items() if k != 'VD0T']
    # оформляем темпы для тренировок
    paces = [formatting.as_line(k, v, sep=' ') for k, v in count_paces.items()] #datetime.strptime(v, '%H:%M:%S')
    # оформляем сообщение
    content = formatting.as_list(
        formatting.as_line(lexicon_ru.LEXICON_RU['process_calculate_vdot_command'][0],
                           vdot),
        formatting.as_marked_section(
            formatting.Bold(lexicon_ru.LEXICON_RU['process_calculate_vdot_command'][1]),
            *target_results,
            marker="🔸 ", ),
        formatting.as_marked_section(
            formatting.Bold(lexicon_ru.LEXICON_RU['process_calculate_vdot_command'][2]),
            *paces,
            marker="🔸 ", ),
    )
    return count_paces, content


def create_err():
    a = 5/0

