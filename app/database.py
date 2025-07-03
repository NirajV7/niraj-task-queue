from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# The database URL tells SQLAlchemy how to connect to our Postgres database.
# postgresql://user:password@db/task_queue
# 'db' is the service name from our docker-compose.yml file.
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@db/task_queue"

# The engine is the entry point to the database.
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Each instance of the SessionLocal class will be a new database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is a factory function that will be used to create our ORM models.
Base = declarative_base()

# Dependency to get a DB session
def get_db():
    """
    A dependency for FastAPI routes to get a database session.
    It ensures the database connection is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()