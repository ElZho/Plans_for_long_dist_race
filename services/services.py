from aiogram.utils import formatting

from database.methods import get_my_plans, get_my_plan_details, get_my_race_reports, get_my_profile, change_profile_data
from lexicon import lexicon_ru


def show_my_plans(user_id) -> dict:
    """Extract users plans from database and represent them in dictionary for keybords buttons"""

    plans = get_my_plans(user_id)
    buttons_name = dict()
    for plan in plans:
        buttons_name.update({str(plan.id): '{}\n\n - {}\n\n{}'.format(plan.plan_date.strftime('%d.%m.%y'),
                                                                      lexicon_ru.LEXICON_SELECT_DIST[
                                                                          str(plan.plan_name)],
                                                                      lexicon_ru.PLAN_CONDITIONS[
                                                                          (plan.active, plan.completed)])
                             })
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
    training = [formatting.as_key_value(formatting.as_line(i + 1,
                                                           lexicon_ru.LEXICON_RU[
                                                               'process_calculate_plan_command'][
                                                               1],
                                                           end='\n------------------------------\n'),
                                        weekly_train[i], ) for i in range(3)]
    content = formatting.as_list(
        formatting.Underline(
            formatting.as_line(lexicon_ru.LEXICON_RU['process_calculate_plan_command'][2],
                               lexicon_ru.LEXICON_SELECT_DIST[str(plan_id)])),
        formatting.as_marked_section(
            formatting.Bold(page_text),
            *training,
            marker="🔸 ",
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
            data.update(photo = v)
    res = change_profile_data(user_id, **data)
    return res
