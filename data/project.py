from sqlalchemy import Column, Integer

from .db_session import SqlAlchemyBase


class Project(SqlAlchemyBase):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    fh_id = Column(Integer, unique=True)