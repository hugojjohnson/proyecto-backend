from beanie import init_beanie
import motor.motor_asyncio
import os

from mongodb.models.book import Book
from mongodb.models.user import User, Token, Log, Project


async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        f"mongodb+srv://{os.environ["MGDB_USERNAME"]}:{os.environ["MGDB_PASSWORD"]}@main.jyiltof.mongodb.net/?retryWrites=true&w=majority&appName=main"
    )

    await init_beanie(database=client.books_example, document_models=[Book])
    await init_beanie(database=client.main, document_models=[User, Token, Log, Project])