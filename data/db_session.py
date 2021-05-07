from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

SqlAlchemyBase = declarative_base()
__factory = None


def global_init(db_file):
    db_file = db_file.strip()
    global __factory
    if __factory:
        return
    if not db_file:
        raise Exception('Некорректный файл БД')
    connection_str = 'sqlite:///%s?check_same_thread=False' % db_file
    engine = create_engine(connection_str, echo=False)
    __factory = sessionmaker(bind=engine)
    from . import __all_models
    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
