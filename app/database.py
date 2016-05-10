from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app import app

parking_engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI_PARKING"], convert_unicode=True)
parking_db_session = scoped_session(sessionmaker(autocommit=False,
                                                 autoflush=False,
                                                 bind=parking_engine))

misc_engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI_MISC"], convert_unicode=True)
misc_db_session = scoped_session(sessionmaker(autocommit=False,
                                              autoflush=False,
                                              bind=misc_engine))
PBase = declarative_base()
PBase.query = parking_db_session.query_property()

MiscBase = declarative_base()
MiscBase.query = misc_db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import mod_parking.models
    import mod_socks.models
    import mod_login.models
    PBase.metadata.create_all(bind=parking_engine)
    MiscBase.metadata.create_all(bind=misc_engine)
