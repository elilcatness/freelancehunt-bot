from sqlalchemy import Column, Integer, ForeignKey, Table, orm

from .db_session import SqlAlchemyBase

project_to_mail = Table('project_to_mail', SqlAlchemyBase.metadata,
                        Column('project', Integer, ForeignKey('projects.id')),
                        Column('mail', Integer, ForeignKey('mails.id')))


class Mail(SqlAlchemyBase):
    __tablename__ = 'mails'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    projects = orm.relation('Project', secondary=project_to_mail, backref='mails')
