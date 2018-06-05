from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.emoji import emojize


def get_game_kb(width_row, cards, player_try):
    keyboard = InlineKeyboardMarkup(row_width=width_row)
    count_btn = InlineKeyboardButton(emojize(f':stopwatch: {player_try}'), callback_data='counter')
    for index, emoji in enumerate(cards):
        keyboard.insert(InlineKeyboardButton(emojize(emoji), callback_data='emj{}'.format(index)))

    keyboard.insert(count_btn)
    keyboard.insert(InlineKeyboardButton(emojize('Заново :repeat:'), callback_data='restart'))
    keyboard.insert(InlineKeyboardButton(emojize('Выйти :arrow_right:'), callback_data='menu'))
    return keyboard


def get_main_kb():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(KeyboardButton(
        emojize(':chequered_flag: Играть :chequered_flag:')
    ))
    keyboard.row(KeyboardButton(emojize(':trophy: Рейтинги :trophy:')))
    keyboard.row(
        KeyboardButton(emojize(':bar_chart: Статистика')),
        KeyboardButton(emojize(':interrobang: FAQ')),
        KeyboardButton(emojize(':construction: Настройки'))
    )
    return keyboard


main = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(KeyboardButton(
        emojize(':chequered_flag: Играть :chequered_flag:')
    ))
main.row(KeyboardButton(emojize(':trophy: Рейтинги :trophy:')))
main.row(
    KeyboardButton(emojize(':bar_chart: Статистика')),
    KeyboardButton(emojize(':interrobang: FAQ')),
    KeyboardButton(emojize(':construction: Настройки'))
)
level = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(
    KeyboardButton(emojize('Простой :chicken:')),
    KeyboardButton(emojize('Средний :monkey:')),
    KeyboardButton(emojize('Сложный :person_lifting_weights:')),
)
finish = InlineKeyboardMarkup()\
    .add(InlineKeyboardButton(emojize('Заново :repeat:'), callback_data='restart'))\
    .add(InlineKeyboardButton(emojize('В меню :arrow_right:'), callback_data='menu'))
change_nickname = InlineKeyboardMarkup().row(
    InlineKeyboardButton(emojize('Верно :heavy_check_mark:'), callback_data='changed_nickname'),
    InlineKeyboardButton(emojize('Изменить :pencil2:'), callback_data='edit_nickname'),
    InlineKeyboardButton(emojize('Отенить :arrow_right:'), callback_data='cancel_change_nickname')
)
clear_result = InlineKeyboardMarkup().row(
    InlineKeyboardButton(emojize('Обнулить :heavy_check_mark:'), callback_data='clear_result'),
    InlineKeyboardButton(emojize('Отменить :arrow_right:'), callback_data='cancel_clear')
)
