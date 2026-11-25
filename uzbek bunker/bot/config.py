import os


BOT_TOKEN: str = os.getenv(
    "BOT_TOKEN",
    "9031082623:AAG1msrdrTEUHivJVk4nyJqHxJvZNSLDdWE",
)
BOT_USERNAME: str = os.getenv("BOT_USERNAME", "uzbek_bunker_bot")
WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")

MIN_PLAYERS: int = 4

