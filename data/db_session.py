from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

SqlAlchemyBase = declarative_base()
__factory = None


def global_init(db_file):
    db_file = db_file.strip()
    global __factory
    if __factory:
        return
    if not db_file:
        raise Exception('Некорректный файл БД')
    engine = create_engine(db_file.replace('postgres', 'postgresql'), poolclass=NullPool, echo=False)
    __factory = sessionmaker(bind=engine)
    from . import __all_models
    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
