# reconmaster/app/db/models.py

from sqlalchemy import Column, Integer, String, Text
from .database import Base

# Define the Tool model which corresponds to the 'tools' table in the database
class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, index=True)
    description = Column(Text, nullable=False)
    base_command = Column(String, nullable=False)
    advantages = Column(Text) # Can store comma-separated strings or JSON
    example_usage = Column(String)
