from bot.handlers import start, admin, callbacks


def register(app):
    start.register(app)
    admin.register(app)
    callbacks.register(app)
