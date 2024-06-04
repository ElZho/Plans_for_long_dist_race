LEXICON_RU: dict[str, str] = {

    'help': 'Итак:\n\nЯ сначала определю твой текущий уровень. '
            'Для этого мне потребуются результаты твоих забегов. '
            'Лучше всего\nвзять результаты забегов на длинные дистанции\n'
            'Но если таких нет,\nто подойдут и короткие.\nХотя расчет будет '
            'менее точным\n\n'
            'После того, как я узнаю твой текущий уровень,\nя смогу рассчитать темп\nдля '
            'разных видов тренировок.\nВесь план состоит из 3-х типов\nтренировок: '
            'интервальных, темповых и длинных.\nВ неделю необходимо проводить минимум три\nбеговых тренировки. '
            'Их желательно дополнить тренировками\nкроссфит и тренировками для улучшения техники бега\nПлан подготовки '
            'к забегу на 5-10 км рассчитан на 12 недель.\nК полумарафону и марафонам - 16.\nСначала рассчитаем текущий '
            'VDOT\n\n'
            'Доступные команды:\n/fillform - начать рассчет плана'
            '\n/cancel - отмена\n'
            '/showdata -  посмотреть внесенные данные\n'
            '/calculate - посмотреть результаты, которые ты\nсможешь достичь с текущим уровнем VO2max\n'
            '/get_plan_in_file - получить файл с планом.\nБудет отправлен файл в формате txt\n'
            '/get_my_plans -  для авторизированных пользователей, выводит список планов\n'
            '/add_new_race_result -  добавить новые результаты забегов',

    'help_for_authorized_user': 'Доступные команды:\n/fillform - начать рассчет плана\n'
                                '/cancel - отмена\n'
                                '/showmyprofile -  посмотреть внесенные данные\n'
                                '/calculate - посмотреть результаты, которые ты\nсможешь достичь с текущим уровнем VO2max\n'
                                '/get_plan_in_file - получить файл с планом.\nБудет отправлен файл в формате txt\n'
                                '/get_my_plans -  для авторизированных пользователей, выводит список планов\n'
                                '/add_new_race_result -  добавить новые результаты забегов\n'
                                '/get_next_week_plan - посмотреть план на следующую неделю',

    'start': 'Привет!\nЯ бот, который поможет тебе '
             'составить планы подготовки\nс забегам.\n'
             'Чтобы понять, что я умею, отправь /help\n'
             'Чтобы начать - отправь команду\n/fillform',

    'fillform': 'Пожалуйста, введите ваше имя',

    'name_sent': 'Спасибо!\n\nА теперь введите ваш возраст',

    'wrong_name': 'То, что вы отправили не похоже на имя\n\n'
                  'Пожалуйста, введите ваше имя\n\n'
                  'Если вы хотите прервать заполнение анкеты - '
                  'отправьте команду /cancel',

    'fill_age': 'Спасибо!\n\nУкажите ваш пол',

    'wrong_not_age': 'Калькулятор рассчитан на возраст от 16 до 90\n\n'
                     'Если ваш возраст отличается от указанного\n\nто вы можете прервать '
                     'заполнение анкеты - отправьте команду /cancel',

    'gender_press': 'Спасибо!\n\nУкажите ваш вес',

    'fill_weight': 'Спасибо!\n\nВведите рост',

    'wrong_weight': 'Калькулятор рассчитан на вес от 35 до 150 кг\n\n'
                    'Если ваш вес отличается от указанного,\n\nто вы можете прервать '
                    'заполнение анкеты - отправьте команду /cancel',

    'fill_height': 'Спасибо!\n\nВведите дистанцию, за которую\n'
                   'хотите ввести свои результаты',

    'wrong_height': 'Калькулятор рассчитан на рост от 135 до 250 см\n\n'
                    'Если ваш рост отличается от указанного,\n\nто вы можете прервать '
                    'заполнение анкеты - отправьте команду /cancel',

    'warning_not_distances': 'Нажмите кнопку выбора дистанции\n\n'
                             'Если ошиблись, повторите ввод.',

    'select_distances': 'Спасибо!\n\nУкажите ваш результат - время, за которое вы преодолели {}.\n '
                        'В формате 01:21:15',

    'warning_wrong_time': 'Время должно быть введено в формате 01:21:15\n'
                          ' или 01h21m15s или 012115.\nЧасы должны быть не больше 24.\n'
                          'Минуты и секунды не больше 60.',

    'time_sent': 'Спасибо!\n\nТеперь добавьте фото',

    'photo_sent': 'Спасибо!\n\n'
                  'Чтобы посмотреть данные вашей '
                  'анкеты - отправьте команду /showdata',

    'not_photo': 'Это не фото',

    'wrong_ans': 'Ты отправил не то, что я ожидал. Подумай!!! Если робот не реагирует, жми /esc',

    'showdata': ['Пульсовые зоны:', 'Чтобы сохранить данные нажмите:'],

    'process_calculate_vdot_command': ['Твой VO2max - ', "Достижимые результаты для тебя на разных дистанциях:\n",
                                       "Твои тренировочные темпы для разных дистанций\n"],

    'process_calculate_plan_command': ["{} недель до старта\n", '-я тренировка ', 'Твой план подготовки к '],

    'save_data': 'Чтобы перейти к расчету\nрассчитать введите /calculate',

    'save_plan': 'План сохранен.\nТеперь ты всегда можешь посмотреть его.\n Команда - /get_my_plans\n'
                 'Чтобы получить план в файле - /get_plan_in_file\n'
                 'Чтобы перейти к другим действиям введите отправьте\n'
                 '/help и выберете действие',

    'get_saved_plan_in_file': 'У тебя нет сохраненных планов',

    'cancel in FSM': 'Отмена расчета. 🤷',

    'cancel out FSM': 'А я ничего и не рассчитываю. Отменять нечего. 🤷',

    'message out FSM': 'А я ничего и не рассчитываю.\nВыбири команду чтобы начать расчет\n - /fillform',

    'get_my_plans': 'Планы тренировок:\nЧтобы выйти из режима просмотра\nпланов - /cancel',

    'calculate_new_plan': 'Чтобы рассчитать план,\nнужно выбрать результат забега,\nна основе которого рассчитать.\n'
                          'Хочешь внести новый результат\nили выбрать из внесенных ранее?',

    'select_result': 'Выберете вариант:',

    'new_time_sent': 'Спасибо. Новый результат сохранен.\nЕсли хотите рассчитать новый\nплан - введите /calculate',

    'make_plan_active': ['У тебя уже есть активный план', 'Теперь {} активный.\nТы можешь начинать тренироваться!'],

    'delete_plan': 'Твой план {} удален.',

    'get_next_week_plan': ['У тебя нет активного плана', 'Ты выполнил весь план'],

    'make_week_completed': ['У тебя нет активного плана', 'Вы выполнили весь план.', 'Вы выполнили {} неделюю'],

    'change_profile': 'Выберете значение,\nкоторое хотите поменять:',

    'wait_data': ['Введите значение:', 'Спасибо. Хотите изменить еще значение?\nВыберете показатель для замены\n'
                                       'Или введите, чтобы сохранить /count_save',
                  'Вы изменили все возможные данные.\nВведите, чтобы сохранить /count_save'],

    'count_save': ['Произошла непредвиденная ошибка', 'Данные сохранены'],

    'Info_text': '    План состоит из 12 - 16 тренировочных недель. На каждой неделе необходимо выполнить 3 тренировки\n'
                 '1-я тренировка - интервальная, 2-я тренировка - темповая, 3-й тренировка рассчитана на повышение вы-\n'
                 'носливости.\n'
                 '    Обратите внимание, что рекомендованные темпы рассчитаны на основании среднестатистических данных.\n'
                 'Поэтому при выполнении тренировок ориентируйтесь на свои ощущения. После тренировки вы не должны\n'
                 'чувствовать изнеможение. Тренировка это часть жизни.У вас должны оставаться силы на общение с семьей\n'
                 ' и друзьями.\n'
                 '    Если вам тяжело выполнять этот план тренировок, рекомендуется его пересчитать, указав большее\n '
                 'время прохождения дистанции. Особенно это рекомендуется сделать, если вы начинающий бегун и еще не\n'
                 'бегали длинные дистанции. Оптимальной для расчета является дистанция 5, 10 или более км. Если вы еще\n'
                 'бегали дистанции 5, 10 км, то после того, как вы сможете пробежать такую дистанцию, пересчитайте план\n'
                 'на основании полученных данных.\n\n'
                 '    Легенда\n8x400 (400 RI) - 8 раз по 400 m с отдыхом 400m.\n'
                 '6x800 (90 sec RI) - 6 раз по 800 метров с отдыхом 90 сек.\n'
}

Sex_buttons: dict[str, str] = {
    'Мужской': 'Мужской ♂',
    'Женский': 'Женский ♀'
}

LEXICON_COMMANDS_RU: dict[str, str] = {
    '/start': 'Запуск бота',
    '/help': 'Помощь',
    '/cancel': 'Отмена'
}

LEXICON_INLINE_BUTTUNS: dict[str, str] = {
    '1500 м': '1,5км',
    'Миля': 'Миля',
    '3000 м': '3км',
    '2 мили': '2 мили',
    '5000 м': '5км',
    '10000 м': '10км',
    '15000 м': '15км',
    'Полумарафон': 'Полумарафон',
    'Марафон': 'Марафон'
}

LEXICON_YES_NO: dict[str, str] = {
    'yes': 'Внесу новый',
    'no': 'Выберу из старых'
}

LEXICON_SELECT_DIST: dict[str, str] = {
    '0': '5-10K',
    '1': 'Half marathon',
    '2': 'My first marathon',
    '3': 'Marathon (I\'ve already finished the one)'
}
PAG_BUTTON = {'backward': '<<',
              'forward': '>>'}

SHOW_DATA: dict[str, dict[str, str]] = {
    'photo_capt': {
        'age': 'Возраст',
        "gender": 'Пол',
        'weight': 'Вес',
        'height': 'Рост',
        'res_distances': 'Дистанция',
        'result': 'Результат',
        'IMT': 'Индекс массы тела',
        "max_pulse": 'Максимальный пульс'
    },
    'pulse_zone': {
        'I зона:': (0.5, 0.6),
        'II зона:': (0.6, 0.75),
        'III зона:': (0.75, 0.85),
        'IV зона:': (0.85, 0.95),
        'V зона:': (0.95, 1)
    }
}

PLAN_CONDITIONS: dict = {(True, False): 'Выполняется',
                         (False, True): "Завершен",
                         (False, False): 'Неактивный',
                         (True, True): "Завершен"}
