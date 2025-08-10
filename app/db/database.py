# reconmaster/app/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the path to the SQLite database file.
# It will be created in the `app/db/` directory.
SQLALCHEMY_DATABASE_URL = "sqlite:///./app/db/tools.db"

# Create the SQLAlchemy engine.
# The `connect_args` is needed only for SQLite to allow multi-threaded access.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a SessionLocal class. Each instance of this class will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class. Our database model classes will inherit from this class.
Base = declarative_base()
