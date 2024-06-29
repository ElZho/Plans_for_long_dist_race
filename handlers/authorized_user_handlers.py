import logging
import os
from datetime import timedelta, datetime, time
from re import findall

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import (CallbackQuery, Message, FSInputFile, PhotoSize, ErrorEvent)
from aiogram.utils import formatting

from database.methods import (get_plan_name, create_race_report, make_plan_active, delete_plan, get_next_week_plan,
                              make_week_completed, get_my_profile)
from filters.filtres import CheckTime, IsAuthorized, CheckPlans, CheckRaces, CheckProfileData, CheckDist
from keyboards.keyboards import create_pagination_keyboard, create_inline_kb
from lexicon import lexicon_ru
from lexicon.lexicon_ru import LEXICON_INLINE_BUTTUNS, LEXICON_SELECT_DIST
from services.calculations import find_vdot, count_target_tempo
from services.planing import sent_plan
from services.services import show_my_plans, get_plan_details, format_plan_details, collect_my_race_report, \
    calculate_save, count_race_plan
from states.states import FSMFillForm


logger = logging.getLogger(__name__)
router = Router()
router.message.filter(IsAuthorized())


# Этот хэндлер будет срабатывать на команду /help вне состояний
# и рассказывать о возможностях системы и сообщать команды.
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(
        text=lexicon_ru.LEXICON_RU['help_for_authorized_user']
    )


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# не равным по умолчанию и сообщать, что эта команда работает внутри машины состояний
@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):

    await message.answer(
        text=lexicon_ru.LEXICON_RU['cancel in FSM']
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


@router.error()
async def error_handler(event: ErrorEvent):
    logger.critical("Critical error caused by %s", event.exception, exc_info=True)


@router.message(Command(commands='get_my_plans'), StateFilter(default_state))
async def process_get_my_plans(message: Message, state: FSMContext):
    # get plans from db and pass them to buttons
    buttons_name = show_my_plans(message.from_user.id)

    await message.answer(
        text=lexicon_ru.LEXICON_RU['get_my_plans'], reply_markup=create_inline_kb(1, buttons_name)
    )
    await state.set_state(FSMFillForm.view_saved_plan)


@router.callback_query(StateFilter(FSMFillForm.view_saved_plan), CheckPlans())
async def process_get_my_plans_details(callback: CallbackQuery, state: FSMContext):
    # get training and format it
    training = get_plan_details(callback.from_user.id, callback.data)
    plan = get_plan_name(callback.data)
    page = len(training.keys())

    # save state data
    await state.update_data(training=training, plan=plan, page_quantity=page, page=page, plan_id=callback.data)

    # format training into message
    content = format_plan_details(training[page], plan, page, ['/make_plan_active', '/delete_plan'])

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(**content.as_kwargs(), reply_markup=create_pagination_keyboard(
        'backward',
        f'{str(page)}/{str(page)}',
        'forward'))


@router.callback_query(StateFilter(FSMFillForm.view_saved_plan), F.data == 'forward')
async def process_forward_press(callback: CallbackQuery, state: FSMContext):
    # получаем данные из хранилища
    data = await state.get_data()

    if data['page'] > 1:
        # перелистываем страницу назад
        pg = data['page'] - 1
        await state.update_data(page=data['page'] - 1)

        # format training
        content = format_plan_details(data['training'][pg], data['plan'], pg, ['/make_plan_active',
                                                                                   '/delete_plan'])

        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.edit_text(**content.as_kwargs(), reply_markup=create_pagination_keyboard(
            'backward',
            f'{str(pg)}/{str(data['page_quantity'])}',
            'forward'))


@router.callback_query(StateFilter(FSMFillForm.view_saved_plan), F.data == 'backward')
async def process_backward_press(callback: CallbackQuery, state: FSMContext):
    # получаем данные из хранилища
    data = await state.get_data()
    if data['page'] < data['page_quantity']:
        # перелистываем страницу назад
        page = data['page'] + 1
        await state.update_data(page=page)

        # format training
        content = format_plan_details(data['training'][page], data['plan'], page, ['/make_plan_active',
                                                                                   '/delete_plan'])

        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.edit_text(**content.as_kwargs(), reply_markup=create_pagination_keyboard(
            'backward',
            f'{str(page)}/{str(data['page_quantity'])}',
            'forward'))


@router.message(Command(commands='make_plan_active'), FSMFillForm.view_saved_plan)
async def process_make_plan_active(message: Message, state: FSMContext):
    data = await state.get_data()
    result = make_plan_active(message.from_user.id, int(data['plan_id']))

    if result == 0:
        await message.answer(text=lexicon_ru.LEXICON_RU['make_plan_active'][0])
    else:
        plan = lexicon_ru.LEXICON_SELECT_DIST[str(data['plan'])]
        await message.answer(text=lexicon_ru.LEXICON_RU['make_plan_active'][1].format(plan))

    await state.clear()


@router.message(Command(commands='delete_plan'), FSMFillForm.view_saved_plan)
async def process_delete_plan(message: Message, state: FSMContext):
    data = await state.get_data()
    delete_plan(message.from_user.id, int(data['plan_id']))
    plan = lexicon_ru.LEXICON_SELECT_DIST[str(data['plan'])]

    await message.answer(text=lexicon_ru.LEXICON_RU['delete_plan'].format(plan))
    await state.clear()



@router.message(Command(commands='add_new_race_result'), StateFilter(default_state))
async def process_add_new_result(message: Message, state: FSMContext):
    # get plans from db and pass them to buttons

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text=lexicon_ru.LEXICON_RU['fill_height'],
        # Dist_markup
        reply_markup=create_inline_kb(3,
                                      LEXICON_INLINE_BUTTUNS)
    )
    await state.set_state(FSMFillForm.add_new_result)


@router.callback_query(StateFilter(FSMFillForm.add_new_result), F.data.in_(LEXICON_INLINE_BUTTUNS))
async def select_distances(callback: CallbackQuery, state: FSMContext):
    # Cохраняем дистанцию (callback.data нажатой кнопки) в хранилище,
    # по ключу "res_distances"
    await state.update_data(res_distances=callback.data)

    # Отправляем пользователю сообщение с клавиатурой
    await callback.message.delete()
    await callback.message.answer(
        text=lexicon_ru.LEXICON_RU['select_distances'].format(callback.data)
    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.add_new_result_time)


@router.message(StateFilter(FSMFillForm.add_new_result_time), CheckTime())
async def process_res_time_sent(message: Message, state: FSMContext):
    # Превращаем часы, минуты, секунды в время"
    h, m, s = findall(r'(\d{2})', message.text)

    # Cохраняем часы в хранилище по ключу "result"
    await state.update_data(result=timedelta(hours=int(h), minutes=int(m), seconds=int(s)))
    data = await state.get_data()
    # считаем VO2Max
    vdot, _ = (
        find_vdot(data["res_distances"],
                  datetime.strptime(str(data['result']), '%H:%M:%S')))

    create_race_report(message.from_user.id, data['res_distances'], time(hour=int(h), minute=int(m), second=int(s)),
                       vdot)

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text=lexicon_ru.LEXICON_RU['new_time_sent']
    )
    await state.clear()


@router.message(Command(commands='get_plan_in_file'), StateFilter(default_state))
async def process_sent_file(message: Message, state: FSMContext):
    buttons_name = show_my_plans(message.from_user.id)
    if not buttons_name:
        await message.answer(lexicon_ru.LEXICON_RU['get_saved_plan_in_file'])
    elif len(buttons_name) == 1:
        plan_name = get_plan_name(list(buttons_name.keys())[0])
        data = get_plan_details(message.from_user.id, list(buttons_name.keys())[0])
        filename = sent_plan(LEXICON_SELECT_DIST[str(plan_name)],
                             lexicon_ru.LEXICON_RU['Info_text'], data, message.chat.id)
        # отправляем
        doc = FSInputFile(filename)
        await message.reply_document(doc)
        # удаляем файл
        os.remove(filename)
    else:
        await message.answer(
            text=lexicon_ru.LEXICON_RU['get_my_plans'], reply_markup=create_inline_kb(2, buttons_name)
        )
        await state.set_state(FSMFillForm.get_saved_plan_in_file)


@router.callback_query(StateFilter(FSMFillForm.get_saved_plan_in_file), CheckPlans())
async def process_get_saved_plan_in_file(callback: CallbackQuery, state: FSMContext):
    # get training and format it
    data = get_plan_details(callback.from_user.id, callback.data)
    plan_name = get_plan_name(callback.data)

    # упаковываем в файл txt
    filename = sent_plan(LEXICON_SELECT_DIST[str(plan_name)],
                         lexicon_ru.LEXICON_RU['Info_text'], data, callback.message.chat.id)
    # отправляем
    doc = FSInputFile(filename)
    await callback.message.reply_document(doc)
    # удаляем файл
    os.remove(filename)
    await state.clear()


@router.message(Command(commands='calculate'), StateFilter(default_state))
async def process_calculate_new_plan(message: Message, state: FSMContext):
    await message.answer(lexicon_ru.LEXICON_RU['calculate_new_plan'],
                         reply_markup=create_inline_kb(2, lexicon_ru.LEXICON_YES_NO))
    await state.set_state(FSMFillForm.select_result)


# Этот хендлер будет срабатывать на 'yes': 'Внесу новый'
@router.callback_query(StateFilter(FSMFillForm.select_result), F.data.in_(['yes']))
async def process_add_new_result(callback: CallbackQuery, state: FSMContext):
    # удаляем предыдущее сообщение
    await callback.message.delete()

    # Отправляем пользователю сообщение с клавиатурой
    await callback.message.answer(
        text=lexicon_ru.LEXICON_RU['fill_height'],
        # Dist_markup
        reply_markup=create_inline_kb(3,
                                      LEXICON_INLINE_BUTTUNS)
    )
    await state.set_state(FSMFillForm.add_new_result)


# Этот хендлер будет срабатывать 'no': 'Выберу из старых'
@router.callback_query(StateFilter(FSMFillForm.select_result), F.data.in_(['no']))
async def process_select_result(callback: CallbackQuery, state: FSMContext):
    # удаляем предыдущее сообщение
    await callback.message.delete()

    # выводим рейсы
    my_races = collect_my_race_report(callback.from_user.id)
    await state.update_data(my_races=my_races)
    buttons = dict([(k, '{} - {} за {} VO2max {}'.format(*v)) for k, v in my_races.items()])
    await callback.message.answer(
        text=lexicon_ru.LEXICON_RU['select_result'],
        # Dist_markup
        reply_markup=create_inline_kb(1,
                                      buttons)
    )
    await state.set_state(FSMFillForm.get_new_paces)


@router.callback_query(StateFilter(FSMFillForm.get_new_paces), CheckRaces())
async def process_calculate_paces(callback: CallbackQuery, state: FSMContext):
    # удаляем предыдущее сообщение
    await callback.message.delete()

    data = await state.get_data()

    result = data['my_races'][callback.data]
    user_dict = dict()

    # считаем VO2Max
    user_dict['vdot'], user_dict['results'] = (find_vdot(result[1],
                                                         datetime.strptime(str(result[2]), '%H:%M:%S')))
    if int(user_dict['vdot']) < 65:
        # считаем темпы
        user_dict['count_tempo'] = (
            count_target_tempo(user_dict['results']['5000 м'],
                               user_dict['vdot']))
        await state.update_data(count_tempo=user_dict['count_tempo'],
                                vdot=user_dict['vdot'])
        # оформляем достижимые результаты
        target_results = [formatting.as_line(k, formatting.Italic(v), sep=' ')
                          for k, v in user_dict['results'].items() if k != 'VD0T']
        # оформляем темпы для тренировок
        paces = [formatting.as_line(k, v, sep=' ') for k, v in user_dict['count_tempo'].items()]
        # оформляем сообщение
        content = formatting.as_list(
            formatting.as_line(lexicon_ru.LEXICON_RU['process_calculate_vdot_command'][0],
                               user_dict['results']['VD0T']),
            formatting.as_marked_section(
                formatting.Bold(lexicon_ru.LEXICON_RU['process_calculate_vdot_command'][1]),
                *target_results,
                marker="🔸 ", ),
            formatting.as_marked_section(
                formatting.Bold(lexicon_ru.LEXICON_RU['process_calculate_vdot_command'][2]),
                *paces,
                marker="🔸 ", ),
        )

        await callback.message.answer(**content.as_kwargs(), reply_markup=create_inline_kb(2, LEXICON_SELECT_DIST))
        await state.set_state(FSMFillForm.select_dist)
    else:
        await callback.message.answer(
            lexicon_ru.LEXICON_RU['process_calculate_vdot_command'][3].format(user_dict['vdot']))
        await state.clear()



@router.message(Command(commands='get_next_week_plan'), StateFilter(default_state))
async def process_get_next_week_plan(message: Message, state: FSMContext):
    result = get_next_week_plan(message.from_user.id)

    if result == 0:
        await message.answer(lexicon_ru.LEXICON_RU['get_next_week_plan'][0])
    elif result == 1:
        await message.answer(lexicon_ru.LEXICON_RU['get_next_week_plan'][1])
    else:
        await state.update_data(week=result[0].week, plan_id=result[0].plan_id, first_train=result[0].first_train,
                                second_train=result[0].second_train,
                                third_train=result[0].third_train)

        page_text = lexicon_ru.LEXICON_RU['process_calculate_plan_command'][0].format(result[0].week)
        weekly_train = [result[0].first_train, result[0].second_train, result[0].third_train]
        training = [formatting.as_key_value(formatting.as_line(
                                                               lexicon_ru.LEXICON_RU[
                                                                   'process_calculate_plan_command'][
                                                                   1].format(i + 1),
                                                               end='\n------------------------------\n'),
                                            weekly_train[i], ) for i in range(3)]
        content = formatting.as_list(
            formatting.Underline(page_text),
            *training,
            formatting.BotCommand('/make_week_completed')
            ,
            formatting.BotCommand('/cancel')
        )

        await message.answer(**content.as_kwargs())
        await state.set_state(FSMFillForm.make_week_completed)


@router.message(Command(commands='make_week_completed'), StateFilter(FSMFillForm.make_week_completed))
async def process_make_week_completed(message: Message, state: FSMContext):
    data = await state.get_data()
    # spisok = takes_week_details(data)
    result = make_week_completed(message.from_user.id, data['plan_id'], data['week'])
    await message.answer(text=lexicon_ru.LEXICON_RU['make_week_completed'][result].format(data['week']))
    await state.clear()


@router.message(Command(commands='showmyprofile'))
async def process_showmyprofile(message: Message):
    """This handler works on command showprofole and shows users profile:
    Name, age, weight, height, max pulse, pulse zones and imt"""

    name, profile, _ = get_my_profile(message.from_user.id)
    data = dict({'age': profile.age, 'height': profile.height, 'weight': profile.weight,
                 'IMT': profile.imt, 'max_pulse': profile.max_pulse})

    caption = formatting.as_list(formatting.as_section(formatting.Bold(name),
                                                       formatting.as_list(formatting.as_list(
                                                           *[formatting.as_key_value(v,
                                                                                     data[k])
                                                             for k, v in
                                                             lexicon_ru.SHOW_DATA['photo_capt'].items()
                                                             if k not in ["gender", 'res_distances', 'result']]

                                                       ), sep="\n\n", )),

                                 lexicon_ru.LEXICON_RU['showdata'][1],
                                 formatting.BotCommand('/change_profile'),
                                 sep="\n\n",
                                 )
    try:
        await message.answer_photo(
            photo=profile.photo,
            caption=caption.as_html())
    except TelegramBadRequest:
        logger.error('Тут было исключение', profile.photo, exc_info=True)


@router.message(Command('change_profile'), StateFilter(default_state))
async def process_change_profile(message: Message, state: FSMContext):
    # сохраняем в хранилище
    buttons = dict(filter(lambda item: item[0] in ('age', 'weight', 'height'),
                          lexicon_ru.SHOW_DATA['photo_capt'].items()))
    buttons.update({'photo': 'photo'})
    await state.update_data(buttons=buttons)

    await message.answer(text=lexicon_ru.LEXICON_RU['change_profile'],
                         reply_markup=create_inline_kb(1, buttons))
    await state.set_state(FSMFillForm.change_profile)


@router.callback_query(StateFilter(FSMFillForm.change_profile), F.data.in_(['age', 'weight', 'height', 'photo']))
async def process_value_selected(callback: CallbackQuery, state: FSMContext):
    # сохраняем в хранилище
    await state.update_data(key=callback.data)

    await callback.message.answer(text=lexicon_ru.LEXICON_RU['wait_data'][0],
                                  reply_markup=None)
    await state.set_state(FSMFillForm.wait_data)


@router.message(StateFilter(FSMFillForm.wait_data), CheckProfileData())
async def process_value_sent(message: Message, state: FSMContext):
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
        await message.answer(text=lexicon_ru.LEXICON_RU['wait_data'][1],
                             reply_markup=create_inline_kb(1, buttons))
    else:
        await message.answer(text=lexicon_ru.LEXICON_RU['wait_data'][2],
                             reply_markup=None)
    await state.set_state(FSMFillForm.change_profile)


@router.message(StateFilter(FSMFillForm.wait_data), F.photo[-1].as_('largest_photo'))
async def process_photo_sent(message: Message, state: FSMContext, largest_photo: PhotoSize):
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
        await message.answer(text=lexicon_ru.LEXICON_RU['wait_data'][1],
                             reply_markup=create_inline_kb(1, buttons))
    else:
        await message.answer(text=lexicon_ru.LEXICON_RU['wait_data'][2],
                             reply_markup=None)
    await state.set_state(FSMFillForm.change_profile)


@router.message(Command(commands='count_save'), StateFilter(FSMFillForm.change_profile))
async def process_get_data(message: Message, state: FSMContext):
    # получаем ключ из хранилища
    data = await state.get_data()
    res = calculate_save(message.from_user.id, **data)
    await message.answer(text=lexicon_ru.LEXICON_RU['count_save'][res],
                         reply_markup=None)
    await state.clear()


@router.message(Command(commands='plan_my_race'), StateFilter(default_state))
async def process_plan_my_race(message: Message, state: FSMContext):

    await message.answer(text=lexicon_ru.LEXICON_RU['plan_my_race'][0])
    await state.set_state(FSMFillForm.get_race_dist)


@router.message(StateFilter(FSMFillForm.get_race_dist), CheckDist())
async def process_get_dist(message: Message, state: FSMContext):
    await state.update_data(dict=float(message.text.replace(',', '.')))

    distance = float(message.text)
    k = int(distance)
    m = int((distance - k) * 1000)

    await message.answer(text=lexicon_ru.LEXICON_RU['plan_my_race'][1].format(k, m))
    await state.set_state(FSMFillForm.get_race_time)


@router.message(StateFilter(FSMFillForm.get_race_time), CheckTime())
async def process_get_race_time(message: Message, state: FSMContext):
    h, m, s = findall(r'(\d{2})', message.text)
    race_time = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
    dist = await state.get_data()
    plan = count_race_plan(dist['dict'], race_time)

    k = int(dist['dict'])
    m = int((dist['dict'] - k) * 1000)

    content = formatting.as_marked_section(
        formatting.Bold(lexicon_ru.LEXICON_RU['plan_my_race'][2].format(k, m)),
        *plan, marker="\n🔸 ",
    )
    await message.answer(**content.as_kwargs())
    await state.clear()
