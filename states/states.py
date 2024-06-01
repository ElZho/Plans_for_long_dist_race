from aiogram.fsm.state import State, StatesGroup

# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодействия с пользователем
    fill_name = State()        # Состояние ожидания ввода имени
    fill_age = State()         # Состояние ожидания ввода возраста
    fill_gender = State()      # Состояние ожидания выбора пола
    fill_weight = State()     # Состояние ожидания ввода веса
    fill_height = State()  # Состояние ожидания ввода веса
    fill_res_distances = State()   # Состояние ожидания выбора дистанции для ввода результатов
    fill_res_time = State()   # Состояние ожидания ввода времени прохождения указанной дистанции
    upload_photo = State() # ждем фото
    wait_calc = State()  # считаем VDOT
    select_dist = State()  # выбираем дистанцию подготовки
    plan_dist = State()  # планируем тренировки
    wait_sent_file = State() # ожидание отправки файла с планом
    view_saved_plan = State() # ожидание просмотра сохраненных планов для зарегистрированных пользователй
    add_new_result = State() # ожидание ввода нового результата забега, выбор дистанции
    add_new_result_time = State() # ожидание ввода результата забега, ввод времени
    get_saved_plan_in_file = State() # ожидание получения сохраненного плана в файл
    select_result = State() # выбор результата для расчета нового плана
    get_new_paces = State() # получение новых темпов для тренировок
    make_week_completed = State() # отметить план на неделю выполненным
