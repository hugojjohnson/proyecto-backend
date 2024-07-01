from beanie import Document, PydanticObjectId
from pydantic import BaseModel
from typing import List, Optional

class User(Document):
    username: str
    email: str
    hash: str
    date_joined: str

    class Settings:
        name = "users"


class Token(Document):
    user: PydanticObjectId
    time_created: str
    value: str


# Application classes
class Log(Document):
    user: PydanticObjectId | str
    project: PydanticObjectId | str
    date: str
    goal: str
    notes: str

class Project(Document):
    user: PydanticObjectId | str
    coverUrl: str
    name: str
    goal: str
    dateStarted: str
    duration: int