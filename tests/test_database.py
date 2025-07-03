# In tests/test_database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app import models # <-- ADD THIS IMPORT to make sure tables are registered

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Now, this command will see all your models and create the tables correctly
Base.metadata.create_all(bind=engine)

def override_get_db():
    """
    A dependency override to use the test database instead of the real one.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()