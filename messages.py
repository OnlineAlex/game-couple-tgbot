from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import text, bold, italic


start_msg = emojize(
    'Привет, {nickname}!\nГотов проверить себя?\nЖми :checkered_flag: Играть :checkered_flag: :point_down:'
)
help_msg = 'Доступные команды:\n/start - начало работы с ботом\n' \
           '/change_level - Изменить уровень игры\n/change_nickname - Изменить ник в игре\n' \
           '/clear_results - обнулить свои результаты\n/FAQ - ответы на вопросы по игре\n' \
           '/developer - написать разработчику\n\nТак же можно использовать клавиатуру:\n' \
           'Играть — новая игра\nРейтинги — турнирная таблица\n' \
           'Статистика — статистика игрока\nНастройки — изменить личные данне'
change_nickname = emojize(':pencil2: Напиши новый никнейм. Допускается 3-32 символа, пробелы и emodji')
confirm_nickname = emojize('Твой новый ник {nickname}? :open_mouth:')
accept_nickname = emojize('Готово! Теперь буду называть тебя {nickname} :wink:')
clear_results = emojize('Обнулить результаты:interrobang: Все достижения пропадут :bangbang:')
unknown_msg = emojize(':dizzy_face: Я не готов к этому сообщению.\n'
                      'Если это очень важно напиши разработчику — /develover\n'
                      'А лучше давай поиграем :point_down:'
                      )
unknown_type_msg = emojize('Я не знаю, что с этим делать :astonished:\n'
                           'Я просто напомню, что есть команда /help')
faq_msg = text(
    bold('Часто задаваемые вопросы\n'),
    bold('Как играть?'),
    italic('Смысл игры — найти одинаковые эмоджи.'
           'Открытие подряд 2 одинаковых эмоджи, приведет к их закреплению на игровом поле.'
           'Дальше можно искать другие одинаковые пары. '
           'Задача: запоминать открытые ячейки, что бы закончить игру с меньшим количеством кликов\n'),
    bold('Сколько максимально можно набрать рейтинга?'),
    italic('Теоретически — 600 очков. По 200 на каждом уровне\nДля этого нужно с первого раза угадать пары. '
           'Обьективно, обладая хорошей памятью, можно набрать по 100 очков на кождом уровне\n'),
    bold('Как рассчитывается рейтинг?'),
    italic('По специальной формуле. Если вы открыли все пары с первого раза получите 200 очков,'
           'если на каждую ячейку ушло по 2 клика — 100 очков\n'),
    bold('Как попасть в турнирную таблицу?'),
    italic('Вы попадаете в нее сразу. Что бы полноценно бороться за первое место, пройдите 3 уровня.\n'),
    bold('Что делать когда бот не реагирует на команды?'),
    italic('Попробуйте перезапустить бота. Если это не помогло, напишите разработчику ') + '/developer\n',
    sep='\n'
)
player_stat = emojize('{nickname}, твои результаты :muscle::\nПростой :chicken: — {easy}\n'
                      'Средний :monkey: — {normal}\nСложный :person_lifting_weights: — {hard}\n\n'
                      'В общем рейтинге :trophy::\n№ {number} {nickname} — {score}:black_small_square:'
                      )
configuration_msg = emojize(':gear::gear::gear:\n/clear_results - обнулить свои результаты\n'
                            '/change_nickname - Изменить ник в игре\n'
                            'Другие возможности можно посмотреть нажав /help'
                            )
rating_msg = emojize(':trophy: В общем рейтинге:\n№ {number} {nickname} — {score}:black_small_square:'
                     )
choice_level_msg = emojize(
    'Выбери уровень игры.\nРекорды уровней:\n'
    'Простой — :sports_medal: {easy}\n'
    'Средний — :sports_medal: {normal}\n'
    'Сложный — :sports_medal: {hard}'
)
game_board_msg = 'Найди одинаковые emojii\nИзменить уровень - /change_level'
finish_success_msg = emojize(':boom::tada::boom::tada::boom::tada:\nПоздравляю  с новым личнным рекордом\n'
                             'Кликов сделано — :stopwatch:{count_try}\n'
                             'Набрано очков — {rating}:black_small_square:\n'
                             'Другой уровень - /change_level'
                             )
finish_fail_msg = emojize(':sob::sob::sob: Это не лучший твой результат\n'
                          'Кликов сделано — :stopwatch: {count_try}\n'
                          'Набрано очков — {rating}:black_small_square:\n'
                          'Личный рекорд уровня — {top_rating}:black_small_square:')


MESSAGES = {
    'start_answer': start_msg,
    'help': help_msg,
    'change_nickname': change_nickname,
    'confirm_nickname': confirm_nickname,
    'accept_nickname': accept_nickname,
    'clear_results': clear_results,
    'unknown_msg': unknown_msg,
    'unknown_type_msg': unknown_type_msg,
    'faq_msg': faq_msg,
    'player_stat': player_stat,
    'configuration': configuration_msg,
    'rating': rating_msg,
    'choice_level': choice_level_msg,
    'game_board_msg': game_board_msg,
    'finish_success_msg': finish_success_msg,
    'finish_fail_msg': finish_fail_msg,
}
