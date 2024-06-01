from aiogram.utils import formatting

from database.methods import get_my_plans, get_my_plan_details, get_my_race_reports
from lexicon import lexicon_ru


def show_my_plans(user_id) -> dict:
    """Extract users plans from database and represent them in dictionary for keybords buttons"""

    plans = get_my_plans(user_id)
    buttons_name = dict()
    for plan in plans:
        buttons_name.update({str(plan.id): '{} - {}\n{}'.format(plan.plan_date.strftime('%d.%m.%y'),
                                                                lexicon_ru.LEXICON_SELECT_DIST[str(plan.plan_name)],
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

