#!.venv/bin/python
from os import getenv

import crescent
import hikari
from dotenv import load_dotenv

load_dotenv()
bot = hikari.GatewayBot(getenv("DISCORD_TOKEN", "DISCORD_TOKEN"))
client = crescent.Client(bot)
client.plugins.load("plugins.gamertag_commands")


def main() -> None:
    bot.run()


if __name__ == "__main__":
    main()
