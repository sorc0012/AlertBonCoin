from app.static.utils import Utils
from app import db
import sqlalchemy
import os

# Define the database object which is imported
# by modules and controllers
# dbPath = 'app.db'
# basedir = os.path.abspath(os.path.dirname(__file__))
# engine = sqlalchemy.create_engine('sqlite:///' + os.path.join(basedir, dbPath))
# db_session = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(autocommit=False,
#                                          autoflush=False,
#                                          bind=engine))
# Base = sqlalchemy.ext.declarative.declarative_base()
# Base.query = db_session.query_property()

if __name__ == '__main__':
    Utils.update_result_all(db.session, i_email=True)
