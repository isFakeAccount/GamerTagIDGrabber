#!.venv/bin/python
from os import getenv

import crescent
import hikari
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
    discord_token = getenv("DISCORD_TOKEN")
    if discord_token is None:
        msg = (
            "DISCORD_TOKEN environment variable not set. "
            "Please make sure you have .env file in project root directory and contains the right environment variables."
        )
        raise ValueError(msg)

    bot = hikari.GatewayBot(discord_token)
    client = crescent.Client(bot)
    client.plugins.load("plugins.gamertag_commands")
    bot.run()


if __name__ == "__main__":
    main()
