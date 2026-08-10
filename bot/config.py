import os
from dotenv import load_dotenv

load_dotenv()


def _ids(value: str):
    return [int(x) for x in value.replace(",", " ").split() if x.strip().lstrip("-").isdigit()]


class Config:
    # --- Telegram core (get API_ID/API_HASH from https://my.telegram.org) ---
    API_ID = int(os.environ.get("API_ID", 0))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

    # --- Access control ---
    OWNER_ID = int(os.environ.get("OWNER_ID", 0))
    ADMINS = list({*_ids(os.environ.get("ADMINS", "")), OWNER_ID} - {0})

    # --- Storage ---
    # Private channel where files live. Bot must be admin there.
    STORAGE_CHANNEL = int(os.environ.get("STORAGE_CHANNEL", 0))

    # --- Force subscribe (0 = disabled). Bot must be admin in this channel. ---
    FORCE_SUB_CHANNEL = int(os.environ.get("FORCE_SUB_CHANNEL", 0))

    # --- Database ---
    DB_URI = os.environ.get("DB_URI", "")
    DB_NAME = os.environ.get("DB_NAME", "filestorebot")

    # --- Behaviour flags ---
    # Disable forwarding/saving of delivered files.
    PROTECT_CONTENT = os.environ.get("PROTECT_CONTENT", "False").lower() == "true"
    # Allow non-admins to spin up their own clone via /clone.
    ALLOW_CLONE = os.environ.get("ALLOW_CLONE", "True").lower() == "true"

    @classmethod
    def validate(cls):
        missing = [
            k for k in ("API_ID", "API_HASH", "BOT_TOKEN", "DB_URI")
            if not getattr(cls, k)
        ]
        if missing:
            raise SystemExit(f"Missing required env vars: {', '.join(missing)}")
        if not cls.OWNER_ID:
            raise SystemExit("OWNER_ID is required.")
