from pyrogram import filters
from pyrogram.handlers import CallbackQueryHandler


async def callback_handler(client, query):
    data = query.data
    if data == "close":
        await query.message.delete()
    elif data == "how_clone":
        await query.answer()
        await query.message.reply_text(
            "♻️ **Create your own clone**\n\n"
            "1. Open @BotFather → `/newbot` → copy the token.\n"
            "2. Send me: `/clone <your-bot-token>`\n"
            "3. Open your new bot, then set its storage channel with "
            "`/setchannel <channel_id>` (add your bot as admin there first).\n\n"
            "Your clone runs independently with you as its admin."
        )
    else:
        await query.answer()


def register(app):
    app.add_handler(CallbackQueryHandler(callback_handler))
