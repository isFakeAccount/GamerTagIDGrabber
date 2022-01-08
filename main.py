import os

import discord
import psnawp_api
import requests
from dotenv import load_dotenv

bot = discord.Bot()


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.slash_command(guild_ids=[793952307103662102])
async def grab_xuid(ctx, gamer_tag: str):
    if ctx.channel_id == 924193319507079238:
        auth_headers = {"X-Authorization": os.getenv("XBOX_API")}
        params = {'gt': gamer_tag.strip()}
        response = requests.get('https://xbl.io/api/v2/friends/search', headers=auth_headers, params=params)
        json_response = response.json()
        if profile_list := json_response.get('profileUsers'):
            await ctx.respond(
                "\n".join(f"{profile['settings'][2]['value']}: {profile['id']}" for profile in profile_list))
        else:
            await ctx.respond(f"GamerTag {gamer_tag} not found.")
    else:
        await ctx.respond("The command only works in the #gamer-tag-id-grabber channel.")


@bot.slash_command(guild_ids=[793952307103662102])
async def grab_psnid(ctx, gamer_tag: str):
    if ctx.channel_id == 924193319507079238:
        try:
            user = psnawp.user(online_id=gamer_tag)
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
    main()
