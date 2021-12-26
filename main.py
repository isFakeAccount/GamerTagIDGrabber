import os
from time import strftime

import psnawp_api
import requests
from pincer import Client
from pincer.commands import command
from pincer.objects import MessageContext


class GamerTagIDGrabber(Client):
    def __init__(self, token: str, psnawp):
        super().__init__(token)
        self.psnawp = psnawp

    @Client.event
    async def on_ready(self):
        print(f"Logged in as {self.bot} at {strftime('%m/%d/%Y %H:%M:%S %Z')}.")

    @command(name="xuid", description="Get XUID from XBOX GamerTag", guild="793952307103662102")
    async def grab_xuid(self, ctx: MessageContext, gamer_tag: str):
        if ctx.channel_id == 924193319507079238:
            auth_headers = {"X-Authorization": os.getenv("XBOX_API")}
            params = {'gt': gamer_tag.strip()}
            response = requests.get('https://xbl.io/api/v2/friends/search', headers=auth_headers, params=params)
            json_response = response.json()
            if profile_list := json_response.get('profileUsers'):
                await ctx.reply("\n".join(f"{profile['settings'][2]['value']}: {profile['id']}" for profile in profile_list))
            else:
                await ctx.reply(f"GamerTag {gamer_tag} not found.")
        else:
            await ctx.reply("The command only works in the #gamer-tag-id-grabber channel.")

    @command(name="psnid", description="Get PSNID from XBOX GamerTag", guild="793952307103662102")
    async def grab_psnid(self, ctx: MessageContext, gamer_tag: str):
        if ctx.channel_id == 924193319507079238:
            try:
                user = self.psnawp.user(online_id=gamer_tag)
                await ctx.reply(f"{user.online_id}: {user.account_id}")
            except Exception:
                await ctx.reply(f"GamerTag {gamer_tag} not found.")
        else:
            await ctx.reply("The command only works in the #gamer-tag-id-grabber channel.")


def main():
    psnawp = psnawp_api.psnawp.PSNAWP(os.getenv('NPSSO_CODE'))
    bot = GamerTagIDGrabber(os.getenv("TOKEN"), psnawp)
    bot.run()


if __name__ == '__main__':
    main()
