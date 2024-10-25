import logging.config
import engine.config as config
from engine.bot import client
from engine.utils import load_cogs


def run_discord_bot():
    logging.config.dictConfig(config.LOGGING_SETTINGS)
    load_cogs(client)
    client.run(config.DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    run_discord_bot()
