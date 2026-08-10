from bot.modules import file_store, clone


def register(app):
    file_store.register(app)
    clone.register(app)
