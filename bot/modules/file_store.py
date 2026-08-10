from pyrogram import filters
from pyrogram.handlers import MessageHandler

from bot.utils.decorators import admin_only
from bot.utils.helpers import encode, get_message_id

MEDIA = filters.document | filters.video | filters.audio | filters.photo | filters.animation | filters.voice


def _link(client, payload_plain: str) -> str:
    return f"https://t.me/{client.me.username}?start={encode(payload_plain)}"


@admin_only
async def store_file(client, message):
    """Admin sends any file in PM -> copy to storage channel -> return a share link."""
    if not client.storage_channel:
        return await message.reply_text(
            "⚠️ No storage channel set. Use `/setchannel <channel_id>` first."
        )
    try:
        posted = await message.copy(client.storage_channel)
    except Exception as e:
        return await message.reply_text(f"❌ Couldn't save to storage channel: `{e}`")
    link = _link(client, f"get-{posted.id}")
    await message.reply_text(
        f"✅ **Stored!**\n\n🔗 Share link:\n`{link}`",
        quote=True,
        disable_web_page_preview=True,
    )


# Simple two-step batch: /batch, then forward FIRST post, then forward LAST post.
_BATCH_STATE = {}


@admin_only
async def batch_start(client, message):
    _BATCH_STATE[message.from_user.id] = {}
    await message.reply_text(
        "📦 **Batch mode**\nForward the **first** post from the storage channel "
        "(or paste its t.me link)."
    )


async def batch_collect(client, message):
    uid = message.from_user.id
    state = _BATCH_STATE.get(uid)
    if state is None:
        return
    msg_id = await get_message_id(client, message)
    if not msg_id:
        return await message.reply_text("❌ That isn't a valid storage-channel post. Try again.")
    if "first" not in state:
        state["first"] = msg_id
        return await message.reply_text("👍 Now forward the **last** post (or its link).")
    first, last = state["first"], msg_id
    _BATCH_STATE.pop(uid, None)
    link = _link(client, f"batch-{first}-{last}")
    await message.reply_text(
        f"✅ **Batch link created** ({abs(last - first) + 1} files):\n`{link}`",
        disable_web_page_preview=True,
    )


def register(app):
    app.add_handler(MessageHandler(batch_start, filters.command("batch") & filters.private))
    # Batch collection must run before the generic file-store handler.
    app.add_handler(MessageHandler(
        batch_collect,
        filters.private & (MEDIA | filters.text) & ~filters.command(["start", "batch", "clone",
                                                                      "stats", "broadcast",
                                                                      "setchannel", "setforcesub",
                                                                      "deleteclone"]),
    ), group=0)
    app.add_handler(MessageHandler(store_file, filters.private & MEDIA), group=1)
