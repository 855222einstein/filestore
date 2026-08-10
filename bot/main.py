import asyncio

from pyrogram import Client, idle

from bot import LOGGER, __version__
from bot.config import Config
from bot.database import db
from bot.handlers import register as register_handlers
from bot.modules import register as register_modules
from bot.modules.clone import restart_clones, CLONES


async def main():
    Config.validate()

    app = Client(
        "mother_bot",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
    )
    register_handlers(app)
    register_modules(app)

    await app.start()
    me = await app.get_me()
    app.me = me

    # Load persisted settings, falling back to env for the mother bot.
    settings = await db.get_settings(me.id)
    app.admins = Config.ADMINS
    app.storage_channel = settings.get("storage_channel") or Config.STORAGE_CHANNEL
    app.force_sub_channel = settings.get("force_sub_channel") or Config.FORCE_SUB_CHANNEL
    app.is_clone = False

    LOGGER.info("Mother bot @%s started (v%s).", me.username, __version__)

    await restart_clones()
    LOGGER.info("Boot complete. Active clones: %d", len(CLONES))

    await idle()

    # Graceful shutdown.
    for clone in list(CLONES.values()):
        try:
            await clone.stop()
        except Exception:
            pass
    await app.stop()
    LOGGER.info("Stopped.")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
