import os
import logging
import logging.config
import sqlalchemy as sql
import argparse
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy import Column, Integer, String, MetaData
# import config
#from helpers import create_connection, get_session


conn_type = "mysql+pymysql"
user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
host = os.environ.get("MYSQL_HOST")
port = os.environ.get("MYSQL_PORT")
database = os.environ.get("MYSQL_DATABASE")
LOCAL_DB_WRITE_PATH = "data/sqlite_flight.db"

Base = declarative_base()

logging.config.fileConfig("config/logging/local.conf")
logger = logging.getLogger('flight-models')


class Flight(Base):
    """Create a data model for the database to be set up for capturing flights """
    __tablename__ = 'flight'
    id = Column(Integer, primary_key=True)
    month = Column(Integer, unique=False, nullable=False)
    day_of_month = Column(Integer, unique=False, nullable=False)
    day_of_week = Column(Integer, unique=False, nullable=False)
    airline = Column(String(100), unique=False, nullable=False)
    origin_city = Column(String(100), unique=False, nullable=False)
    dest_city = Column(String(100), unique=False, nullable=False)
    dep_time = Column(Integer, unique=False, nullable=False)
    air_time = Column(Integer, unique=False, nullable=False)

    def __repr__(self):
        return '<Flight %r>' % self.title


def _truncate_flight(session):
    """Deletes flight records table if rerunning and run into unique key error."""
    session.execute('''DELETE FROM flight''')

def create_db(engine=None, engine_string=None):
    """Creates a database with the data models inherited from `Base` (Tweet and TweetScore).

    Args:
        engine (:py:class:`sqlalchemy.engine.Engine`, default None): SQLAlchemy connection engine.
            If None, `engine_string` must be provided.
        engine_string (`str`, default None): String defining SQLAlchemy connection URI in the form of
            `dialect+driver://username:password@host:port/database`. If None, `engine` must be provided.

    Returns:
        None
    """
    if engine is None and engine_string is None:
        return ValueError("`engine` or `engine_string` must be provided")
    elif engine is None:
        engine = sql.create_engine(engine_string)

    Base.metadata.create_all(engine)




if __name__ == "__main__":
    logger = logging.getLogger('flight-models')

    parser = argparse.ArgumentParser(description="Create defined tables in database")
    parser.add_argument("--truncate", "-t", default=False, action="store_true",
                        help="If given, delete current records from tweet_scores table before create_all "
                             "so that table can be recreated without unique id issues ")
    parser.add_argument('mode', help='which database to create table in', choices=['rds', 'sqlite'])
    args = parser.parse_args()

    if args.mode == 'rds':
        engine_string = "{}://{}:{}@{}:{}/{}".format(conn_type, user, password, host, port, database)
    else:
        engine_string = "sqlite:///{}".format(LOCAL_DB_WRITE_PATH)

    # If "truncate" is given as an argument (i.e. python models.py --truncate), then empty the flight table)
    if args.truncate:
        engine = sql.create_engine(engine_string)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            logger.info("Attempting to truncate flight table.")
            _truncate_flight(session)
            session.commit()
            logger.info("flight truncated.")
        except Exception as e:
            logger.error("Error occurred while attempting to truncate flight table.")
            logger.error(e)
            pass
        finally:
            session.close()

    create_db(engine_string=engine_string)

    try:
        engine = sql.create_engine(engine_string)
        Session = sessionmaker(bind=engine)
        session = Session()
        flight1 = Flight(month=11, day_of_month=3, day_of_week=4, airline="AA", origin_city="LAX", dest_city="ORD", dep_time=2220, \
                         air_time = 100)
        session.add(flight1)
        session.commit()
        logger.info("Database created with one row")
    except sql.exc.IntegrityError as e:
        # Checking for primary key duplication
        logger.error("add_row: "+str(e.args))
    except sql.exc.OperationalError:
        # Checking for correct credentials
        logger.error("add_row: Access denied! Please enter correct credentials")
    finally:
        session.close()
