from sqlalchemy import Column, Integer, String, create_engine, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DB_FILENAME

Base = declarative_base()


class Players(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True, autoincrement=False)
    nickname = Column(String(33))
    top_easy_rating = Column(Float, default=0)
    top_normal_rating = Column(Float, default=0)
    top_hard_rating = Column(Float, default=0)


class Session:
    def __init__(self):
            self.engine = create_engine('sqlite:///{}'.format(DB_FILENAME), echo=False)
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
