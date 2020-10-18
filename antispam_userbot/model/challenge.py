import pymongo
from mdocument import Document, DocumentDoesntExist

from antispam_userbot.config import mongo_client, MONGO_DATABASE_NAME


class Challenge(Document):
    collection = "challenges"
    database = MONGO_DATABASE_NAME
    client = mongo_client

    @classmethod
    def create_indexes(cls):
        """Creates required indexes."""

        cls.sync_collection.create_index([
            ("user_id", pymongo.ASCENDING)
        ], unique=True)

    @classmethod
    async def create(cls, user_id, correct_answer) -> "Document":
        """Creates new challenge for user."""

        query = {
            "user_id": user_id,
            "correct_answer": correct_answer,
        }

        return await super().create(**query)

    @classmethod
    async def one(cls, user_id, required=True):
        """Finds challenge by user id."""

        query = {
            "user_id": user_id,
        }
        try:
            return await super().one(**query)
        except DocumentDoesntExist as e:
            if required:
                raise e

    @classmethod
    async def find_and_delete(cls, user_id) -> None:
        """Finds user challenge and deletes it."""

        challenge = await cls.one(user_id)
        if challenge:
            await challenge.delete()
