import base64
import re

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant


def encode(string: str) -> str:
    """URL-safe base64 without padding — safe for /start deep-link payloads."""
    b64 = base64.urlsafe_b64encode(string.encode("ascii"))
    return b64.decode("ascii").rstrip("=")


def decode(payload: str) -> str:
    padding = "=" * (-len(payload) % 4)
    return base64.urlsafe_b64decode((payload + padding).encode("ascii")).decode("ascii")


async def is_subscribed(client, user_id: int) -> bool:
    """True if force-sub is off, user is admin, or user is a member of the FSub channel."""
    channel = getattr(client, "force_sub_channel", 0)
    if not channel:
        return True
    if user_id in getattr(client, "admins", []):
        return True
    try:
        member = await client.get_chat_member(channel, user_id)
        return member.status not in (
            ChatMemberStatus.LEFT,
            ChatMemberStatus.BANNED,
        )
    except UserNotParticipant:
        return False
    except Exception:
        # If we can't verify (e.g. bot not admin), don't hard-block users.
        return True


_LINK_RE = re.compile(r"https?://t\.me/(?:c/(\d+)|([\w_]+))/(\d+)")


async def get_message_id(client, message) -> int:
    """Resolve a storage-channel message id from a forward or a t.me post link."""
    storage = getattr(client, "storage_channel", 0)

    if message.forward_from_chat and message.forward_from_chat.id == storage:
        return message.forward_from_message_id

    if message.text:
        match = _LINK_RE.match(message.text.strip())
        if match:
            c_id, uname, msg_id = match.groups()
            if c_id and int(f"-100{c_id}") == storage:
                return int(msg_id)
            if uname:
                chat = await client.get_chat(storage)
                if chat.username and chat.username.lower() == uname.lower():
                    return int(msg_id)
    return 0
