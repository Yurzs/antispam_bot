import os

from motor.motor_asyncio import AsyncIOMotorClient

SECRET = os.environ["SECRET"]
API_ID = os.environ["API_ID"]
SESSION_PATH = os.environ["SESSION_PATH"]

print(SESSION_PATH)
MONGO_DATABASE_URI = os.environ["MONGO_DATABASE_URI"]
MONGO_DATABASE_NAME = os.environ["MONGO_DATABASE_NAME"]

mongo_client = AsyncIOMotorClient(MONGO_DATABASE_URI)
