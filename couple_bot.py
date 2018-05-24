import logging
import asyncio
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor, exceptions
from aiogram.types import ContentType, Message, CallbackQuery, ParseMode
from aiogram.utils.emoji import demojize
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

import config
import keyboards as kb
from gameplay import Player, Keyboard, Game
from utils import States
from messages import MESSAGES


logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.DEBUG)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
game = Game()
player = Player()
keyboard = Keyboard()


async def is_valid_game_callback(callback):
    if not callback.data or not callback.data.startswith('emj'):
        return False
    if keyboard.cell_is_open(callback.from_user.id, callback.data):
        await bot.answer_callback_query(callback.id, 'Уже открыта')
        return False
    return True


async def finish_game_msg(player_id):
    rating = player.get_rating(player_id)
    if player.is_new_record(player_id):
        player.add_new_record(player_id)
        await bot.send_message(player_id, MESSAGES['finish_success_msg'].format(
            count_try=game.get_count_try(player_id),
            rating=rating
        ), reply_markup=kb.finish)
    else:
        await bot.send_message(player_id, MESSAGES['finish_fail_msg'].format(
            count_try=game.get_count_try(player_id),
            rating=rating,
            top_rating=player.get_player_record(player_id)
        ), reply_markup=kb.finish)

    state = dp.current_state(user=player_id)
    await state.set_state(States.GAME_RU_FINISH[0])


def get_table(players):
    table_str = '{:^3}| {:<6}| {:^20}\n'.format('№', 'Очки', 'Имя игрока')
    position = 0
    last_rating = 0
    for player_info in players:
        if last_rating != player_info[1]:
            position += 1
        if len(player_info) == 3:
            table_str += '....\n'
            position = player_info[2]
        table_str += '{:<3} | {:>6} | {:<20} \n'.format(position, player_info[1], player_info[0])
        last_rating = player_info[1]
    return table_str


@dp.message_handler(state='*', commands=['start'])
async def process_start_command(message: Message):
    player_id = message.from_user.id
    if player.is_new_player(player_id):
        user_nick = message.from_user.username or message.from_user.first_name
        player.add_player(player_id, user_nick.capitalize())
    await message.reply(
        MESSAGES['start_answer'].format(nickname=player.get_player(player_id).nickname),
        reply_markup=kb.main,
        reply=False
    )


@dp.message_handler(state='*', commands=['help'])
async def process_help_command(message: Message):
    await message.reply(MESSAGES['help'], reply_markup=kb.main, reply=False)


@dp.message_handler(state='*', commands=['change_nickname'])
async def process_change_nickname_command(message: Message):
    await message.reply(
        MESSAGES['change_nickname'],
        reply=False
    )
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.RU_CHANGE_NICKNAME[0])


@dp.message_handler(state='*', commands=['clear_results'])
async def process_clear_result_command(message: Message):
    await message.reply(
        MESSAGES['clear_results'],
        reply_markup=kb.clear_result,
        reply=False
    )


@dp.message_handler(state='*', commands=['developer'])
async def process_developer_command(message: Message):
    await message.reply(
        'Принимаю пожелания/жалобы/предложения в ЛС @cashncarry',
        reply=False
    )


@dp.message_handler(
    state='*',
    func=lambda msg: demojize(msg.text) == ':exclamation_question_mark: FAQ'
)
@dp.message_handler(state='*', commands=['faq'])
async def process_faq_command(message: Message):
    await message.reply(
        MESSAGES['faq_msg'],
        reply_markup=kb.main,
        reply=False,
        parse_mode=ParseMode.MARKDOWN
    )


@dp.message_handler(
    state='*',
    func=lambda msg: demojize(msg.text) == ':chequered_flag: Играть :chequered_flag:'
)
@dp.message_handler(state='*', commands=['change_level'])
async def process_change_level_command(message: Message):
    await  message.reply(
        MESSAGES['choice_level'].format(
            easy=player.get_level_record('top_easy_rating'),
            normal=player.get_level_record('top_normal_rating'),
            hard=player.get_level_record('top_hard_rating')
        ),
        reply_markup=kb.level,
        reply=False
    )


@dp.message_handler(state='*', func=lambda message: demojize(message.text) in config.levels.keys())
async def start_new_game(message: Message):
    player_id = message.from_user.id
    level = config.levels[demojize(message.text)]
    keyboard.create_kb(player_id, level)
    game.new_game(player_id)
    await bot.send_message(
        player_id,
        MESSAGES['game_board_msg'],
        reply_markup=keyboard.get_kb(player_id)
    )
    state = dp.current_state(user=player_id)
    await state.set_state(States.GAME_RU_ON[0])


@dp.message_handler(state=States.RU_CHANGE_NICKNAME)
async def confirmation_nickname(message: Message):
    player_id = message.from_user.id
    new_nickname = message.text
    if game.has_nickname(new_nickname):
        await bot.send_message(player_id, 'Никнейм занят, попробуй другой')
    elif len(new_nickname) > 32:
        await bot.send_message(player_id, 'Длинный никнейм, попробуй другой')
    elif len(new_nickname) < 3:
        await bot.send_message(player_id, 'Короткий никнейм, минимум 3 символа')
    else:
        await bot.send_message(
            message.from_user.id,
            MESSAGES['confirm_nickname'].format(nickname=new_nickname),
            reply_markup=kb.change_nickname
        )


@dp.message_handler(
    state='*',
    func=lambda msg: demojize(msg.text) == ':bar_chart: Статистика'
)
async def process_statistic_btn(message: Message):
    player_info = player.get_player(message.from_user.id)
    player_number, player_score, player_nickname = player.get_player_in_table(player_info.id)
    await bot.send_message(player_info.id, MESSAGES['player_stat'].format(
        nickname=player_nickname,
        easy=player_info.top_easy_rating,
        normal=player_info.top_normal_rating,
        hard=player_info.top_hard_rating,
        number=player_number,
        score=player_score
    ), reply_markup=kb.main)


@dp.message_handler(
    state='*',
    func=lambda msg: demojize(msg.text) == ':trophy: Рейтинги :trophy:'
)
async def process_rating_btn(message: Message):
    top_players = game.get_top_players(message.from_user.id)
    await bot.send_message(message.from_user.id, get_table(top_players), reply_markup=kb.main)


@dp.message_handler(
    state='*',
    func=lambda msg: demojize(msg.text) == ':construction: Настройки'
)
async def process_configuration_menu(message: Message):
    await bot.send_message(message.from_user.id, MESSAGES['configuration'], reply_markup=kb.main)


@dp.message_handler(state='*')
async def unknown_message(message: Message):
    await bot.send_message(message.from_user.id, MESSAGES['unknown_msg'], reply_markup=kb.main)


@dp.message_handler(state='*', content_types=ContentType.ANY)
async def unknown_type_message(message: Message):
    await message.reply(MESSAGES['unknown_type_msg'])


@dp.callback_query_handler(state=States.GAME_RU_ON, func=is_valid_game_callback)
async def process_callback_btn(callback_query: CallbackQuery):
    state = dp.current_state(user=callback_query.from_user.id)

    keyboard.show_cell(callback_query.from_user.id, callback_query.data)
    game.add_try(callback_query.from_user.id)
    await bot.edit_message_reply_markup(
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=keyboard.get_kb(callback_query.from_user.id)
    )

    if not game.has_open_cell(callback_query.from_user.id):
        game.add_open_cell(callback_query.from_user.id, callback_query.data)
    elif game.have_couple(callback_query.from_user.id, callback_query.data):
        await state.set_state(States.GAME_RU_PAUSED[0])
        game.del_open_cell(callback_query.from_user.id)
        if game.is_finish(callback_query.from_user.id):
            return await finish_game_msg(callback_query.from_user.id)
    else:
        await state.set_state(States.GAME_RU_PAUSED[0])
        await asyncio.sleep(0.8)
        keyboard.hide_cells(callback_query.from_user.id, callback_query.data)
        game.del_open_cell(callback_query.from_user.id)
        await bot.edit_message_reply_markup(
            callback_query.from_user.id,
            callback_query.message.message_id,
            reply_markup=keyboard.get_kb(callback_query.from_user.id)
        )

    await state.set_state(States.GAME_RU_ON[0])


@dp.callback_query_handler(state=States.GAME_RU_PAUSED, func=lambda c: c.data and c.data.startswith('emj'))
async def process_game_paused(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Не спеши')


@dp.callback_query_handler(state='*', func=lambda c: c.data and c.data.startswith('emj'))
async def process_game_finished(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Игра окончена, начни новую')


@dp.callback_query_handler(
    state=States.GAME_RU_ON | States.GAME_RU_PAUSED,
    func=lambda c: c.data and c.data == 'restart'
)
async def process_restart_in_game(callback_query: CallbackQuery):
    keyboard.create_kb(callback_query.from_user.id, player.get_level(callback_query.from_user.id))
    game.new_game(callback_query.from_user.id)
    try:
        await bot.edit_message_reply_markup(
            callback_query.from_user.id,
            callback_query.message.message_id,
            reply_markup=keyboard.get_kb(callback_query.from_user.id)
        )
    except exceptions.MessageNotModified:
        await bot.answer_callback_query(callback_query.id, 'Новая игра')


@dp.callback_query_handler(state='*', func=lambda c: c.data and c.data == 'restart')
async def process_start_new_game(callback_query: CallbackQuery):
    keyboard.create_kb(callback_query.from_user.id, player.get_level(callback_query.from_user.id))
    game.new_game(callback_query.from_user.id)
    await bot.send_message(
        callback_query.from_user.id,
        'Найди одинаковые emojii\nИзменить уровень - /change_level',
        reply_markup=keyboard.get_kb(callback_query.from_user.id)
    )

    state = dp.current_state(user=callback_query.from_user.id)
    await state.set_state(States.GAME_RU_ON[0])


@dp.callback_query_handler(state='*', func=lambda c: c.data and c.data == 'counter')
async def process_game_paused(callback_query: CallbackQuery):
    return await bot.answer_callback_query(callback_query.id, 'Колличество попыток')


@dp.callback_query_handler(state='*', func=lambda c: c.data == 'menu')
async def process_menu_btn(callback_query: CallbackQuery):
    state = dp.current_state(user=callback_query.from_user.id)
    player_number, player_score, player_nickname = player.get_player_in_table(
        callback_query.from_user.id
    )
    await state.set_state(States.MENU_RU[0])
    await bot.send_message(callback_query.from_user.id, MESSAGES['rating'].format(
        number=player_number,
        nickname=player_nickname,
        score=player_score
    ), reply_markup=kb.main)


@dp.callback_query_handler(state=States.RU_CHANGE_NICKNAME, func=lambda c: c.data == 'changed_nickname')
async def process_change_nickname(callback_query: CallbackQuery):
    new_nickname = callback_query.message.text[15:-3]
    player.change_nickname(callback_query.from_user.id, new_nickname)
    await bot.send_message(
        callback_query.from_user.id,
        MESSAGES['accept_nickname'].format(nickname=new_nickname),
        reply_markup=kb.main
    )
    state = dp.current_state(user=callback_query.from_user.id)
    await state.set_state(States.MENU_RU[0])


@dp.callback_query_handler(state=States.RU_CHANGE_NICKNAME, func=lambda c: c.data == 'edit_nickname')
async def process_edit_nickname(callback_query: CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Новый ник:')


@dp.callback_query_handler(state=States.RU_CHANGE_NICKNAME, func=lambda c: c.data == 'cancel_change_nickname')
async def process_cancel_change_nickname(callback_query: CallbackQuery):
    player_id = callback_query.from_user.id
    await bot.send_message(
        player_id,
        'Ник не изменился',
        reply_markup=kb.main
    )
    state = dp.current_state(user=player_id)
    await state.set_state(States.MENU_RU[0])


@dp.callback_query_handler(state='*', func=lambda c: c.data == 'clear_result')
async def process_clear_result(callback_query: CallbackQuery):
    player_id = callback_query.from_user.id
    player.clear_player_records(player_id)
    await bot.send_message(player_id, 'Результаты обнулены', reply_markup=kb.main)


@dp.callback_query_handler(state='*', func=lambda c: c.data == 'cancel_clear')
async def process_cancel_clear_result(callback_query: CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Отменил', reply_markup=kb.main)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)
