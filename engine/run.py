from engine.bot import client
from engine.logger import init_logger
from engine.utils import load_cogs
from dotenv import load_dotenv
import os

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')


def run_discord_bot():
    init_logger()
    load_cogs(client)
    client.run(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    run_discord_bot()
