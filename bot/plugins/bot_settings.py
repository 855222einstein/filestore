"""
botsettings.py
Bot Settings message with inline buttons (Cookies section omitted).

Requires: python-telegram-bot >= 20.0
Install:  pip install python-telegram-bot
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ------------------------------------------------------------------ #
# Configuration
# ------------------------------------------------------------------ #
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Replace with your real values / load them from config or a database.
LOG_CHANNEL = "not set"
FORCE_SUB_CHANNEL_ID = "[insert_channel_id]"


# ------------------------------------------------------------------ #
# Builders
# ------------------------------------------------------------------ #
def build_settings_text() -> str:
    """Compose the Bot Settings message body."""
    return (
        "Bot Settings\n\n"
        f"Log Channel : {LOG_CHANNEL}\n"
        f"Force Sub : {FORCE_SUB_CHANNEL_ID}\n\n"
        "Tap a button below to configure a setting."
    )


def build_settings_keyboard() -> InlineKeyboardMarkup:
    """Build the inline keyboard (Cookies button omitted)."""
    keyboard = [
        [InlineKeyboardButton("Log Channel", callback_data="set_log_channel")],
        [InlineKeyboardButton("Force Sub", callback_data="set_force_sub")],
        [InlineKeyboardButton("Close", callback_data="close_settings")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ------------------------------------------------------------------ #
# Handlers
# ------------------------------------------------------------------ #
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the Bot Settings message with inline buttons."""
    await update.message.reply_text(
        text=build_settings_text(),
        reply_markup=build_settings_keyboard(),
    )


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button taps."""
    query = update.callback_query
    await query.answer()

    if query.data == "set_log_channel":
        await query.edit_message_text(
            "Send me the Log Channel ID/username to set it.",
            reply_markup=build_settings_keyboard(),
        )
    elif query.data == "set_force_sub":
        await query.edit_message_text(
            "Send me the Force Sub channel ID to set it.",
            reply_markup=build_settings_keyboard(),
        )
    elif query.data == "close_settings":
        await query.edit_message_text("Settings closed.")


# ------------------------------------------------------------------ #
# Entry point
# ------------------------------------------------------------------ #
def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("settings", settings))
    app.add_handler(CallbackQueryHandler(on_button))
    app.run_polling()


if __name__ == "__main__":
    main()
