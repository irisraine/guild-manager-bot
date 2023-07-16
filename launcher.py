from bot import client
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('TOKEN')


def run_discord_bot():
    client.run(TOKEN)


if __name__ == "__main__":
    run_discord_bot()
