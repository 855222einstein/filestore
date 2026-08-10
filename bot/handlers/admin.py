import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from pyrogram.handlers import MessageHandler

from bot.database import db
from bot.utils.decorators import admin_only


@admin_only
async def stats_handler(client, message):
    await message.reply_text(
        "📊 **Bot Stats**\n\n"
        f"👥 Users: `{await db.total_users()}`\n"
        f"🤖 Clones: `{await db.total_clones()}`\n"
        f"🗂 Storage channel: `{client.storage_channel or 'not set'}`\n"
        f"🔒 Force-sub: `{client.force_sub_channel or 'off'}`"
    )


@admin_only
async def setchannel_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/setchannel <channel_id>` (e.g. -1001234567890)")
    try:
        channel = int(message.command[1])
        chat = await client.get_chat(channel)
        await client.send_message(channel, "✅ Storage channel linked.")
    except Exception as e:
        return await message.reply_text(f"❌ Can't use that channel: `{e}`\nMake me an admin there first.")
    await db.update_setting(client.me.id, "storage_channel", channel)
    client.storage_channel = channel
    await message.reply_text(f"✅ Storage channel set to **{chat.title}** (`{channel}`).")


@admin_only
async def setforcesub_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/setforcesub <channel_id | off>`")
    arg = message.command[1]
    if arg.lower() == "off":
        await db.update_setting(client.me.id, "force_sub_channel", 0)
        client.force_sub_channel = 0
        return await message.reply_text("✅ Force-subscribe disabled.")
    try:
        channel = int(arg)
        await client.get_chat_member(channel, "me")
    except Exception as e:
        return await message.reply_text(f"❌ {e}\nMake me an admin in that channel first.")
    await db.update_setting(client.me.id, "force_sub_channel", channel)
    client.force_sub_channel = channel
    await message.reply_text(f"✅ Force-subscribe set to `{channel}`.")


@admin_only
async def broadcast_handler(client, message):
    if not message.reply_to_message:
        return await message.reply_text("↩️ Reply to the message you want to broadcast.")
    status = await message.reply_text("📣 Broadcasting...")
    sent = failed = 0
    async for user in db.all_user_ids():
        uid = user["_id"]
        try:
            await message.reply_to_message.copy(uid)
            sent += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await message.reply_to_message.copy(uid)
                sent += 1
            except Exception:
                failed += 1
        except (InputUserDeactivated, UserIsBlocked, PeerIdInvalid):
            await db.delete_user(uid)
            failed += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)
    await status.edit_text(f"✅ Broadcast done.\nSent: `{sent}` | Failed/removed: `{failed}`")


def register(app):
    app.add_handler(MessageHandler(stats_handler, filters.command("stats") & filters.private))
    app.add_handler(MessageHandler(setchannel_handler, filters.command("setchannel") & filters.private))
    app.add_handler(MessageHandler(setforcesub_handler, filters.command("setforcesub") & filters.private))
    app.add_handler(MessageHandler(broadcast_handler, filters.command("broadcast") & filters.private))
