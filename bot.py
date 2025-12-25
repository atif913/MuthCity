# (©)Codexbotz

from aiohttp import web
from plugins import web_server

import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import sys
from datetime import datetime

from config import (
    API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS,
    FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL_2, CHANNEL_ID, PORT
)

ascii_art = """
░█████╗░░█████╗░██████╗░███████╗██╗░░██╗██████╗░░█████╗░████████╗███████╗
██╔══██╗██╔══██╗██╔══██╗██╔════╝╚██╗██╔╝██╔══██╗██╔══██╗╚══██╔══╝╚════██║
██║░░╚═╝██║░░██║██║░░██║█████╗░░░╚███╔╝░██████╦╝██║░░██║░░░██║░░░░░███╔═╝
██║░░██╗██║░░██║██║░░██║██╔══╝░░░██╔██╗░██╔══██╗██║░░██║░░░██║░░░██╔══╝░░
╚█████╔╝╚█████╔╝██████╔╝███████╗██╔╝╚██╗██████╦╝╚█████╔╝░░░██║░░░███████╗
░╚════╝░░╚════╝░╚═════╝░╚══════╝╚═╝░░╚═╝╚═════╝░░╚════╝░░░░╚═╝░░░╚══════╝
"""

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        # --------- FORCE SUB CHANNEL 1 ----------
        if FORCE_SUB_CHANNEL:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                self.invitelink = link
            except Exception as e:
                self.LOGGER(__name__).warning(e)
                self.LOGGER(__name__).warning(
                    "Bot can't export invite link from Force Sub Channel 1! "
                    f"Check FORCE_SUB_CHANNEL value ({FORCE_SUB_CHANNEL}) "
                    "and ensure bot is admin with Invite Users permission."
                )
                sys.exit()

        # --------- FORCE SUB CHANNEL 2 ----------
        if FORCE_SUB_CHANNEL_2:
            try:
                link2 = (await self.get_chat(FORCE_SUB_CHANNEL_2)).invite_link
                if not link2:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL_2)
                    link2 = (await self.get_chat(FORCE_SUB_CHANNEL_2)).invite_link
                self.invitelink2 = link2
            except Exception as e:
                self.LOGGER(__name__).warning(e)
                self.LOGGER(__name__).warning(
                    "Bot can't export invite link from Force Sub Channel 2! "
                    f"Check FORCE_SUB_CHANNEL_2 value ({FORCE_SUB_CHANNEL_2}) "
                    "and ensure bot is admin with Invite Users permission."
                )
                sys.exit()

        # --------- DB CHANNEL CHECK ----------
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(
                f"Make sure bot is Admin in DB Channel ({CHANNEL_ID})."
            )
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(
            f"Bot Running..!\n\nCreated by \nhttps://t.me/CodeXBotz"
        )
        print(ascii_art)
        print("Welcome to CodeXBotz File Sharing Bot")
        self.username = usr_bot_me.username

        # --------- WEB SERVER ---------
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()

    async def check_force_sub(self, message):
        user_id = message.from_user.id

        # Check Channel 1
        if FORCE_SUB_CHANNEL:
            try:
                await self.get_chat_member(FORCE_SUB_CHANNEL, user_id)
            except UserNotParticipant:
                return await message.reply(
                    "Please join Channel 1 to continue.",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Join Channel 1", url=self.invitelink)]]
                    )
                )

        # Check Channel 2
        if FORCE_SUB_CHANNEL_2:
            try:
                await self.get_chat_member(FORCE_SUB_CHANNEL_2, user_id)
            except UserNotParticipant:
                return await message.reply(
                    "Please join Channel 2 to continue.",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Join Channel 2", url=self.invitelink2)]]
                    )
                )

        return True

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")