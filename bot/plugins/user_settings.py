from pyrogram import filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database import db


def _panel(user: dict):
    notify = user.get("notify", True)
    text = (
        "⚙️ **Your Settings**\n\n"
        f"🆔 User ID: `{user.get('_id')}`\n"
        f"🔔 Broadcast notifications: {'ON ✅' if notify else 'OFF ❌'}"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            f"🔔 Notifications: {'ON' if notify else 'OFF'}",
            callback_data="us:toggle_notify",
        )],
        [InlineKeyboardButton("✖️ Close", callback_data="us:close")],
    ])
    return text, kb


async def settings_cmd(client, message):
    await db.add_user(message.from_user.id)
    user = await db.get_user(message.from_user.id)
    text, kb = _panel(user)
    await message.reply_text(text, reply_markup=kb)


async def settings_cb(client, query):
    uid = query.from_user.id
    action = query.data.split(":", 1)[1]
    if action == "close":
        return await query.message.delete()
    if action == "toggle_notify":
        user = await db.get_user(uid)
        await db.update_user_setting(uid, "notify", not user.get("notify", True))
        user = await db.get_user(uid)
        text, kb = _panel(user)
        await query.answer("Updated.")
        await query.message.edit_text(text, reply_markup=kb)


def register(app):
    app.add_handler(MessageHandler(
        settings_cmd,
        filters.command(["settings", "mysettings"]) & filters.private,
    ))
    app.add_handler(CallbackQueryHandler(settings_cb, filters.regex("^us:")), group=1)
