from engine.bot import client
from engine.logger import init_logger
from engine.utils import load_cogs
import engine.config as config


def run_discord_bot():
    init_logger()
    load_cogs(client)
    client.run(config.DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    run_discord_bot()
