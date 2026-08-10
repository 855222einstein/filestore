from pyrogram import filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.config import Config
from bot.database import db
from bot.utils.decorators import admin_only


def _panel(client):
    protect = getattr(client, "protect_content", Config.PROTECT_CONTENT)
    text = (
        "🛠 **Bot Settings**\n\n"
        f"🗂 Storage channel: `{getattr(client, 'storage_channel', 0) or 'not set'}`\n"
        f"🔒 Force-sub channel: `{getattr(client, 'force_sub_channel', 0) or 'off'}`\n"
        f"🛡 Protect content: {'ON ✅' if protect else 'OFF ❌'}\n\n"
        "Change channels with `/setchannel <id>` and `/setforcesub <id|off>`."
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            f"🛡 Protect content: {'ON' if protect else 'OFF'}",
            callback_data="bs:toggle_protect",
        )],
        [InlineKeyboardButton("🔄 Refresh", callback_data="bs:refresh")],
        [InlineKeyboardButton("✖️ Close", callback_data="bs:close")],
    ])
    return text, kb


@admin_only
async def botsettings_cmd(client, message):
    text, kb = _panel(client)
    await message.reply_text(text, reply_markup=kb)


async def botsettings_cb(client, query):
    if query.from_user.id not in getattr(client, "admins", []):
        return await query.answer("Not authorized.", show_alert=True)
    action = query.data.split(":", 1)[1]
    if action == "close":
        return await query.message.delete()
    if action == "toggle_protect":
        new = not getattr(client, "protect_content", Config.PROTECT_CONTENT)
        client.protect_content = new
        await db.update_setting(client.me.id, "protect_content", new)
        await query.answer("Updated.")
    else:
        await query.answer()
    text, kb = _panel(client)
    await query.message.edit_text(text, reply_markup=kb)


def register(app):
    app.add_handler(MessageHandler(botsettings_cmd, filters.command("botsettings") & filters.private))
    app.add_handler(CallbackQueryHandler(botsettings_cb, filters.regex("^bs:")), group=2)
