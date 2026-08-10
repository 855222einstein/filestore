from pyrogram import Client, filters
from pyrogram.errors import AccessTokenInvalid
from pyrogram.handlers import MessageHandler

from bot import LOGGER
from bot.config import Config
from bot.database import db

# Keep references so clones aren't garbage-collected.
CLONES = {}


def _configure(app, admins, storage_channel, force_sub_channel, is_clone):
    app.admins = admins
    app.storage_channel = storage_channel
    app.force_sub_channel = force_sub_channel
    app.is_clone = is_clone


async def _build(token, name):
    from bot.handlers import register as register_handlers
    from bot.modules import register as register_modules

    app = Client(
        name,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=token,
        in_memory=True,
    )
    register_handlers(app)
    register_modules(app)
    return app


async def start_clone(token, owner_id):
    """Start a single clone Client and attach its own config."""
    app = await _build(token, f"clone_{owner_id}")
    await app.start()
    me = await app.get_me()
    app.me = me
    settings = await db.get_settings(me.id)
    _configure(
        app,
        admins=[owner_id],
        storage_channel=settings.get("storage_channel", 0),
        force_sub_channel=settings.get("force_sub_channel", 0),
        is_clone=True,
    )
    CLONES[me.id] = app
    LOGGER.info("Clone @%s started (owner %s).", me.username, owner_id)
    return me


async def restart_clones():
    """Re-launch every stored clone on boot; drop any with a dead token."""
    async for record in db.all_clones():
        try:
            await start_clone(record["token"], record["owner_id"])
        except AccessTokenInvalid:
            LOGGER.warning("Removing clone %s — token invalid.", record["_id"])
            await db.delete_clone(record["_id"])
        except Exception as e:
            LOGGER.error("Failed to start clone %s: %s", record["_id"], e)


async def clone_handler(client, message):
    user = message.from_user
    if not Config.ALLOW_CLONE and user.id not in Config.ADMINS:
        return await message.reply_text("⛔ Cloning is disabled on this bot.")
    if len(message.command) < 2:
        return await message.reply_text(
            "Usage: `/clone <bot_token>`\nGet a token from @BotFather (`/newbot`)."
        )
    token = message.command[1].strip()

    if await db.get_clone_by_owner(user.id):
        return await message.reply_text(
            "⚠️ You already have a clone. Use `/deleteclone` first to replace it."
        )

    status = await message.reply_text("⏳ Starting your clone...")
    try:
        me = await start_clone(token, user.id)
    except AccessTokenInvalid:
        return await status.edit_text("❌ Invalid bot token.")
    except Exception as e:
        return await status.edit_text(f"❌ Failed to start clone: `{e}`")

    await db.add_clone(me.id, token, user.id, me.username)
    await status.edit_text(
        f"✅ **Clone @{me.username} is live!**\n\n"
        "Next: open your bot and run `/setchannel <channel_id>` "
        "(add your bot as admin in that channel first)."
    )


async def deleteclone_handler(client, message):
    user = message.from_user
    record = await db.get_clone_by_owner(user.id)
    if user.id in Config.ADMINS and len(message.command) > 1:
        record = await db.get_clone(int(message.command[1]))
    if not record:
        return await message.reply_text("You don't have a clone to delete.")
    bot_id = record["_id"]
    app = CLONES.pop(bot_id, None)
    if app:
        try:
            await app.stop()
        except Exception:
            pass
    await db.delete_clone(bot_id)
    await message.reply_text(f"🗑 Clone @{record.get('username')} removed.")


def register(app):
    app.add_handler(MessageHandler(clone_handler, filters.command("clone") & filters.private))
    app.add_handler(MessageHandler(deleteclone_handler, filters.command("deleteclone") & filters.private))
