import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
)
# Pyrogram is chatty at INFO; keep our logs clean.
logging.getLogger("pyrogram").setLevel(logging.WARNING)

__version__ = "1.0.0"
LOGGER = logging.getLogger("filestorebot")
