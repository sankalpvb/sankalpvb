# reconmaster/app/api/schemas.py

from pydantic import BaseModel
from typing import Optional

# This is the Pydantic model (schema) for our Tool data.
# It defines the shape of the data that will be sent over the API.

class ToolBase(BaseModel):
    name: str
    category: str
    description: str
    base_command: str
    advantages: Optional[str] = None
    example_usage: Optional[str] = None

class Tool(ToolBase):
    id: int

    class Config:
        # This tells Pydantic to read the data even if it is not a dict,
        # but an ORM model (like our SQLAlchemy Tool model).
        orm_mode = True
