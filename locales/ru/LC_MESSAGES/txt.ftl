hello-user = Привет, { $username }. Я бот, который поможет
             тебе готовится к забегам. Если у тебя есть
             результат твоего забега или тренировки, то
             я определю твой примерный уровень МПК и
             рассчитаю план тренировок. Если готов
             начать - /fillform

help_-user = Список моих команд:
             /fillform - начать заполнять анкету'
             /cancel - отмена
             /showdata -  посмотреть внесенные данные
             /calculate - рассчитать план
             /get_my_plans -  выводит список сохраненных планов
             /add_new_race_result -  добавить новые результаты забегов
             /get_next_week_plan - показать план на следующую неделю
                                   Если у тебя есть активный план
             /plan_my_race - поможет спланировать гонку или тренировку
                            если ты хочешь пробежать дистанцию за опре-
                            деленное время.


help_-auth-user = { help_-user }
                   Посмотреть свой профиль и изменить данные:
                   - /show_my_profile
                   Получить комплексы функциональных тренировок -
                   /get_fttrain
                   Получить комплекс тренировки на развитие беговых
                   навыков -  /get_runskillstrain


help_-admin = { help_-auth-user }
             /get_my_users


cancel_-in_-fsm_ = Отмена расчета. 🤷


cancel_ = Отмена. Я вроде ничего не рассчитывал. 🤷


messageoutFSM = А я вроде ничего не рассчитывал.
                 Начать расчет, отправьте - /fillform


unidentifiedcallback = Если вы видете это сообщение, значит вы нажали
                       кнопку из старого сообщения! Или что-то пошло
                       не так! 🤷


fill-form = Пожалуйста, введите ваше имя


name_-sent = Спасибо, { $name }!
            А теперь введите ваш возраст


wrong-name_ = Вы отправили { $name }. Это не похоже на имя.
             Пожалуйста, введите ваше имя. Имя должно
             начинаться с заглавной буквы и состоять
             из букв русского или латинского алфавита.
             Если вы хотите прервать заполнение анкеты -
             отправьте команду /cancel


fill-age = Спасибо! Укажите ваш пол


male = Мужской ♂


female = Женский ♀


age-sent = Спасибо!
           Укажите ваш пол


wrong-age = Калькулятор рассчитан на возраст от 16 до 90
                Если ваш возраст отличается от указанного
                то вы можете прервать заполнение анкеты -
                отправьте команду /cancel


gender-pressed = Спасибо!
               <b>Ваш максимальный пульс, рассчитанный по формуле { $physiologist }</b>
               <b> { $maxpulse } ударов в мин.</b> .
               Теперь укажите ваш вес


wrong-gender = Я знаю только два пола: мужчина и женщина.
               Для выбора пола просто нажми одну из кнопок!


fill-weight = Спасибо! Введите рост.


wrong-weight = Калькулятор рассчитан на вес от 35 до 150 кг
               Если ваш вес отличается от указанного, то вы
               можете прервать заполнение анкеты - отправьте
               команду /cancel


fill-height = Спасибо! Теперь отправьте фото. С фотографией
              ваш аккаунт будет выглядеть симпатичнее. ))


wrong-height = Калькулятор рассчитан на рост от 135 до 250 см
               Если ваш рост отличается от указанного,то вы можете прервать
               заполнение анкеты - отправьте команду /cancel


photo_-sent = Спасибо! Чтобы посмотреть ваши данные
              отправьте /showdata


showpulse =
            Максимальный пульс: { $maxpulse }
            {"   "}
            <b>Пульсовые зоны:</b>
            1-я зона - { $beg1 } - { $end1 }
            2-я зона - { $beg2 } - { $end2 }
            3-я зона - { $beg3 } - { $end3 }
            4-я зона - { $beg4 } - { $end4 }
            5-я зона - { $beg5 } - { $end5 }


show_-data_ =
            Имя: { $user_name }
            Возраст: { $user_age }
            Пол: { $user_gender }
            Вес: { $weight }
            Рост: { $height }
            Индекс массы тела: { $imt }
            {"   "}
            { $pulsezones }
            { $case ->
            [1] Чтобы сохранить данные отправьте:
               /save_data
            *[0] /change_profile
            }


save_-data_ =   Данные сохранены. Вы можете приступать к расчету плана.
                Расчет плана будет состоять из следующих задач:
                1. Получение информации о забегах.
                2. Выбор целевой дистанции, к которой предстоит подготовится
                3. Расчет плана подготовки.
                { " " }
              Для того, чтобы ввести информацию о забеге введите:
              /add_new_race_result
              <b>Важно!</b>
              Оптимальной для рассчета является дистанция 5 км и более.
              Но если вы никогда не бегали такие длинные дистанции, то
              выберите дистанцию, за которую у вас есть результат.
              План можно скорректировать после второй тренировки.
              { " " }
              <b>Отправьте /add_new_race_result</b>

## Messages to hundlers for selecting distance to add raceresult
choose_-dist = Выберете дистанцию, которую бежали на результат.


distancebuttonskeys = {$racedist ->

                      [m1500] 1,5 км
                      [mile] 1 миля
                      [m3000] 3 км
                      [miles2] 2 мили
                      *[km5] 5 км
                      [km10] 10 км
                      [km15] 15 км
                      [hmph] 21.1 км
                      [mph] 42.2 км
                    }

select_-dist = { $dist } км

## Messages for hundlers when user selects dictance to add race result
select_-distances = Спасибо! Вы выбрали дистанцию { $dist }.
                   Введите время в формате - 01:21:15 или
                   просто 6 цифр без разделителя - 012115.

wrong-dist = Вы ввели { $val }. Это не похоже ни на одну дистанцию,
             которую я ожидаю.
             Пожалуйста, выберите одну из дистанций на кнопке.

## Messages for hundlers when racetime sent
wrong-time_ = Время должно быть введено в формате 01:21:15
              или 01h21m15s или 012115. Часы должны быть не
              болee 24. Минуты и секунды не больше 60.
              Вы ввели { $res }!


restime-sent = Спасибо!
               {"  "}
               Ваш МПК (расчетный) - { $vdot }
               {"  "}
               <b>Вы могли бы пробежать:</b>
               🔸 10 км за { $tenk }
               🔸 Полумарафон за { $hmp }
               🔸 Марафон за { $mp }
               {"   "}
               Чтобы перейти к рассчету плана
               введите /calculate


## Message for command calculate
ups = Что-то пошло не так. Попробуйте повторить чуть позже.

yetnonhave-reports = У вас пока нет ни одного результата забега.
                     Чтобы добавить отправьте /add_new_race_result


confirmresult =
    { $countresults ->
    [one] <b>Найден один результат забега.</b>
    [few] <b>Найдены { $countresults } результата забега. Недавний забег</b>
    [many] <b>Найдены { $countresults } результатов забега. Недавний забег</b>
    *[other]<b> У вас { $countresults } забегов. Недавний забег</b>
    }
      <b>на <i>{ $dist }</i> с результатом <i>{ $result }</i></b>
     {"   "}
     Хотите рассчитать план на основе этого забега?
     {"   "}


yes-no-buttons = { $butt ->
                *[yes] Да!
                [no] Нет. Выберу другой!
                }

paces-count = { $selectvar ->
                *[one]
                <b> Тренировочные темпы для разных дистанций: </b>
                {" "}
               <u>Темпы на интервальные тренировки:</u>
                 🔸  400 м - { $m400 }
                 🔸  600 м - { $m600 }
                 🔸  800 м - { $m800 }
                 🔸 1000 м - { $m1000 }
                 🔸 1200 м - { $m1200 }
                 🔸 1600 м - { $m1600 }
                 {" "}
                <u>Темпы на темповые тренировки:</u>
                 🔸 темп на короткие - { $ST }
                 🔸 темп на средние  - { $MT }
                 🔸 темп на длинные - { $LT }
                 {" "}
                <u>Темп на полумарафон и марафон:</u>
                 🔸 темп на полумарафон - { $HMP }
                 🔸 темп марафон - { $MP }
                 [0] У тебя очень высокий уровень МПК { $vdot }.
                 Мои алгоритмы рассчитаные на любителей с более
                 низким уровнем подготовки.
                 }

raceview = дата { $racedate } дистанция { select_-dist} время { $racetime }

selectother = Выберете результат для расчета:


distances = { $dist ->
           *[K10] 5 -10 километров
           [K21] Полумарафон
           [FMP] Мой первый марафон
           [MP] Марафон
            }


first-train = { $selectvar ->
                *[1] 🔸 🏃‍♂️ { $count } раз по { $dist } в темпе - { $pace } за { $inttime }.
                [2] 🚶 Отдых { $rest } между интервалами.

                }
second-train = { $selectvar ->
                *[1]🔸 ‍🏃‍ { $dist } K в темпе { $pace } за { $inttime }.
                [2] 🚶 { $dist } K в темпе { $pace }.
                }

third-train = { $selectvar ->
                *[1]🔸 🏃‍ { $dist } K в темпе { $pace } за { $inttime }.
                [2]🔸 🏃‍ { $dist } K {$pace}.
                }


raceplanformatting = <b> План подготовки на { $dist }: </b>
                        {"  "}
                        <u>{ $week } недель до старта. </u>
                        {"  "}
                        <u><i>1-я тренировка - интервальная:</i></u>
                        {"  "}
                        <i>Важно, чтобы время на одинаковых интервалах не</i>
                        <i>отличалось более, чем на несколько секунд.</i>
                        <i>Выполняется в 4-ой, а для бегунов со стажем 5-й</i>
                        <i>пульсовых зонах</i>
                        Интервалы:
                        { $firsttrain}
                        {"  "}
                        <u><i>2-я тренировка - темповая:</i></u>
                        {"  "}
                        <i>Важно, держать заданный темп.</i>
                        <i>Тренировка выполняется на ПАНО.</i>
                        { $secondtrain}
                        {"  "}
                        <u><i>3-я тренировка - длительная:</i></u>
                        {"  "}
                        <i>Длительную тренирувку можно выполнять</i>
                        <i>без дополнительной разминки. Бежать в</i>
                        <i>развивающем темпе. Начинать чуть медленнее</i>
                        <i>целевого темпа, а окончание забега в темпе</i>
                        <i>выше целевого. Тренировка выполняется во </i>
                        <i>2-й пульсовой зоне.</i>
                        { $thirdtrain}
                        {"  "}
                        { $additiontext}

commands_-name =
    { $case ->
       *[1] Сохранить план отправьте - /save_plan
        [2] Сделать план активным отправьте - /make_plan_active
                   Удалить план отправьте - /delete_plan
                   Показать пульсовые зоны - /show_my_pulse_zones
        [3]
        Внести результаты тренировки - /enter_trainresults
        Отметить план на неделю выполненным - /make_week_completed
    }
    Выйти из просмотра плана - /cancel


saveplan-result = { $case ->
        *[1] План успешно сохранен! Чтобы начать тренировки, сделайте план
        активным из меню просмотра планов.
        [2] У вас уже есть такой план от { $plandate }
        Вы можете сделать его активным.
        }
        Введите команду просмотра планов - /get_my_plans


planbottons = { $case ->
              *[0] { $plandate } { $dist }
              [active] { $plandate } { $dist } 🏃‍♂️ активный
              [compleeted] { $plandate } { $dist } ✅ выполнен
              }


getsavedplans = { $case ->
                *[1] <b>Планы тренировок:</b>
                Чтобы просмотреть план нажмите на кнопку с планом.
                Чтобы выйти из режима просмотра списка планов - /cancel
                [0] У вас нет пока ни одного плана.
                }


makeplanactive = { $case ->
                *[1] Успешно! Теперь вы можете приступить к выполнению.
                [2] У вас уже есть один активный план
                   подготовки к { $dist } от { $dataplan }
                   }


deleteplan = { $case ->
            *[1] План { $plan } успешно удален.
            [0] Что-то пошло не так. Попробуйте
            повторить попытку позже.
            }


makeweekcompleted = { $case ->
                    *[1] Неделя { $week } плана { $plan } выполнена.
                    [2] Неделя { $week } и план { $plan } выполнены.
                    }


changeprofile = { $case ->
        *[0] <b>Выберете значение,которое хотите поменять:</b>
        [age] Возраст
        [gender] Пол
        [weight] Вес
        [height] Рост
        [res_distances] Дистанция
        [result] Результат
        [IMT] Индекс массы тела
        [max_pulse] Максимальный пульс
        [photo] Фотографию
        }


waitdata = { $case ->
           *[0] Введите значение:
           [1] Спасибо. Хотите изменить еще значение?
               Выберете показатель для замены или
               отправьте - /save_profile , чтобы сохранить изменения
           [2] Вы изменили все возможные данные.
           Отправьте - /save_profile , чтобы сохранить изменения
           [3] Данные сохранены. Чтобы проверить профиль -
           /showdata
           }


planmyrace = { $case ->
               *[0] Укажите дистанцию.
                 Например, 21.1 - 21 км. 100 м.

               [1] Дистанция { $km } км { $metr } м.
                Введите планируемое время - 6 цифр без разделителя.
                Например, 010555 - 1 час 5 мин 55 сек.

               [2]<b>План на { $km } км { $metr } м.</b>
               {"  "}
               }


getmyusers = { $case ->
            *[0] <b>Твои пользователи:</b>
            {"  "}
            [1] Имя: <i>{ $usersname }</i> возраст: <i>{ $age }</i> количество планов: <i>{ $plans}</i>.
             }


# user have no plan
getnextweekplan = У тебя еще нет активного плана. Выбери план
                  и сделай его активным:
                  /get_my_plans


# waiting for command or callback data
notgetit = { $data }
           Не понял вас. Вероятно я жду ответ на
           предыдущее сообщение. Команду или
           нажатие кнопки.
           Отправьте /cancel если ничего не
           помогает.


fttrain = { $complex ->
           *[0] 3-5 кругов:
           🔸 10 отжиманий
           🔸 10 запрыгиваний на коробку
           🔸 10 махов гирей 12 кг
           🔸 10 пресс склепка
           🔸 10 лодочка(спина)

           [1] 3-5 кругов:
           🔸 20 берпи
           🔸 20 пресс
           🔸 20 Джек
           🔸 20 приседаний
           🔸 20 скалолаз

           [2] 3-5 кругов:
           🔸 Пресс 20
           🔸 Мяч вверх 10
           🔸 Махи гирей 20
           🔸 Пррисед с мячом 10
           🔸 Скручивания на косые 20
           🔸 Бицепс плечи 10
           🔸 Мяч прыжки 20
           🔸 Гиря перекаты 10

           [3] 3-5 кругов:
           🔸 Скакалка 100 раз
           🔸 Приседаниями 20 раз
           🔸 Скакалка 100 раз
           🔸 Отжимания 20 раз
           🔸 Джек 100 раз
           🔸 Берпи 20 раз

           [4] 3-5 кругов:
           🔸 Скакалка 100
           🔸 Пресс скручивания 20
           🔸 Скалолаз 20
           🔸 Приседания 20
           🔸 Скакалка 50 раз в быстром темпе

           [5] 3-5 кругов:
           🔸 Приседания 20
           🔸 Cкаклолаз 20
           🔸 Мяч в стену 20
           🔸 Пресс 20

           [6] 3-5 кругов:
           🔸 20 Скалолаз
           🔸 20 пресс
           🔸 20 присед с выприг
           🔸 20 броски мяча в стену

           [7] 3-5 кругов:
           🔸 Джек 20
           🔸 Берпи 10
           🔸 Броски мяча 20
           🔸 Отжимания 10
           🔸 Скакалка 100

           [8] 3-5 кругов:
           🔸 Берпи 10
           🔸 Запрыгиыания 10
           🔸 Отжимания от коробки 10

           [9] 3-5 кругов:
           🔸 10 отжиманий
           🔸 10 Разножки
           🔸 Берпи 10
           🔸 Пресс 30
           }


runskillstrain = Тренировка проводится на стадионе или на дорожке
                 длинной 25-100 метров. Длина дорожки и
                 количество повторов выбирается в зависимости от
                 уровня подготовки.
                {"  "}
                <b>Тренировка по бегу:</b>
             🔸 Бег с высоким подниманием бедра
             🔸 Бег с захлестом голени
             🔸 Бег велосипед (как будто прокручиваем педали велосипеда)
             🔸 Олений бег
             🔸 Бег с поочередным выбрасываем ноги и колена. Выполняется поочередно:
             одна дорожка на одной ноге, другая на другой.
             🔸 Выпригивания из присяда вперед (Лягушка)
             🔸 Прыжки с одной ноги на другую. Встать на одну ногу, прыгнуть в длину
             на максимальное расстояние, приземлиться на другую ногу.
             {"  "}
             <b>Круговая тренировка.</b>
             <i>Можно выполнять по времени или по количеству повторений.</i>
             <i>Например, по 30 сек. с отдыхом 1 мин. между кругами.</i>
             <i> 3- 5 кругов</i>
             🔸 Разножка (Выпрыгивания из выпада в выпад)
             🔸 На скамейке выталкивание с ноги на ногу
             🔸 Выпрыгивание из приседа (воздушные приседания)
             🔸 Махи согнутой в колене ногой из положения выпада
             🔸 Скалолаз с упором о стенку
             {"  "}
             <b>Планки.</b>
             🔸 Планка боковая (можно в положении звезда) ~ по 30 сек. на каждой стороне
             🔸 Планка с упором на локти или руки с поочередным подниманием ног ~ 2 мин.


trainresultsbuttons = { $button ->
                      *[train1] 1-я тренировка
                       [train2] 2-я тренировка
                       [train3] 3-я тренировка
                       }


entertrainresults = { $case ->
                    *[0] Выберите тренировку
                     [1] Вы отметили все тренировки.
                     Завершить неделю - отправьте - /make_week_completed

                    }


selecttrainresults = Выбери дистанцию для внесения результата


addtrainresults = { $case ->
                   *[0] <b> Введите результат для дистанции { $dist } км. </b>
                    <i> Формат ввода - шесть цифр без разделителей. Например, </i>
                    <i>если вы предолели дистанцию 10 км за 1 час 2 минуты, 35 </i>
                    <i>секунд, введите 010235 - шесть цифр без разделителей.</i>
                    [1] <b> Введите лучший и худший результаты на интервале { $dist } км.</b>
                    <i>Формат ввода - два раза по шесть цифр с разделителем пробел. </i>
                    <i>Например, если вы бежали 10 раз по 400 метров, и ваш лучший результат </i>
                    <i>был 2 минуты 10 секунд, а худщий 2 минуты 18 секунд, то введите </i>
                    <i>000210 000218 - два раза по шесть цифр с разделителем пробел между </i>
                    <i>значениями. </i>
                    }

distance-measure = { $case ->
                [metr] метров
                *[km]  {" "}км
                }


waittrainresults = { $case ->
                    *[0] Успешно! Выбери дистанцию для внесения результата.
                    [1] Успешно! Для сохранения
                     внесенных данных - /save_trainresults.
                    }


savetrainresult = Успешно! Данные сохранены
                {" "}


showresults = Ваши результаты за дистанцию { $dist }
              Целевое время { $goal }. Фактическое время { $fact } + { $diff }
              { $case ->
              *[0] Тренировка завершена успешно!
              [1] Получится следующий раз!
              }
              {" "}