import os

from sqlalchemy import Column, Integer, String, create_engine, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from config import DB_FILENAME, game_emj

Base = declarative_base()


class Players(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True, autoincrement=False)
    nickname = Column(String(33))
    level = Column(Integer, default=16)
    top_easy_rating = Column(Float, default=0)
    top_normal_rating = Column(Float, default=0)
    top_hard_rating = Column(Float, default=0)


class Emoji(Base):
    __tablename__ = 'emoji'
    id = Column(Integer, primary_key=True)
    emoji = Column(String)


class Games(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True, autoincrement=False)
    open_cell = Column(String(6))
    count_try = Column(Integer, default=0)


class Keyboards(Base):
    __tablename__ = 'keyboards'
    id = Column(Integer, primary_key=True)
    btn_data = Column(String(6))
    btn_text = Column(Integer)
    hidden_text = Column(Integer)
    player_id = Column(Integer, ForeignKey('players.id'))
    player = relationship('Players', backref='button')


class Session:
    def __init__(self):
            self.engine = create_engine(os.environ['DATABASE_URL'], echo=True)
            self._create_new()

    def _delete_model(self, model_cls):
        session = self._get_session
        models = session.query(model_cls).order_by(model_cls.id)
        for model in models:
            session.delete(model)
        session.commit()

    @property
    def _get_session(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

    def _create_new(self):
        Base.metadata.create_all(self.engine)
        session = self._get_session
        if not session.query(Emoji.id).first():
            self._add_emoji()
        session.close()

    def _add_emoji(self):
        session = self._get_session
        emojis = []
        for emoji in game_emj:
            emojis.append(Emoji(emoji=emoji))
        session.add_all(emojis)
        session.commit()
