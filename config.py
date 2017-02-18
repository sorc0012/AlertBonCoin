import os
# Statement for enabling the development environment
DEBUG = True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - we are working with
# SQLite for this example

# SQLALCHEMY_DATABASE_URI = 'mysql://sorc0012:Sorcalways12@mysql-sorc0012.alwaysdata.net/sorc0012_alertboncoindb'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
print("DBURI: " + SQLALCHEMY_DATABASE_URI)

SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'db_repository')

SQLALCHEMY_POOL_RECYCLE = 299

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "secret"

# Maximum page nb for search
MAX_PAGE_NB = 5