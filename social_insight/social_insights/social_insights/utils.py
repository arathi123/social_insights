from sqlalchemy.sql.schema import MetaData

from .models import DBSession, Base
from sqlalchemy import engine_from_config
from sqlalchemy.sql.elements import quoted_name


def configure_db_session(settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    if 'sosilee.schema' in settings:
        schema = settings['sosilee.schema']
        Base.metadata.schema = quoted_name(schema, True)
    Base.metadata.bind = engine
    Base.prepare(engine, reflect=True)
    Base.metadata.create_all()
    return engine, DBSession


def drop_all_tables(settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    if 'sosilee.schema' in settings:
        schema = settings['sosilee.schema']
    metadata = MetaData(engine, schema=schema, reflect=True)
    metadata.drop_all()
