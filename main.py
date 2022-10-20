import json
import logging
import os
import re
import traceback
from typing import Annotated as Atd
from typing import Optional

import aiohttp
import crescent
from aiohttp import ClientSession
from dotenv import load_dotenv
from psnawp_api import PSNAWP
from psnawp_api.core.psnawp_exceptions import PSNAWPNotFound, PSNAWPAuthenticationError

load_dotenv('config.env')
bot = crescent.Bot(os.getenv('TOKEN'))
ROOT_URI = f"https://database.deta.sh/v1/{os.getenv('PROJECT_ID')}/fallout_76_db"


async def xbox_gamertag_to_xuid(gamertag):
    auth_headers = {"X-Authorization": os.getenv("XBOX_API"), "Content-Type": "application/json"}
    params = {'gt': gamertag}
    # Retries the search two times before giving up.
    for i in range(2):
        async with aiohttp.ClientSession(headers=auth_headers) as session:
            async with session.get('https://xbl.io/api/v2/friends/search', params=params) as resp:
                json_response = await resp.json()
                logger.info(f"XBOX API response {json_response}.")
                if json_response.get('code') == 28:
                    break
                if profile_list := json_response.get('profileUsers'):
                    return [(profile['settings'][2]['value'], profile['id']) for profile in profile_list]
    return []


@bot.include
@crescent.command(description="To grab the XUID of XBOX user.", guild=793952307103662102)
async def grab_xuid(ctx: crescent.Context, gamer_tag: Atd[str, "XBOX 360 GamerTag"]):
    await ctx.defer()
    logger.info(f"Received XBOX gamertag: {gamer_tag}.")

    if not re.match(r"[A-Za-z0-9 ]+$", gamer_tag):
        await ctx.respond(f"{gamer_tag} is not XBOX 360 compatible GamerTag")
        return

    try:
        profile_list = await xbox_gamertag_to_xuid(gamer_tag)
        if profile_list:
            await ctx.respond('\n'.join([f"{x[0]}: {x[1]}" for x in profile_list]))
        else:
            await ctx.respond(f"Could not find the gamertag {gamer_tag}")
    except aiohttp.ContentTypeError:
        await ctx.respond(f"XBOX API Error, Try again.")


@bot.include
@crescent.command(description="Gets the GamerTag from XUID", guild=793952307103662102)
async def xuid_to_gamertag(ctx: crescent.Context, xuid: Atd[int, "XBOX User ID"]):
    await ctx.defer()
    logger.info(f"Received XBOX gamertag: {xuid}.")
    auth_headers = {"X-Authorization": os.getenv("XBOX_API")}
    async with aiohttp.ClientSession(headers=auth_headers) as session:
        async with session.get(f'https://xbl.io/api/v2/account/{xuid}') as resp:
            json_response = await resp.json()
            logger.info(f"XBOX API response {json_response}.")
            if profile_list := json_response.get('profileUsers'):
                await ctx.respond(
                    "\n".join(f"{profile['settings'][2]['value']}: {profile['id']}" for profile in profile_list))
            else:
                await ctx.respond(f"XUID {xuid} not found.")


@bot.include
@crescent.command(description="To grab the PSNID of PSN user.", guild=793952307103662102)
async def grab_psnid(ctx: crescent.Context, gamer_tag: Atd[str, "PlayStation GamerTag"]):
    logger.info(f"Received PSN gamertag: {gamer_tag}.")
    try:
        user = psnawp.user(online_id=gamer_tag)
        logger.info(f"Response PSN {user}.")
        await ctx.respond(f"{user.online_id}: {user.account_id}")
    except PSNAWPNotFound:
        await ctx.respond(f"GamerTag {gamer_tag} not found.")
    except PSNAWPAuthenticationError:
        traceback.print_exc()
        await ctx.respond(traceback.format_exc(1))


@bot.include
@crescent.command(description="Gets the gamertag from PSNID.", guild=793952307103662102)
async def psnid_to_gamertag(ctx: crescent.Context, psnid: Atd[str, "PlayStation User ID"]):
    if not re.match(r"\d+", psnid):
        await ctx.respond(f"{psnid} is not correct PSN ID.")
        return

    logger.info(f"Received PSNID: {psnid}.")
    try:
        user = psnawp.user(account_id=f"{psnid}")
        logger.info(f"Response PSN {user}.")
        await ctx.respond(f"{user.online_id}: {user.account_id}")
    except PSNAWPNotFound:
        await ctx.respond(f"PSNID {psnid} not found.")
    except Exception:
        traceback.print_exc()
        await ctx.respond(traceback.format_exc(1))


async def get_item(key: str):
    async with ClientSession(headers={"X-API-Key": os.getenv("PROJECT_KEY"), 'Content-Type': 'application/json'}) as session:
        async with session.get(f"{ROOT_URI}/items/{key}") as resp:
            json_data = await resp.json()
            return json_data


async def query_items(key: str, value: str):
    async with ClientSession(headers={"X-API-Key": os.getenv("PROJECT_KEY"), 'Content-Type': 'application/json'}) as session:
        payload = json.dumps({"query": [{key: value}], "limit": 5, "last": None})
        async with session.post(f"{ROOT_URI}/query", data=payload) as resp:
            json_data = await resp.json()
            return json_data.get("items")


async def update_items(data: dict):
    async with ClientSession(headers={"X-API-Key": os.getenv("PROJECT_KEY"), 'Content-Type': 'application/json'}) as session:
        payload = json.dumps({"items": [data]})
        async with session.put(f"{ROOT_URI}/items", data=payload) as resp:
            json_data = await resp.json()
            return json_data.get("items")


@bot.include
@crescent.command(description="Sets the is_blacklisted field of db to true or false.", guild=793952307103662102)
async def set_blacklisted(ctx: crescent.Context, reddit: Atd[str, "Reddit Username"], value: Atd[bool, "Whether to set the user as blacklisted or not."]):
    profile_data = await get_item(reddit)
    profile_data["is_blacklisted"] = value
    await update_items(profile_data)
    await ctx.respond(f"u/{reddit} is_blacklisted {value}")


@bot.include
@crescent.command(description="Deletes the Reddit user from database. Use this command with caution.", guild=793952307103662102)
async def delete_reddit_user(ctx: crescent.Context, reddit: Atd[str, "Reddit Username"]):
    root_uri = f"https://database.deta.sh/v1/{os.getenv('PROJECT_ID')}/fallout_76_db"
    async with ClientSession(headers={"X-API-Key": os.getenv("PROJECT_KEY"), 'Content-Type': 'application/json'}) as session:
        async with session.delete(f"{root_uri}/items/{reddit.lower()}") as resp:
            json_data = await resp.json()
            formatted_json = \
                f"""
                ```json\n{json.dumps(json_data, sort_keys=True, indent=4)}
                ```
                """
            await ctx.respond(formatted_json)


@bot.include
@crescent.command(description="Grabs user info from user verification database", guild=793952307103662102)
async def grab_user_info(ctx: crescent.Context,
                         reddit: Atd[Optional[str], "Reddit Username"] = None,
                         psn: Atd[Optional[str], "PlayStation GamerTag"] = None,
                         psnid: Atd[Optional[str], "PlayStation User ID"] = None,
                         xbl: Atd[Optional[str], "XBOX 360 GamerTag"] = None,
                         xuid: Atd[Optional[str], "XBOX User ID"] = None,
                         pc: Atd[Optional[str], "Reddit Username"] = None):
    await ctx.defer()
    if reddit is not None:
        result = await get_item(reddit.lower())
    elif psn is not None:
        try:
            user = psnawp.user(online_id=psn)
            result = await query_items(key="PlayStation", value=user.online_id)
        except (PSNAWPNotFound, PSNAWPAuthenticationError):
            result = await query_items(key="PlayStation", value=psn)
    elif psnid is not None:
        result = await query_items(key="PlayStation_ID", value=psnid)
    elif xbl is not None:
        try:
            xb_xuid = await xbox_gamertag_to_xuid(xbl)
        except Exception:
            xb_xuid = None
        if xb_xuid:
            result = await query_items(key="XBOX", value=xb_xuid[0][0])
        else:
            result = await query_items(key="XBOX", value=xbl)
    elif xuid is not None:
        result = await query_items(key="XBOX_ID", value=xuid)
    elif pc is not None:
        result = await query_items(key="Fallout 76", value=pc)
    else:
        result = "Nothing was passed as argument."

    formatted_json = \
        f"""
        ```json\n{json.dumps(result, sort_keys=True, indent=4)}
        ```
        """
    await ctx.respond(formatted_json)


def main():
    bot.run()


if __name__ == '__main__':
    psnawp = PSNAWP(os.getenv('NPSSO_CODE'))
    logger = logging.getLogger("GammerTagIDGrabber")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    log_stream = logging.StreamHandler()
    log_stream.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s')
    log_stream.setFormatter(formatter)
    logger.addHandler(log_stream)

    client = psnawp.me()
    logger.info(f"Logged in as PSN ID: {client.online_id}.")
    main()
