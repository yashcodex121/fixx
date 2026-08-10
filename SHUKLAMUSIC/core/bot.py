# -----------------------------------------------
# 🔸 StrangerMusic Project
# 🔹 Developed & Maintained by: Shashank Shukla (https://github.com/itzshukla)
# 📅 Copyright © 2022 – All Rights Reserved
#
# 📖 License:
# This source code is open for educational and non-commercial use ONLY.
# You are required to retain this credit in all copies or substantial portions of this file.
# Commercial use, redistribution, or removal of this notice is strictly prohibited
# without prior written permission from the author.
#
# ❤️ Made with dedication and love by ItzShukla
# -----------------------------------------------

import sys

# Optional uvloop
if sys.platform != "win32":
    try:
        import uvloop
        uvloop.install()
        print("✓ uvloop enabled")
    except ImportError:
        print("⚠ uvloop not installed, using default asyncio loop")

from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus
import config
from ..logging import LOGGER


class SHUKLA(Client):
    def __init__(self):
        LOGGER(__name__).info("Starting Bot...")

        super().__init__(
            name="SHUKLAMUSIC",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()

        me = await self.get_me()

        self.id = me.id
        self.name = f"{me.first_name} {me.last_name or ''}".strip()
        self.username = me.username or "None"
        self.mention = me.mention

        try:
            await self.send_message(
                chat_id=config.LOGGER_ID,
                text=(
                    f"<u><b>» {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b></u>\n\n"
                    f"ɪᴅ : <code>{self.id}</code>\n"
                    f"ɴᴀᴍᴇ : {self.name}\n"
                    f"ᴜsᴇʀɴᴀᴍᴇ : @{self.username}"
                ),
            )

        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).error(
                "Bot cannot access LOGGER_ID. Add the bot to the log group/channel."
            )
            raise SystemExit(1)

        except Exception as ex:
            LOGGER(__name__).error(
                f"Failed to access LOGGER_ID: {type(ex).__name__}: {ex}"
            )
            raise SystemExit(1)

        try:
            member = await self.get_chat_member(
                config.LOGGER_ID,
                self.id
            )

            if member.status not in (
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER,
            ):
                LOGGER(__name__).error(
                    "Promote the bot as admin in LOGGER_ID."
                )
                raise SystemExit(1)

        except Exception as ex:
            LOGGER(__name__).error(
                f"Failed checking admin status: {type(ex).__name__}: {ex}"
            )
            raise SystemExit(1)

        LOGGER(__name__).info(
            f"Music Bot Started Successfully as {self.name}"
        )

    async def stop(self):
        LOGGER(__name__).info("Stopping Bot...")
        await super().stop()
