import traceback
from dataclasses import dataclass
from logging import getLogger
from os import getenv
from typing import Literal
from urllib.parse import quote

import crescent
import hikari
from aiohttp import ClientSession
from psnawp_api import PSNAWP
from psnawp_api.core.psnawp_exceptions import PSNAWPAuthenticationError, PSNAWPNotFound

from .openxbl_types import People, ProfileUser

plugin = crescent.Plugin[hikari.GatewayBot, None]()
xbox_group = crescent.Group("xbox")
xbox_legacy = crescent.Group(name="xbox_legacy")
playstation_group = crescent.Group("playstation")
gamertag_logger = getLogger("gamertag_id_grabber")


def format_with_ansi(text: str, color_code: int) -> str:
    """Format the input text using ANSI escape characters with the provided color code.

    Args:
        text (str): The text to be formatted.
        color_code (int): The ANSI color code to apply to the text.

    Returns:
        str: The formatted text with ANSI escape characters.
    """
    return f"\x1b[1;{color_code}m{text}\x1b[0m"


@dataclass
class GamerTag:
    """A dataclass representing a gamer tag."""

    username: str
    platform: Literal["PC", "XBOX", "PlayStation"]
    user_id: str
    display_name: str

    # fmt: off
    def __str__(self) -> str:
        return (f"- {self.username}:\n"
                f"  - {self.formatted_platform_color}\n"
                f"  - GamerTagID: {self.user_id}\n"
                f"  - Display Name: {self.display_name}\n")
    # fmt: on

    @property
    def formatted_platform_color(self) -> str:
        if self.platform == "XBOX":
            return format_with_ansi(f"Platform: {self.platform}", 32)
        elif self.platform == "PlayStation":
            return format_with_ansi(f"Platform: {self.platform}", 34)
        else:
            return format_with_ansi(f"Platform: {self.platform}", 31)


@plugin.include
@xbox_group.child
@crescent.command(name="get_xuid", description="Get XUID of XBOX Gamertag", guild=793952307103662102)
class XUID:
    gamer_tag = crescent.option(str, description="XBOX GamerTag")

    async def callback(self, ctx: crescent.Context) -> None:
        gamertag_logger.info(f"xbox get_xuid: {self.gamer_tag}")
        await ctx.defer()
        profile_list = await self.xbox_gamertag_to_xuid(self.gamer_tag)
        tmp = "".join(profile_list) if len(profile_list) else f"Could not find gamertag {self.gamer_tag}."
        await ctx.respond(f"```ansi\n{tmp}```")

    @staticmethod
    async def xbox_gamertag_to_xuid(gamertag: str) -> list[str]:
        auth_headers = {"X-Authorization": getenv("OPENXBL_API", "OPENXBL_API"), "Content-Type": "application/json"}

        async with (
            ClientSession(headers=auth_headers) as session,
            session.get(f"https://xbl.io/api/v2/search/{quote(gamertag)}") as resp,
        ):
            if resp.status != 200:
                return []

            json_response = await resp.json()
            profile_list: list[People] = json_response.get("people", [])
            return [
                str(
                    GamerTag(
                        username=profile["gamertag"],
                        platform="XBOX",
                        user_id=profile["xuid"],
                        display_name=profile["uniqueModernGamertag"],
                    )
                )
                for profile in profile_list[:10]
            ]


@plugin.include
@xbox_legacy.child
@crescent.command(name="get_xuid", description="Get XUID of XBOX 360 Gamertag", guild=793952307103662102)
class XUID360:
    gamer_tag = crescent.option(str, description="XBOX 360 GamerTag")

    async def callback(self, ctx: crescent.Context) -> None:
        gamertag_logger.info(f"xbox_legacy get_xuid: {self.gamer_tag}")
        await ctx.defer()
        profile_list = await self.xbox_gamertag_to_xuid(self.gamer_tag)
        tmp = "".join(profile_list) if len(profile_list) else f"Could not find gamertag {self.gamer_tag}."
        await ctx.respond(f"```ansi\n{tmp}```")

    @staticmethod
    async def xbox_gamertag_to_xuid(gamertag: str) -> list[str]:
        auth_headers = {"X-Authorization": getenv("OPENXBL_API", "OPENXBL_API"), "Content-Type": "application/json"}

        async with (
            ClientSession(headers=auth_headers) as session,
            session.get(f"https://xbl.io/api/v2/friends/search/{quote(gamertag)}") as resp,
        ):
            if resp.status != 200:
                return []

            json_response = await resp.json()
            profile_list: list[ProfileUser] = json_response.get("profileUsers", [])
            return [
                str(
                    GamerTag(
                        username=profile["settings"][2]["value"],
                        platform="XBOX",
                        user_id=profile["id"],
                        display_name="N/A",
                    )
                )
                for profile in profile_list[:10]
            ]


@plugin.include
@xbox_group.child
@crescent.command(name="get_gamertag", description="Get XBOX Gamertag from XUID", guild=793952307103662102)
class XBOXGamerTag:
    xuid = crescent.option(int, description="XBOX User ID")

    async def callback(self, ctx: crescent.Context) -> None:
        gamertag_logger.info(f"xbox get_gamertag: {self.xuid}")
        await ctx.defer()
        auth_headers = {"X-Authorization": getenv("OPENXBL_API", "OPENXBL_API"), "Content-Type": "application/json"}
        async with (
            ClientSession(headers=auth_headers) as session,
            session.get(f"https://xbl.io/api/v2/account/{self.xuid}") as resp,
        ):
            json_response = await resp.json()
            if profile_list := json_response.get("profileUsers"):
                tmp = "".join(
                    [
                        str(
                            GamerTag(
                                username=profile["settings"][2]["value"],
                                platform="XBOX",
                                user_id=profile["id"],
                                display_name="N/A",
                            )
                        )
                        for profile in profile_list[:10]
                    ]
                )
                await ctx.respond(f"```ansi\n{tmp}```")
            else:
                await ctx.respond(f"XUID {self.xuid} not found.")


@plugin.include
@playstation_group.child
@crescent.command(name="get_psnid", description="Get PSNID of PlayStation Gamertag", guild=793952307103662102)
class PSNID:
    gamer_tag = crescent.option(str, description="PlayStation GamerTag")

    async def callback(self, ctx: crescent.Context) -> None:
        gamertag_logger.info(f"playstation get_psnid: {self.gamer_tag}")
        await ctx.defer()
        try:
            psnawp = PSNAWP(getenv("NPSSO_CODE", "NPSSO_CODE"))
            user = psnawp.user(online_id=self.gamer_tag)
            tmp = str(GamerTag(username=self.gamer_tag, platform="PlayStation", user_id=user.account_id, display_name=user.online_id))
            await ctx.respond(f"```ansi\n{tmp}```")
        except PSNAWPNotFound:
            await ctx.respond(f"Could not find gamertag {self.gamer_tag}.")
        except PSNAWPAuthenticationError:
            traceback.print_exc()
            await ctx.respond(traceback.format_exc(1))


@plugin.include
@playstation_group.child
@crescent.command(name="get_gamertag", description="Get PlayStation Gamertag from PSNID", guild=793952307103662102)
class PlayStationGamerTag:
    psnid = crescent.option(int, description="PlayStation User ID")

    async def callback(self, ctx: crescent.Context) -> None:
        gamertag_logger.info(f"playstation get_gamertag: {self.psnid}")
        await ctx.defer()
        try:
            psnawp = PSNAWP(getenv("NPSSO_CODE", "NPSSO_CODE"))
            user = psnawp.user(account_id=f"{self.psnid}")
            tmp = str(GamerTag(username=user.online_id, platform="PlayStation", user_id=user.account_id, display_name=user.online_id))
            await ctx.respond(f"```ansi\n{tmp}```")
        except PSNAWPNotFound:
            await ctx.respond(f"PSNID {self.psnid} not found.")
        except Exception:
            traceback.print_exc()
            await ctx.respond(traceback.format_exc(1))
