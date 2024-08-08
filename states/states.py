from aiogram.fsm.state import State, StatesGroup


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодействия с пользователем
    fill_name = State()  # Состояние ожидания ввода имени
    fill_age = State()  # Состояние ожидания ввода возраста
    fill_gender = State()  # Состояние ожидания выбора пола
    fill_weight = State()  # Состояние ожидания ввода веса
    fill_height = State()  # Состояние ожидания ввода веса
    upload_photo = State()  # ждем фото
    show_data = State() # Состояние ожидания команды показать анкету
    save_data = State() # Ожидание команды сохранить анкету

    wait_calc = State()  # считаем VDOT
    select_dist = State()  # выбираем дистанцию подготовки
    plan_dist = State()  # планируем тренировки
    wait_save_file = State()  # ожидание команды сохранить файл
    view_saved_plan = State()  # ожидание просмотра сохраненных планов для зарегистрированных пользователй

    add_new_result = State()  # ожидание ввода нового результата забега, выбор дистанции
    add_new_result_time = State()  # ожидание ввода результата забега, ввод времени

    # get_saved_plan_in_file = State()  # ожидание получения сохраненного плана в файл
    select_result = State()  # выбор результата для расчета нового плана
    result_analysis = State()  # анализ выбранного результата для целей расчета план

    make_week_completed = State()  # отметить план на неделю выполненным
    select_train_results = State() # выбрать результат, который нужно внести
    add_train_results = State() # внести результаты тренировки
    wait_train_results = State() # ожидание внесения времени за тренировочную дистанцию
    # select_train_intervals = State() # ожидание выбора интервала/дистанции за которую внести время
    wait_save_trainresult = State() # ожидание сохранения внесенных результатов тренировки

    change_profile = State()  # состояние выбора параметров, которые нужно изменить в профиле
    wait_data = State()  #

    get_race_dist = State() # ожидание ввода дистанции для расчета плана на гонку
    get_race_time = State() # ожидание ввода планируемого времени пробега
