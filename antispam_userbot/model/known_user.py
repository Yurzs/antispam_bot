from mdocument import Document

from antispam_userbot.config import mongo_client, MONGO_DATABASE_NAME


class KnownUser(Document):
    collection = "known_users"
    database = MONGO_DATABASE_NAME
    client = mongo_client

    @classmethod
    async def find_by_id(cls, user_id) -> bool:
        """Finds if user_id is in known."""

        search_query = {
            "user_id": user_id
        }
        result = await cls.collection.find_one(search_query)
        if result:
            return True
        return False

    @classmethod
    async def find_or_create(cls, user_id):
        """Finds of creates new known user."""

        result = await cls.find_by_id(user_id)
        if not result:
            return await cls.create(user_id=user_id)
        return result
