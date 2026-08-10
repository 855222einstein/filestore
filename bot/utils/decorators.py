from functools import wraps


def admin_only(func):
    """Restrict a handler to the current bot's admins (mother owner/admins or clone owner)."""
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        admins = getattr(client, "admins", [])
        user = message.from_user
        if user and user.id in admins:
            return await func(client, message, *args, **kwargs)
        await message.reply_text("⛔ You are not authorized to use this command.")
    return wrapper
