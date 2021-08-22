from sqlalchemy import Column, Integer

from .db_session import SqlAlchemyBase


class Mail(SqlAlchemyBase):
    __tablename__ = 'mails'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    last_id = Column(Integer)
    unread_threads_count = Column(Integer, default=0)
    messages_count = Column(Integer, default=0)