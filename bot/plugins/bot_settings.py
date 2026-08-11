from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

# Load real values from your config
LOG_CHANNEL = "not set"
FORCE_SUB_CHANNEL_ID = "[insert_channel_id]"
ADMINS = [12345678]  # your Telegram user id(s)


def settings_text() -> str:
    return (
        "Bot Settings\n\n"
        f"Log Channel : {LOG_CHANNEL}\n"
        f"Force Sub : {FORCE_SUB_CHANNEL_ID}\n\n"
        "Tap a button below to configure a setting."
    )


def settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Log Channel", callback_data="set_log_channel")],
            [InlineKeyboardButton("Force Sub", callback_data="set_force_sub")],
            [InlineKeyboardButton("Close", callback_data="close_settings")],
        ]
    )


@Client.on_message(filters.command("botsettings") & filters.private)
async def botsettings(client: Client, message: Message):
    # Remove this admin gate if you want everyone to use it
    if message.from_user.id not in ADMINS:
        return
    await message.reply_text(settings_text(), reply_markup=settings_keyboard())


@Client.on_callback_query(filters.regex(r"^(set_log_channel|set_force_sub|close_settings)$"))
async def settings_buttons(client: Client, query: CallbackQuery):
    await query.answer()
    if query.data == "set_log_channel":
        await query.message.edit_text("Send me the Log Channel ID/username.", reply_markup=settings_keyboard())
    elif query.data == "set_force_sub":
        await query.message.edit_text("Send me the Force Sub channel ID.", reply_markup=settings_keyboard())
    elif query.data == "close_settings":
        await query.message.edit_text("Settings closed.")
