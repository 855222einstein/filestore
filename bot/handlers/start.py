from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot import LOGGER
from bot.config import Config
from bot.database import db
from bot.utils.helpers import decode, is_subscribed


def _force_sub_markup(invite_link: str, payload: str, me_username: str):
    buttons = [[InlineKeyboardButton("📢 Join Channel", url=invite_link)]]
    if payload:
        buttons.append([InlineKeyboardButton(
            "🔄 I've Joined — Try Again",
            url=f"https://t.me/{me_username}?start={payload}",
        )])
    return InlineKeyboardMarkup(buttons)


async def _deliver(client, message, ids):
    delivered = 0
    for msg_id in ids:
        try:
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=client.storage_channel,
                message_id=msg_id,
                protect_content=Config.PROTECT_CONTENT,
            )
            delivered += 1
        except Exception as e:
            LOGGER.warning("Failed to copy %s: %s", msg_id, e)
    if not delivered:
        await message.reply_text("⚠️ These files are no longer available.")


async def start_handler(client, message):
    user = message.from_user
    await db.add_user(user.id)
    payload = message.command[1] if len(message.command) > 1 else None

    # Force-subscribe gate.
    if not await is_subscribed(client, user.id):
        try:
            invite = (await client.get_chat(client.force_sub_channel)).invite_link \
                or await client.export_chat_invite_link(client.force_sub_channel)
        except Exception:
            invite = "https://t.me/"
        return await message.reply_text(
            "🔒 **Please join our channel to use this bot.**",
            reply_markup=_force_sub_markup(invite, payload or "", client.me.username),
        )

    # No payload → welcome message.
    if not payload:
        return await message.reply_text(
            f"👋 **Hello {user.first_name}!**\n\n"
            "I store files and give you shareable links.\n"
            "Send me a link someone shared to get the file, "
            "or (if you're an admin) send me a file to generate a link.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("♻️ Create Your Own Clone", callback_data="how_clone")]]
            ),
        )

    # Decode the deep-link payload.
    try:
        data = decode(payload)
    except Exception:
        return await message.reply_text("❌ Invalid or expired link.")

    if not client.storage_channel:
        return await message.reply_text("⚠️ This bot has no storage channel configured yet.")

    if data.startswith("get-"):
        ids = [int(data.split("-", 1)[1])]
    elif data.startswith("batch-"):
        _, first, last = data.split("-")
        first, last = int(first), int(last)
        ids = range(first, last + 1) if first <= last else range(first, last - 1, -1)
    else:
        return await message.reply_text("❌ Invalid link format.")

    status = await message.reply_text("📤 Sending your file(s)...")
    await _deliver(client, message, ids)
    await status.delete()


def register(app):
    app.add_handler(MessageHandler(start_handler, filters.command("start") & filters.private))
