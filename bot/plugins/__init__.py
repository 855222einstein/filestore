from bot.plugins import start, user_settings, bot_settings


def register(app):
    start.register(app)
    user_settings.register(app)
    bot_settings.register(app)
