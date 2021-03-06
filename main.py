import logging
import os

import aiohttp
import discord
import psnawp_api
from dotenv import load_dotenv

bot = discord.Bot()


@bot.event
async def on_ready():
    logger.info(f"We have logged in as Discord User {bot.user}.")


@bot.slash_command(description="To grab the XUID of XBOX user.", guild_ids=[793952307103662102])
async def grab_xuid(ctx, gamer_tag: str):
    if ctx.channel_id == 924193319507079238:
        await ctx.response.defer()
        logger.info(f"Received XBOX gamertag: {gamer_tag.strip()}.")
        auth_headers = {"X-Authorization": os.getenv("XBOX_API")}
        params = {'gt': gamer_tag.strip()}
        async with aiohttp.ClientSession() as session:
            async with session.get('https://xbl.io/api/v2/friends/search', headers=auth_headers, params=params) as resp:
                json_response = await resp.json()
                logger.info(f"XBOX API response {json_response}.")
                if profile_list := json_response.get('profileUsers'):
                    await ctx.respond(
                        "\n".join(f"{profile['settings'][2]['value']}: {profile['id']}" for profile in profile_list))
                else:
                    await ctx.respond(f"GamerTag {gamer_tag} not found.")
    else:
        await ctx.respond("The command only works in the #gamer-tag-id-grabber channel.")


@bot.slash_command(description="To grab the PSNID of PSN user.", guild_ids=[793952307103662102])
async def grab_psnid(ctx, gamer_tag: str):
    logger.info(f"Received PSN gamertag: {gamer_tag.strip()}.")
    if ctx.channel_id == 924193319507079238:
        try:
            user = psnawp.user(online_id=gamer_tag)
            logger.info(f"Response PSN {user}.")
            await ctx.respond(f"{user.online_id}: {user.account_id}")
        except Exception:
            await ctx.respond(f"GamerTag {gamer_tag} not found.")
    else:
        await ctx.respond("The command only works in the #gamer-tag-id-grabber channel.")


def main():
    bot.run(os.getenv("TOKEN"))


if __name__ == '__main__':
    load_dotenv('config.env')
    psnawp = psnawp_api.psnawp.PSNAWP(os.getenv('NPSSO_CODE'))
    logger = logging.getLogger("GammerTagIDGrabber")
    logger.setLevel(logging.DEBUG)

    log_stream = logging.StreamHandler()
    log_stream.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s')
    log_stream.setFormatter(formatter)
    logger.addHandler(log_stream)

    client = psnawp.me()
    logger.info(f"Logged in as PSN ID: {client.get_online_id()}.")
    main()
