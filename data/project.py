from sqlalchemy import Column, Integer, ForeignKey, Table, orm

from .db_session import SqlAlchemyBase


class Project(SqlAlchemyBase):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)