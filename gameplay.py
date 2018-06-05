import random
import math
import redis

import db_map as db
import keyboards
from config import top_ratings, game_emj
from sqlalchemy import func, distinct


def get_random_emoji(number_emj):
    selected_emj = random.sample(game_emj[:-1], number_emj // 2) * 2
    random.shuffle(selected_emj)
    return selected_emj


class Game(db.Session):
    def get_player_in_table(self, player_id):
        session = self._get_session
        sum_ratings = db.Players.top_easy_rating + db.Players.top_normal_rating + db.Players.top_hard_rating
        player = session.query(db.Players).get(player_id)
        player_rating = player.top_easy_rating + player.top_normal_rating + player.top_hard_rating
        player_position = session.query(func.count(distinct(sum_ratings)) + 1) \
            .filter(sum_ratings > player_rating).scalar()
        session.close()
        return player_position, round(player_rating, 2), player.nickname

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

    def get_level_record(self, level_name):
        session = self._get_session
        level_attr = getattr(db.Players, level_name)
        record = session.query(level_attr).order_by(level_attr.desc()).first()[0]
        session.close()
        return record


class Player(Game):
    def add_player(self, player_id, nickname):
        session = self._get_session
        new_player = db.Players(id=player_id, nickname=nickname)
        session.add(new_player)
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

    def get_player_record(self, player_id, level):
        session = self._get_session
        record = session.query(top_ratings[level]).select_from(db.Players) \
            .filter_by(id=player_id).first()[0]
        session.close()
        return record

    def add_new_record(self, player_id, record, level):
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


class GameBoard:
    r = redis.Redis(host='127.0.0.1', port=6379, db=1, decode_responses=True)

    def add_new_game(self, player_id, level):
        self.r.set('{}:level'.format(player_id), level)
        self.r.expire('{}:level'.format(player_id), 180000)
        default_cell = [game_emj[-1]]*level
        self.r.lpush('{}:displayed_cells'.format(player_id), *default_cell)
        self.r.expire('{}:displayed_cells'.format(player_id), 180000)
        emoji = get_random_emoji(level)
        self.r.lpush('{}:hidden_cells'.format(player_id), *emoji)
        self.r.expire('{}:hidden_cells'.format(player_id), 180000)
        self.r.set('{}:count_try'.format(player_id), 0)
        self.r.expire('{}:count_try'.format(player_id), 180000)

    def players_has_game(self, player_id):
        return self.r.get('{}:count_try'.format(player_id))

    def delete_game(self, player_id):
        player_keys = self.r.keys('{}:*'.format(player_id))
        if player_keys:
            self.r.delete(*player_keys)

    def get_keyboard(self, player_id):
        level = self.r.get('{}:level'.format(player_id))
        num_columns = round(math.sqrt(int(level)))
        count_try = self.r.get('{}:count_try'.format(player_id))
        displayed_cells = self.r.lrange('{}:displayed_cells'.format(player_id), 0, -1)
        keyboard = keyboards.get_game_kb(num_columns, displayed_cells, count_try)
        return keyboard

    def open_cell(self, player_id, cell_id):
        hidden_emj = self.r.lindex('{}:hidden_cells'.format(player_id), cell_id)
        self.r.lset('{}:displayed_cells'.format(player_id), cell_id, hidden_emj)

    def hide_cells(self, player_id, cell_id):
        default_cell = game_emj[-1]
        prev_cell = self.r.get('{}:open_cell'.format(player_id))
        self.r.lset('{}:displayed_cells'.format(player_id), prev_cell, default_cell)
        self.r.lset('{}:displayed_cells'.format(player_id), cell_id, default_cell)

    def add_open_cell(self, player_id, cell_id):
        self.r.set('{}:open_cell'.format(player_id), cell_id)
        self.r.expire('{}:open_cell'.format(player_id), 180000)

    def has_open_cell(self, player_id):
        return self.r.get('{}:open_cell'.format(player_id))

    def del_open_cell(self, player_id):
        self.r.delete('{}:open_cell'.format(player_id))

    def add_try(self, player_id):
        self.r.incr('{}:count_try'.format(player_id))

    def get_try(self, player_id):
        return self.r.get('{}:count_try'.format(player_id))

    def cell_is_open(self, player_id, cell_id):
        cell = self.r.lindex('{}:displayed_cells'.format(player_id), cell_id)
        return cell != game_emj[-1]

    def have_couple(self, player_id, cell_id):
        prev_cell_id = self.r.get('{}:open_cell'.format(player_id))
        prev_cell = self.r.lindex('{}:displayed_cells'.format(player_id), prev_cell_id)
        cell = self.r.lindex('{}:displayed_cells'.format(player_id), cell_id)
        return cell == prev_cell

    def is_finish(self, player_id):
        emoji = self.r.lrange('{}:displayed_cells'.format(player_id), 0, -1)
        return not game_emj[-1] in emoji

    def get_level(self, player_id):
        return int(self.r.get('{}:level'.format(player_id)))

    def get_rating(self, player_id):
        level = self.r.get('{}:level'.format(player_id))
        count_try = self.r.get('{}:count_try'.format(player_id))
        rating = 2 * int(level) / int(count_try) * 100
        return round(rating, 2)
