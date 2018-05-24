import random
import math

import db_map as db
import keyboards
from config import top_ratings
from sqlalchemy import func, distinct


def get_random_cards(number_emj):
    emoji = [i for i in range(1, 19)]
    selected_emj = random.sample(emoji, number_emj // 2) * 2
    random.shuffle(selected_emj)
    return selected_emj


class Try(db.Session):
    def add_try(self, player_id):
        session = self._get_session
        session.query(db.Games.count_try).filter_by(id=player_id) \
            .update({db.Games.count_try: db.Games.count_try + 1})
        session.commit()

    def get_count_try(self, player_id):
        session = self._get_session
        count_try = session.query(db.Games).get(player_id).count_try
        session.close()
        return count_try


class OpenCell(db.Session):
    def has_open_cell(self, player_id):
        session = self._get_session
        player = session.query(db.Games).get(player_id)
        session.close()
        return bool(player.open_cell)

    def get_open_cell(self, player_id):
        session = self._get_session
        player = session.query(db.Games).get(player_id)
        session.close()
        return player.open_cell

    def add_open_cell(self, player_id, cell_data):
        session = self._get_session
        session.query(db.Games.open_cell).filter_by(id=player_id).update({db.Games.open_cell: cell_data})
        session.commit()

    def del_open_cell(self, player_id):
        session = self._get_session
        session.query(db.Games.open_cell).filter_by(id=player_id).update({db.Games.open_cell: None})
        session.commit()


class Level(db.Session):
    def get_level(self, player_id):
        session = self._get_session
        player_level = session.query(db.Players).get(player_id).level
        session.close()
        return player_level

    def get_level_record(self, level_name):
        session = self._get_session
        level_attr = getattr(db.Players, level_name)
        record = session.query(level_attr).order_by(level_attr.desc()).first()[0]
        session.close()
        return record


class Game(Level, Try, OpenCell):
    default_emj = 19

    def new_game(self, player_id):
        session = self._get_session
        player_game = session.query(db.Games).get(player_id)
        player_game.open_cell = None
        player_game.count_try = 0
        session.commit()

    def have_couple(self, player_id, btn_data):
        open_cell_data = self.get_open_cell(player_id)
        session = self._get_session
        buttons = session.query(db.Keyboards.btn_text).filter_by(player_id=player_id) \
            .filter(db.Keyboards.btn_data.in_([btn_data, open_cell_data])).all()
        session.close()
        return bool(buttons[0] == buttons[1])

    def is_finish(self, player_id):
        session = self._get_session
        hidden_cells = session.query(db.Keyboards.btn_text) \
            .filter_by(player_id=player_id, btn_text=self.default_emj).first()
        session.close()
        return not bool(hidden_cells)

    def get_player_in_table(self, player_id):
        session = self._get_session
        sum_ratings = db.Players.top_easy_rating + db.Players.top_normal_rating + db.Players.top_hard_rating
        player = session.query(db.Players).get(player_id)
        player_rating = player.top_easy_rating + player.top_normal_rating + player.top_hard_rating
        player_position = session.query(func.count(distinct(sum_ratings)) + 1) \
            .filter(sum_ratings > player_rating).scalar()
        session.close()
        return player_position, player_rating, player.nickname

    def get_top_players(self, player_id):
        session = self._get_session
        sum_ratings = db.Players.top_easy_rating + db.Players.top_normal_rating + db.Players.top_hard_rating
        top_players = session.query(db.Players.nickname, func.round(sum_ratings, 2))\
            .order_by(sum_ratings.desc()).limit(10).all()
        player_number, player_score, player_nickname = self.get_player_in_table(player_id)
        if (player_nickname, player_score) not in top_players:
            position_player = session.query(func.count(distinct(sum_ratings)) + 1) \
                .filter(sum_ratings > player_score).scalar()
            top_players.append((player_nickname, player_score, position_player))
        session.close()
        return top_players

    def has_nickname(self, nickname):
        session = self._get_session
        db_nickname = session.query(db.Players.nickname)\
            .filter(func.lower(db.Players.nickname) == func.lower(nickname)).first()
        session.close()
        return bool(db_nickname)


class Keyboard(Game):
    def create_kb(self, player_id, level):
        session = self._get_session
        player = session.query(db.Players).get(player_id)
        player.level = level
        session.query(db.Keyboards).filter_by(player_id=player_id).delete()
        random_cards = get_random_cards(player.level)
        for i in range(player.level):
            player.button.append(db.Keyboards(btn_data=f'emj{i}', btn_text=19, hidden_text=random_cards[i]))

        session.add_all(player.button)
        session.commit()

    def get_kb(self, player_id):
        session = self._get_session
        game_cards = session.query(db.Emoji.emoji, db.Keyboards.btn_data) \
            .join(db.Keyboards, db.Emoji.id == db.Keyboards.btn_text).filter_by(player_id=player_id).order_by(db.Keyboards.id).all()
        level = session.query(db.Players).get(player_id).level
        num_columns = round(math.sqrt(level))
        count_try = session.query(db.Games.count_try).filter_by(id=player_id).scalar()
        kb = keyboards.get_game_kb(num_columns, game_cards, count_try)
        session.close()
        return kb

    def cell_is_open(self, player_id, btn_data):
        session = self._get_session
        buttons = session.query(db.Keyboards.btn_text, db.Keyboards.hidden_text) \
            .filter_by(player_id=player_id, btn_data=btn_data).first()
        session.close()
        return bool(buttons[0] == buttons[1])

    def show_cell(self, player_id, btn_data):
        session = self._get_session
        session.query(db.Keyboards.btn_text) \
            .filter_by(player_id=player_id, btn_data=btn_data) \
            .update({db.Keyboards.btn_text: db.Keyboards.hidden_text})
        session.commit()

    def hide_cells(self, player_id, btn_data):
        session = self._get_session
        session.query(db.Keyboards.btn_text) \
            .filter_by(player_id=player_id, btn_data=btn_data) \
            .update({db.Keyboards.btn_text: Game.default_emj})
        open_btn_data = session.query(db.Games).get(player_id).open_cell
        session.query(db.Keyboards.btn_text) \
            .filter_by(player_id=player_id, btn_data=open_btn_data) \
            .update({db.Keyboards.btn_text: Game.default_emj})
        session.commit()


class Player(Game):
    def add_player(self, player_id, nickname):
        session = self._get_session
        new_player = db.Players(id=player_id, nickname=nickname)
        new_game = db.Games(id=player_id)
        session.add(new_player)
        session.add(new_game)
        session.commit()

    def is_new_player(self, player_id):
        session = self._get_session
        player = session.query(db.Players).get(player_id)
        session.close()
        return not bool(player)

    def get_player(self, player_id):
        session = self._get_session
        player = session.query(db.Players).get(player_id)
        session.close()
        return player

    def get_rating(self, player_id):
        level = self.get_level(player_id)
        count_try = self.get_count_try(player_id)
        rating = 2 * level / count_try * 100
        return round(rating, 2)

    def get_player_record(self, player_id):
        level = self.get_level(player_id)
        session = self._get_session
        record = session.query(top_ratings[level]).select_from(db.Players) \
            .filter_by(id=player_id).first()[0]
        session.close()
        return record

    def is_new_record(self, player_id):
        return bool(self.get_rating(player_id) > self.get_player_record(player_id))

    def add_new_record(self, player_id):
        record = self.get_rating(player_id)
        level = self.get_level(player_id)
        session = self._get_session
        session.query(db.Players).filter_by(id=player_id).update({top_ratings[level]: record})
        session.commit()

    def change_nickname(self, player_id, nickname):
        session = self._get_session
        player = session.query(db.Players).get(player_id)
        player.nickname = nickname
        session.commit()

    def clear_player_records(self, player_id):
        session = self._get_session
        player = session.query(db.Players).get(player_id)
        player.top_easy_rating = 0
        player.top_normal_rating = 0
        player.top_hard_rating = 0
        session.commit()
