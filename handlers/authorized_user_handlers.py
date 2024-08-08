import logging
import os
import random
from datetime import timedelta, datetime, time
from re import findall

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import (CallbackQuery, Message, FSInputFile, PhotoSize, ErrorEvent)

from fluentogram import TranslatorRunner

from database import Database

from filters.filtres import CheckTime, IsAuthorized, CheckPlans, CheckRaces, CheckProfileData, CheckDist, CheckResults, \
    CheckTrainDist, CheckRaceDist, CheckIntervals, CheckTrainTimes
from keyboards.keyboards import create_pagination_keyboard, create_inline_kb

from services.services import find_vdot, time_formatting, get_paces, format_plan_details, calculate_save, \
    count_race_plan, get_trainintervals, convert_times

from states.states import FSMFillForm


logger = logging.getLogger(__name__)
router = Router()
router.message.filter(IsAuthorized())


@router.message(Command(commands='help'))
async def process_help_command(message: Message, i18n: TranslatorRunner):
    """This handler shows help data for authorized user"""
    await message.answer(
        text=i18n.get('help_-auth-user')
    )



@router.message(Command(commands='add_new_race_result'), StateFilter(default_state))
async def process_add_new_result(message: Message, state: FSMContext, i18n: TranslatorRunner, vdot_guides: list):
    """this handler works on command add_new_race_result and allows user to choose distance
       to add new race results"""

    # makes buttons to each dist
    reply_buttons = dict([(key, i18n.get('distancebuttonskeys', racedist=key)) for key in vdot_guides[0].keys()
                          if key != "VD0T"])

    # Sand user message with buttons
    await message.answer(
        text=i18n.choose_.dist(),
        # Dist_markup
        reply_markup=create_inline_kb(3,
                                      reply_buttons)
    )
    await state.set_state(FSMFillForm.add_new_result)


@router.message(StateFilter(FSMFillForm.add_new_result), ~CheckRaceDist()) #F.data.in_(distance_buttons_keys)
async def warning_not_distances(message: Message, i18n: TranslatorRunner):
    """this handler works when there is wrong distance is done"""
    await message.answer(
        text=i18n.wrong.dist(val=message.text)
    )


@router.callback_query(StateFilter(FSMFillForm.add_new_result), CheckRaceDist()) #F.data.in_(distance_buttons_keys)
async def select_distances(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    """this handler works to ask user enter race time"""

    # Save distance (callback.data) in storage key "res_distances",
    await state.update_data(res_distances=callback.data)

    # Sand message with data
    await callback.message.delete()
    await callback.message.answer(
        text=i18n.get('select_-distances', dist=callback.data)
    )
    # set status add_new_result_time
    await state.set_state(FSMFillForm.add_new_result_time)


@router.message(StateFilter(FSMFillForm.add_new_result_time), CheckTime())
async def process_res_time_sent(message: Message, state: FSMContext, vdot_guides: list, i18n: TranslatorRunner,
                                db: Database):
    """this handler works when race time is given"""
    # Превращаем часы, минуты, секунды в время"
    h, m, s = findall(r'(\d{2})', message.text)
    my_time = datetime.strptime(':'.join([h, m, s]), '%H:%M:%S')
    # Cохраняем часы в хранилище по ключу "result"
    await state.update_data(race_time=my_time)
    data = await state.get_data()
    # считаем VO2Max
    vdot, achivable_results, time5k = find_vdot(vdot_guides, data["res_distances"], my_time)

    await db.create_race_report(message.from_user.id, data['res_distances'], my_time.time(), time5k, vdot)

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text=i18n.get("restime-sent", vdot=vdot, tenk=achivable_results["km10"],
                      hmp=achivable_results["hmph"], mp=achivable_results["mph"])
    )
    await state.clear()


@router.message(StateFilter(FSMFillForm.add_new_result_time))
async def warning_wrong_time(message: Message, i18n: TranslatorRunner):
    """This handler works if user enter wrong time """
    await message.answer(
        text=i18n.get("wrong-time_", res=message.text)
    )


@router.message(Command(commands='calculate'), StateFilter(default_state))
async def process_select_race(message: Message, state: FSMContext, i18n: TranslatorRunner, db: Database):
    """handler to begin plan calculation. Ask user to select target distance."""

    race_rep = await db.get_last_race(message.from_user.id)

    if not race_rep:
        await message.answer(i18n.ups())
    elif race_rep == 1:
        await message.answer(i18n.yetnonhave.reports())
    else:
        await state.update_data(race_id=race_rep[0].id, race_time=race_rep[0].race_time, race_dist=race_rep[0].distance,
                                time5k=race_rep[0].time5k,
                                vdot=race_rep[0].vdot, case=1)

        await message.answer(i18n.confirmresult(countresults=len(race_rep),
                                            dist=i18n.get("distancebuttonskeys", racedist=race_rep[0].distance), # distance_buttons_keys[race_rep[0].distance]
                                            result=time_formatting(race_rep[0].race_time)),
                                            reply_markup=create_inline_kb(2, dict({str(race_rep[0].id): "Да!",
                                                                                    'select_other': "Нет.Выберу другой"})))

    await state.set_state(FSMFillForm.select_result)


@router.callback_query(StateFilter(FSMFillForm.select_result), CheckResults())
async def process_calculate_paces(callback: CallbackQuery, state: FSMContext, koef: list,
                                  i18n: TranslatorRunner, db: Database, plans: dict):
    """this handler works when user selects last race result"""
    # get data of last race
    race = await db.get_race_from_id(callback.from_user.id, int(callback.data))

    if int(race.vdot) < 65:
        # calculate paces
        count_tempo = get_paces(race.time5k, koef)

        # save paces in database
        paces_id = await db.add_paces_data(callback.from_user.id, race.id, **count_tempo)
        await state.update_data(count_tempo=count_tempo, paces_id=paces_id, vdot=race.vdot, time5k=race.time5k)

        # create pace dict in time format
        past_in_text_var = dict(map(lambda x: (x[0], time_formatting(x[1])), count_tempo.items()))

        train_dist_dict = dict()
        for k in plans:
            train_dist_dict.update({k: i18n.get('distances', dist=k)})

        await callback.message.answer(text=i18n.paces.count(selectvar=1, **past_in_text_var),
                                      reply_markup=create_inline_kb(2, train_dist_dict))  # select_train_dist

        await state.set_state(FSMFillForm.select_dist)
    else:
        await callback.message.answer(text=i18n.paces.count(selectvar=0, vdot=race.vdot))
        await state.clear()


@router.callback_query(StateFilter(FSMFillForm.select_result), F.data.in_(['select_other', ]))
async def process_calculate_paces(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner, db: Database):
    """This handler works when user want select other race result"""
    # get all races data
    all_races = await db.get_my_race_reports(callback.from_user.id)

    list_of_races = dict()

    for race in all_races:

        text = i18n.raceview(racedate=race.race_date, dist=i18n.get("distancebuttonskeys", racedist=race.distance),
                             racetime=time_formatting(race.race_time))  #distance_buttons_keys[race.distance]

        list_of_races[str(race.id)] = text

    await callback.message.answer(text=i18n.selectother(), reply_markup=create_inline_kb(1, list_of_races))
    await state.set_state(FSMFillForm.result_analysis)


@router.callback_query(StateFilter(FSMFillForm.result_analysis), CheckRaces())
async def result_analysis(callback: CallbackQuery, i18n: TranslatorRunner, db: Database, koef: list, plans: dict,
                          state: FSMContext):
    """This handler works when user choosed race"""
    race = await db.get_race_from_id(callback.from_user.id, int(callback.data))

    if int(race.vdot) < 65:
        # calculate paces
        count_tempo = get_paces(race.time5k, koef)

        # save paces in database
        paces_id = await db.add_paces_data(callback.from_user.id, race.id, **count_tempo)
        await state.update_data(count_tempo=count_tempo, paces_id=paces_id, vdot=race.vdot, time5k=race.time5k)

        # create pace dict in time format
        past_in_text_var = dict(map(lambda x: (x[0], time_formatting(x[1])), count_tempo.items()))

        train_dist_dict = dict()
        for k in plans:
            train_dist_dict.update({k: i18n.get('distances', dist=k)})

        await callback.message.answer(text=i18n.paces.count(selectvar=1, **past_in_text_var),
                             reply_markup=create_inline_kb(2, train_dist_dict)) #select_train_dist

        await state.set_state(FSMFillForm.select_dist)
    else:
        await callback.message.answer(text=i18n.paces.count(selectvar=0, vdot=race.vdot))
        await state.clear()


@router.callback_query(StateFilter(FSMFillForm.select_dist), CheckTrainDist()) # select_train_dist.keys()
@router.callback_query(StateFilter(FSMFillForm.view_saved_plan), CheckPlans())
async def calculate_train_plan(callback: CallbackQuery, i18n: TranslatorRunner, plans: dict,
                          state: FSMContext, db: Database):
    """This Handler calculates and shows first page of plan"""

    data = await state.get_data()
    if data['case'] == 1:
        dist = callback.data
        plan = plans[dist]
        week = len(plan)
    elif data['case'] == 2:
        plan_details = await db.get_plan(callback.from_user.id, int(callback.data))
        dist = plan_details.plan
        plan = plans[dist]
        week = len(plan)
        count_tempo = await db.get_paces_data(callback.from_user.id, pace_id=plan_details.pace_id)
        data['count_tempo'] = dict(count_tempo.__dict__)


        await state.update_data(count_tempo=data['count_tempo'], plan_id=int(callback.data))

    content = format_plan_details(i18n.get("distances", dist=dist), plan[str(week)], week, data['count_tempo'],
                                  i18n, data['case']) #select_train_dist[dist]

    await callback.message.edit_reply_markup(reply_markup=None)
    await state.update_data(week=week, dist=dist, page_quantity=len(plan))
    await callback.message.answer(content, reply_markup=create_pagination_keyboard(
            'backward',
            f'{str(week)}/{str(len(plan))}',
            'forward'))
    if data['case'] == 1:
        await state.set_state(FSMFillForm.wait_save_file)


@router.callback_query(StateFilter(FSMFillForm.wait_save_file), F.data == 'forward')
@router.callback_query(StateFilter(FSMFillForm.view_saved_plan), F.data == 'forward')
async def process_forward_press(callback: CallbackQuery, i18n: TranslatorRunner, plans: list, state: FSMContext):
    """This handler calculates and shows next page of plan"""

    # получаем данные из хранилища
    data = await state.get_data()

    dist = data['dist']
    plan = plans[dist]
    week = data['week']-1

    if week > 0:
        content = format_plan_details(i18n.get("distances", dist=dist), plan[str(week)], week, data['count_tempo'],
                                      i18n, data['case']) #select_train_dist[dist]
        await callback.message.edit_reply_markup(reply_markup=None)
        await state.update_data(week=week)
        await callback.message.edit_text(content, reply_markup=create_pagination_keyboard(
            'backward',
            f'{str(week)}/{str(len(plan))}',
            'forward'))


@router.callback_query(StateFilter(FSMFillForm.wait_save_file), F.data == 'backward')
@router.callback_query(StateFilter(FSMFillForm.view_saved_plan), F.data == 'backward')
async def process_forward_press(callback: CallbackQuery, i18n: TranslatorRunner, plans: list, state: FSMContext):
    """This handler calculates and shows previous page of plan"""

    # получаем данные из хранилища
    data = await state.get_data()

    dist = data['dist']
    plan = plans[dist]
    week = data['week']+1

    if week <= data['page_quantity']:
        content = format_plan_details(i18n.get("distances", dist=dist), plan[str(week)], week, data['count_tempo'],
                                      i18n, data['case']) #,select_train_dist[dist]
        await callback.message.edit_reply_markup(reply_markup=None)
        await state.update_data(week=week)
        await callback.message.edit_text(content, reply_markup=create_pagination_keyboard(
            'backward',
            f'{str(week)}/{str(len(plan))}',
            'forward'))


@router.message(Command(commands='save_plan'), StateFilter(FSMFillForm.wait_save_file))
async def process_save_plan(message: Message, state: FSMContext, db: Database, i18n: TranslatorRunner):
    """This handler works when save_plan commands is entered and saves plan in db"""
    # получаем данные
    user_dict = await state.get_data()

    # сохраняем в бд
    result = await db.add_plan_data(message.from_user.id, user_dict['paces_id'],user_dict['dist'],
                                    user_dict['page_quantity'])

    if result[0]:
        await message.answer(i18n.saveplan.result(case=1))
    else:
        await message.answer(i18n.saveplan.result(case=2, plandate=result[2]))

    await state.clear()


@router.message(Command(commands='get_my_plans'), StateFilter(default_state))
async def process_get_my_plans(message: Message, state: FSMContext, db: Database, i18n: TranslatorRunner):

    # get plans from db and pass them to buttons
    plans = await db.get_my_plans(message.from_user.id)

    if plans:
        buttons_name = dict()
        for plan in plans:

            if plan.active == True:
                butt = i18n.planbottons(case='active', plandate=plan.plan_date, dist=plan.plan)
                buttons_name.update({str(plan.id): butt})
            elif plan.completed == True:
                butt = i18n.planbottons(case='compleeted', plandate=plan.plan_date, dist=plan.plan)
                buttons_name.update({str(plan.id): butt})
            else:
                butt = i18n.planbottons(case=0, plandate=plan.plan_date, dist=plan.plan)
                buttons_name.update({str(plan.id): butt})

        await message.answer(
            text=i18n.getsavedplans(case=1), reply_markup=create_inline_kb(1, buttons_name)
        )
        await state.set_state(FSMFillForm.view_saved_plan)
        await state.update_data(case=2)
    else:
        await message.answer(
            text=i18n.getsavedplans(case=0)
        )


@router.message(Command(commands='make_plan_active'), FSMFillForm.view_saved_plan)
async def process_make_plan_active(message: Message, state: FSMContext, db: Database, i18n: TranslatorRunner):
    data = await state.get_data()
    result = await db.make_plan_active(message.from_user.id, int(data['plan_id']))

    if result == True:
        await message.answer(text=i18n.makeplanactive(case=1))

    else:

        await message.answer(text=i18n.makeplanactive(case=2, dist=i18n.get("distances", dist=result.plan),
                                                      dataplan=result.plan_date)) #,select_train_dist[result.plan]

    await state.clear()


@router.message(Command(commands='delete_plan'), FSMFillForm.view_saved_plan)
async def process_delete_plan(message: Message, state: FSMContext, db: Database, i18n: TranslatorRunner):
    data = await state.get_data()
    result = await db.delete_plan(message.from_user.id, int(data['plan_id']))

    if result:
        plan = i18n.get("distances", dist=data['dist']) # select_train_dist[data['dist']]
        await message.answer(text=i18n.deleteplan(case=1, plan=plan))

    else:
        await message.answer(text=i18n.deleteplan(case=0))

    await state.clear()


# @router.message(Command(commands='get_plan_in_file'), StateFilter(default_state))
# async def process_sent_file(message: Message, state: FSMContext):
#     data = await state.get_data()
#
#
#
# @router.callback_query(StateFilter(FSMFillForm.get_saved_plan_in_file), CheckPlans())
# async def process_get_saved_plan_in_file(callback: CallbackQuery, state: FSMContext):
#     # get training and format it
#     data = get_plan_details(callback.from_user.id, callback.data)
#     plan_name = get_plan_name(callback.data)
#
#     # упаковываем в файл txt
#     filename = sent_plan(LEXICON_SELECT_DIST[str(plan_name)],
#                          lexicon_ru.LEXICON_RU['Info_text'], data, callback.message.chat.id)
#     # отправляем
#     doc = FSInputFile(filename)
#     await callback.message.reply_document(doc)
#     # удаляем файл
#     os.remove(filename)
#     await state.clear()
#

@router.message(Command(commands='get_next_week_plan'))
async def process_get_next_week_plan(message: Message, state: FSMContext, db: Database, i18n: TranslatorRunner,
                                     plans: list):
    result = await db.get_active_plan(message.from_user.id)

    if result:
        await state.update_data(plan_id=result.id, dist=result.plan, week=result.active_week)

        dist = result.plan
        plan = plans[dist]
        week = result.active_week

        count_tempo = await db.get_paces_data(message.from_user.id, pace_id=result.pace_id)
        count_tempo_dict = dict(count_tempo.__dict__)

        content = format_plan_details(i18n.get("distances", dist=dist), plan[str(week)], week, count_tempo_dict,
                                      i18n, 3)
        await state.update_data(train_tempo=count_tempo_dict)
        await message.answer(text=content)
        await state.set_state(FSMFillForm.make_week_completed)
    else:
        await message.answer(text=i18n.getnextweekplan())


@router.message(Command(commands='make_week_completed'), StateFilter(FSMFillForm.make_week_completed))
async def process_make_week_completed(message: Message, state: FSMContext, db: Database, i18n: TranslatorRunner):
    data = await state.get_data()

    result = await db.make_week_completed(data['plan_id'], data['week'])

    await message.answer(text=i18n.makeweekcompleted(case=result, week=data['week'],
                                                     plan=i18n.get("distances", dist=data['dist']) ))
    await state.clear()


@router.message(Command(commands='enter_trainresults'), StateFilter(FSMFillForm.make_week_completed))
async def process_enter_train_results(message: Message, state: FSMContext, db: Database, i18n: TranslatorRunner):
    data = await state.get_data()

    results = await db.get_list_oftrains(data['plan_id'], data['week'])
    buttons_dict = dict({'train1': '1-я тренировка',
          'train2': '2-я тренировка', 'train3': '3-й тренировка'})

    for result in results:
        buttons_dict.pop(result.train)

    if buttons_dict:
        await message.answer(text='Выберите тренировку',
                            reply_markup=create_inline_kb(1, buttons_dict))
        await state.set_state(FSMFillForm.select_train_results)

    else:
        await message.answer(text='Вы отметили все тренировки.')
        await state.clear()


@router.callback_query(StateFilter(FSMFillForm.select_train_results), F.data.in_(["train1", "train2", "train3"]))
async def process_select_train_results(callback: CallbackQuery, state: FSMContext, plans: dict, i18n: TranslatorRunner):
    """Handler to take train results"""
    data = await state.get_data()

    # get train plan from plans
    train_plan = plans[data['dist']][str(data['week'])][callback.data]

    # makes dict from trainplan
    intervals, goal_time = get_trainintervals(train_plan, callback.data, data['train_tempo'])

    bottons = dict()

    await state.update_data(intervals=intervals, results=dict(), train=callback.data, goal_times=goal_time)

    for interval in intervals:

        if interval < 1:
            bottons.update({str(interval): str(int(interval * 1000)) + 'm'})

        else:
            bottons.update({str(interval): str(interval) + 'km'})

    await callback.message.answer(text='Выбери дистанцию, за которую надо внести результат',
                                  reply_markup=create_inline_kb(1, bottons))
    await state.set_state(FSMFillForm.add_train_results)


@router.callback_query(StateFilter(FSMFillForm.add_train_results), CheckIntervals())
async def process_enter_train_results(callback: CallbackQuery, state: FSMContext, plans: dict, i18n: TranslatorRunner):
    data = await state.get_data()

    quantity = data['intervals'].get(float(callback.data))

    if quantity == 1:
        text = 'Введите результат для дистанции {} км'.format(callback.data)
    else:
        text = 'Введите лучший и худший результаты на интервале {} км'.format(callback.data)

    await state.update_data(waiting_result=callback.data)
    await callback.message.answer(text=text)
    await state.set_state(FSMFillForm.wait_train_results)


@router.message(StateFilter(FSMFillForm.wait_train_results), CheckTrainTimes())
async def process_enter_times(message: Message, state: FSMContext, plans: dict, i18n: TranslatorRunner):

    times = message.text.split(' ')
    data = await state.get_data()

    data['intervals'].pop(float(data['waiting_result']))
    goal = data['goal_times'][float(data['waiting_result'])]
    result_list = convert_times(times, goal)

    print('Время', result_list)
    data['results'].update({data['waiting_result']: result_list})

    await state.update_data(results=data['results'], waiting_result=None,
                            intervals=data['intervals'])

    if data['intervals']:
        bottons = dict()

        for interval in data['intervals']:
            if interval < 1:
                bottons.update({str(interval): str(int(interval * 1000)) + 'm'})

            else:
                bottons.update({str(interval): str(interval) + 'km'})
        await message.answer(text='Успешно! Выбери дистанцию, за которую надо внести результат',
                             reply_markup=create_inline_kb(1, bottons))
        await state.set_state(FSMFillForm.add_train_results)
    else:
        await message.answer(text='Успешно! Сохранить - /save_trainresults')
        await state.set_state(FSMFillForm.wait_save_trainresult)


@router.message(StateFilter(FSMFillForm.wait_save_trainresult))
async def process_save_results(message: Message, state: FSMContext, db: Database, plans: dict, i18n: TranslatorRunner):
    # get data from memorystorage
    data = await state.get_data()

    await db.add_train_results(message.from_user.id, data['plan_id'], data['week'], data['train'], data['results'])
    await message.answer(text='Успешно!')
    await state.clear()
    pass


@router.message(Command(commands='showdata'), StateFilter(default_state))
async def process_showmyprofile(message: Message, i18n: TranslatorRunner, db: Database):
    """This handler works on command showprofile and shows users profile:
    Name, age, weight, height, max pulse, pulse zones and imt"""

    profile = await db.get_users_data(message.from_user.id)

    pulse_zones = i18n.get("showpulse", maxpulse=profile.max_pulse,
                                beg1=0.5*profile.max_pulse, end1=0.6*profile.max_pulse,
                                beg2=0.6*profile.max_pulse, end2=0.75*profile.max_pulse,
                                beg3=0.75*profile.max_pulse, end3=0.85*profile.max_pulse,
                                beg4=0.85*profile.max_pulse, end4=0.95*profile.max_pulse,
                                beg5=0.95*profile.max_pulse, end5=1.0*profile.max_pulse)
    try:
        await message.answer_photo(
           photo=profile.photo,
        caption=i18n.get("show_-data_", case=0, user_name=profile.user_name, user_age=profile.age,
                                user_gender=profile.gender, weight=profile.weight, height=profile.height,
                                imt=profile.imt,
                                pulsezones=pulse_zones
                                )
        )
    except TelegramBadRequest:
        logger.error('Тут было исключение', profile.photo, exc_info=True)


@router.message(Command('change_profile'), StateFilter(default_state))
async def process_change_profile(message: Message, state: FSMContext, i18n: TranslatorRunner):
    # сохраняем в хранилище
    buttons = dict({'age':i18n.get('changeprofile', case='age'),
          'weight':i18n.get('changeprofile', case='weight'),
          'height':i18n.get('changeprofile', case='height'),
          'photo':i18n.get('changeprofile', case='photo')})

    await state.update_data(buttons=buttons)

    await message.answer(text=i18n.get('changeprofile', case=0),
                         reply_markup=create_inline_kb(1, buttons))
    await state.set_state(FSMFillForm.change_profile)


@router.callback_query(StateFilter(FSMFillForm.change_profile), F.data.in_(['age', 'weight', 'height', 'photo']))
async def process_value_selected(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    # сохраняем в хранилище
    await state.update_data(key=callback.data)

    await callback.message.answer(text=i18n.get('waitdata', case=0),
                                  reply_markup=None)
    await state.set_state(FSMFillForm.wait_data)


@router.message(StateFilter(FSMFillForm.wait_data), CheckProfileData())
async def process_value_sent(message: Message, state: FSMContext, i18n: TranslatorRunner):
    # получаем ключ из хранилища
    data = await state.get_data()
    val = float(message.text.replace(',', '.'))
    buttons = dict([(k, v) for k, v in data['buttons'].items() if k != data['key']])
    # сохраняем результат в соответствующих ключах
    if data['key'] == 'age':
        await state.update_data(age=val, buttons=buttons)
    elif data['key'] == 'weight':
        await state.update_data(weight=val, buttons=buttons)
    elif data['key'] == 'height':
        await state.update_data(height=val, buttons=buttons)
    # выводим ответ и клавиатуру для выбора
    if buttons:
        await message.answer(text=i18n.get('waitdata', case=1),
                             reply_markup=create_inline_kb(1, buttons))
    else:
        await message.answer(text=i18n.get('waitdata', case=2),
                             reply_markup=None)
    await state.set_state(FSMFillForm.change_profile)


@router.message(StateFilter(FSMFillForm.wait_data), F.photo[-1].as_('largest_photo'))
async def process_photo_sent(message: Message, state: FSMContext, largest_photo: PhotoSize, i18n: TranslatorRunner):
    # Cохраняем данные фото (file_unique_id и file_id) в хранилище
    # по ключам "photo_unique_id" и "photo_id"
    await state.update_data(
        photo_unique_id=largest_photo.file_unique_id,
        photo_id=largest_photo.file_id
    )
    # получаем ключ из хранилища
    data = await state.get_data()
    buttons = dict([(k, v) for k, v in data['buttons'].items() if k != 'photo'])
    # Отправляем пользователю сообщение с клавиатурой
    if buttons:
        await message.answer(text=i18n.get('waitdata', case=1),
                             reply_markup=create_inline_kb(1, buttons))
    else:
        await message.answer(text=i18n.get('waitdata', case=2),
                             reply_markup=None)
    await state.set_state(FSMFillForm.change_profile)


@router.message(Command(commands='save_profile'), StateFilter(FSMFillForm.change_profile))
async def process_get_data(message: Message, state: FSMContext, db: Database, i18n: TranslatorRunner):
    # получаем ключ из хранилища
    data = await state.get_data()
    profile = await db.get_users_data(message.from_user.id)
    changed_profile = calculate_save(profile, **data)
    await db.change_profile_data(message.from_user.id, **changed_profile)
    await message.answer(text=i18n.get('waitdata', case=3),
                         reply_markup=None)
    await state.clear()


@router.message(Command(commands='plan_my_race'), StateFilter(default_state))
async def process_plan_my_race(message: Message, state: FSMContext, i18n: TranslatorRunner):

    await message.answer(text=i18n.get('planmyrace', case=0))
    await state.set_state(FSMFillForm.get_race_dist)


@router.message(StateFilter(FSMFillForm.get_race_dist), CheckDist())
async def process_get_dist(message: Message, state: FSMContext, i18n: TranslatorRunner):

    await state.update_data(dict=float(message.text.replace(',', '.')))

    distance = float(message.text)
    k = int(distance)
    m = int((distance - k) * 1000)

    await message.answer(text=i18n.get('planmyrace', case=1, km=k, metr=m))
    await state.set_state(FSMFillForm.get_race_time)


@router.message(StateFilter(FSMFillForm.get_race_time), CheckTime())
async def process_get_race_time(message: Message, state: FSMContext, i18n: TranslatorRunner):
    h, m, s = findall(r'(\d{2})', message.text)
    race_time = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
    dist = await state.get_data()
    plan = count_race_plan(dist['dict'], race_time)

    k = int(dist['dict'])
    m = int((dist['dict'] - k) * 1000)

    await message.answer(text=i18n.get('planmyrace', case=2, km=k, metr=m) + plan)
    await state.clear()


@router.message(Command(commands='show_my_pulse_zones'))
async def process_show_pulse_zones(message: Message, db: Database, i18n: TranslatorRunner):

    profile = await db.get_users_data(message.from_user.id)
    await message.answer(text=i18n.get("showpulse",
    maxpulse = profile.max_pulse,
    beg1 = 0.5 * profile.max_pulse, end1 = 0.6 * profile.max_pulse,
    beg2 = 0.6 * profile.max_pulse, end2 = 0.75 * profile.max_pulse,
    beg3 = 0.75 * profile.max_pulse, end3 = 0.85 * profile.max_pulse,
    beg4 = 0.85 * profile.max_pulse, end4 = 0.95 * profile.max_pulse,
    beg5 = 0.95 * profile.max_pulse, end5 = 1.0 * profile.max_pulse
                                       ))


@router.message(Command(commands='get_fttrain'), StateFilter(default_state))
async def process_get_fttrain(message: Message, i18n: TranslatorRunner):
    """ Sends random FT train"""

    await message.answer(text=i18n.get("fttrain", complex=random.randint(0, 9)))


@router.message(Command(commands='get_runskillstrain'), StateFilter(default_state))
async def process_get_get_runskillstrain(message: Message, i18n: TranslatorRunner):
    """ Sends random train on run skills"""
    await message.answer(text=i18n.get("runskillstrain"))