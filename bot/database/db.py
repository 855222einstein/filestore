import datetime

import motor.motor_asyncio

from bot import LOGGER
from bot.config import Config


class Database:
    def __init__(self, uri: str, db_name: str):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[db_name]
        self.users = self.db["users"]
        self.clones = self.db["clones"]
        self.settings = self.db["settings"]

    # ---------------- Users ----------------
    async def add_user(self, user_id: int):
        if not await self.users.find_one({"_id": user_id}):
            await self.users.insert_one(
                {"_id": user_id, "joined": datetime.datetime.utcnow()}
            )

    async def is_user_exist(self, user_id: int) -> bool:
        return bool(await self.users.find_one({"_id": user_id}))

    async def total_users(self) -> int:
        return await self.users.count_documents({})

    def all_user_ids(self):
        return self.users.find({}, {"_id": 1})

    async def delete_user(self, user_id: int):
        await self.users.delete_one({"_id": user_id})

    # ---------------- Clones ----------------
    async def add_clone(self, bot_id: int, token: str, owner_id: int, username: str):
        await self.clones.update_one(
            {"_id": bot_id},
            {"$set": {
                "token": token,
                "owner_id": owner_id,
                "username": username,
                "created": datetime.datetime.utcnow(),
            }},
            upsert=True,
        )

    async def get_clone(self, bot_id: int):
        return await self.clones.find_one({"_id": bot_id})

    async def get_clone_by_owner(self, owner_id: int):
        return await self.clones.find_one({"owner_id": owner_id})

    def all_clones(self):
        return self.clones.find({})

    async def total_clones(self) -> int:
        return await self.clones.count_documents({})

    async def delete_clone(self, bot_id: int):
        await self.clones.delete_one({"_id": bot_id})
        await self.settings.delete_one({"_id": bot_id})

    # ---------------- Per-bot settings ----------------
    async def get_settings(self, bot_id: int) -> dict:
        return await self.settings.find_one({"_id": bot_id}) or {}

    async def update_setting(self, bot_id: int, key: str, value):
        await self.settings.update_one(
            {"_id": bot_id}, {"$set": {key: value}}, upsert=True
        )


db = Database(Config.DB_URI, Config.DB_NAME)
LOGGER.info("Database client initialised.")
