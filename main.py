import logging
import os
from json import JSONDecodeError

import aiohttp
import crescent
import psnawp_api
from aiohttp import ContentTypeError
from dotenv import load_dotenv

load_dotenv('config.env')
bot = crescent.Bot(os.getenv('TOKEN'))


@bot.include
@crescent.command(description="To grab the XUID of XBOX user.", guild=793952307103662102)
async def grab_xuid(ctx, gamer_tag: str):
    await ctx.defer()
    logger.info(f"Received XBOX gamertag: {gamer_tag.strip()}.")
    auth_headers = {"X-Authorization": os.getenv("XBOX_API")}
    params = {'gt': gamer_tag.strip()}

    # Retries the search two times before giving up.
    for i in range(2):
        try:
            async with aiohttp.ClientSession(headers=auth_headers) as session:
                async with session.get('https://xbl.io/api/v2/friends/search', params=params) as resp:
                    json_response = await resp.json()
                    logger.info(f"XBOX API response {json_response}.")
                    if profile_list := json_response.get('profileUsers'):
                        await ctx.respond(
                            "\n".join(f"{profile['settings'][2]['value']}: {profile['id']}" for profile in profile_list))
                    else:
                        await ctx.respond(f"GamerTag {gamer_tag} not found.")
                    break
        except (ContentTypeError, JSONDecodeError, KeyError):
            if i == 1:
                await ctx.respond(f"Something wrong with XBOX API, try again later.")
                logger.error("Something wrong with XBOX API", exc_info=True)


@bot.include
@crescent.command(description="Gets the GamerTag from XUID", guild=793952307103662102)
async def xuid_to_gamertag(ctx, xuid: str):
    await ctx.defer()
    logger.info(f"Received XBOX gamertag: {xuid.strip()}.")
    auth_headers = {"X-Authorization": os.getenv("XBOX_API")}
    async with aiohttp.ClientSession(headers=auth_headers) as session:
        async with session.get(f'https://xbl.io/api/v2/account/{xuid.strip()}') as resp:
            json_response = await resp.json()
            logger.info(f"XBOX API response {json_response}.")
            if profile_list := json_response.get('profileUsers'):
                await ctx.respond(
                    "\n".join(f"{profile['settings'][2]['value']}: {profile['id']}" for profile in profile_list))
            else:
                await ctx.respond(f"XUID {xuid} not found.")


@bot.include
@crescent.command(description="To grab the PSNID of PSN user.", guild=793952307103662102)
async def grab_psnid(ctx, gamer_tag: str):
    logger.info(f"Received PSN gamertag: {gamer_tag.strip()}.")
    try:
        user = psnawp.user(online_id=gamer_tag.strip())
        logger.info(f"Response PSN {user}.")
        await ctx.respond(f"{user.online_id}: {user.account_id}")
    except Exception:
        await ctx.respond(f"GamerTag {gamer_tag} not found.")


@bot.include
@crescent.command(description="Gets the gamertag from PSNID.", guild=793952307103662102)
async def psnid_to_gamertag(ctx, psnid: str):
    logger.info(f"Received PSNID: {psnid.strip()}.")
    try:
        user = psnawp.user(account_id=psnid.strip())
        logger.info(f"Response PSN {user}.")
        await ctx.respond(f"{user.online_id}: {user.account_id}")
    except Exception:
        await ctx.respond(f"PSNID {psnid} not found.")


def main():
    bot.run()


if __name__ == '__main__':
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
