# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.
"""Module that handles Bot PM"""
import re
from userge import userge, Message, Config, get_collection, logging
from userge.utils import get_file_id_and_ref
from pyrogram.types import (  
     InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery )
from pyrogram import filters
from pyrogram.errors import FileIdInvalid, FileReferenceEmpty, BadRequest, ChannelInvalid, MediaEmpty
from datetime import date
import asyncio


CHANNEL = userge.getCLogger(__name__)
_LOG = logging.getLogger(__name__)
BOT_BAN = get_collection("BOT_BAN")
BOT_START = get_collection("BOT_START")
LOGO_ID, LOGO_REF = None, None
_CHAT, _MSG_ID = None, None
_DEFAULT = "https://t.me/DamienSoukara/4"

# refresh file id and file reference from TG server


if userge.has_bot:
    @userge.bot.on_message((filters.private | filters.group) & filters.regex(pattern=r"^/start$"))
    async def start_bot(_, message: Message):
        bot = await userge.bot.get_me()
        master = await userge.get_me()
        u_id = message.from_user.id
        found = await BOT_BAN.find_one({'user_id': u_id})
        if found:
            return
        f_name = message.from_user.first_name
        f_username = message.from_user.username
        u_n = master.username
        hello = f"""
Hello **{f_name}**, 👋
Nice To Meet You, Well I Am **{bot.first_name}**, A Bot.
You Can Talk/Contact My **Owner** Using This Bot.
"""
        if Config.BOT_FORWARDS:          
            hello += "\n<b>✅</b> "
            hello += "**ＢＯＴ ＦＯＲＷＡＲＤＩＮＧ ＩＳ** : 𝗢𝗡\n"
            hello += "All Ur Messages Here Will Be Forwared To My **Owner**"
        if u_id != Config.OWNER_ID:
            found = await BOT_START.find_one({'user_id': u_id})
            if not found:
                today = date.today()
                d2 = today.strftime("%B %d, %Y")
                start_date = d2.replace(',', '')
                u_n = master.username
                BOT_START.insert_one({'firstname': f_name, 'user_id': u_id, 'date': start_date})
                await asyncio.sleep(5)
                log_msg = f"🆕️ A New User Started your Bot \n\n• <i>ID</i>: `{u_id}`\n   👤 : "
                log_msg += f"@{f_username}" if f_username else f_name 
                await CHANNEL.log(log_msg)

        if not (_CHAT and _MSG_ID):
            try:
                _set_data()
            except Exception as set_err:
                _LOG.exception("There was some problem while setting Media Data. "
                                f"trying again... ERROR:: {set_err} ::")
                _set_data(True)
        try:
            await _send_botstart(message, hello, u_n)
        except (FileIdInvalid, FileReferenceEmpty, BadRequest):
            await _refresh_id(message)
            await _send_botstart(message, hello, u_n)

 
    async def _refresh_id(message: Message) -> None:
        global LOGO_ID, LOGO_REF  # pylint: disable=global-statement
        try:
            media = await userge.bot.get_messages(_CHAT, _MSG_ID)
        except ChannelInvalid:
            _set_data(True)
            return await _refresh_id(message)
        LOGO_ID, LOGO_REF = get_file_id_and_ref(media)


    def _set_data(errored: bool = False) -> None:
        global _CHAT, _MSG_ID, _DEFAULT  # pylint: disable=global-statement
        pattern = r"^(http(?:s?):\/\/)?(www\.)?(t.me)(\/c\/(\d+)|:?\/(\w+))?\/(\d+)$"
        if Config.BOT_MEDIA and not errored:
            media_link = Config.BOT_MEDIA
            match = re.search(pattern, media_link)
            if match:
                _MSG_ID = int(match.group(7))
                if match.group(5):
                    _CHAT = int("-100" + match.group(5))
                elif match.group(6):
                    _CHAT = match.group(6)
            elif "|" in Config.BOT_MEDIA:
                _CHAT, _MSG_ID = Config.BOT_MEDIA.split("|", maxsplit=1)
                _CHAT = _CHAT.strip()
                _MSG_ID = int(_MSG_ID.strip())
        else:
            match = re.search(pattern, _DEFAULT)
            _CHAT = match.group(6)
            _MSG_ID = int(match.group(7))
    

    async def _send_botstart(message: Message,
                            caption_text: str,
                            u_n: str,
                            recurs_count: int = 0) -> None:
        if not (LOGO_ID and LOGO_REF):
            await _refresh_id(message)
        try:
            await userge.bot.send_cached_media(
                chat_id=message.chat.id,
                file_id=LOGO_ID, 
                file_ref=LOGO_REF,
                caption=caption_text,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🗣 OWNER", url=f"t.me/{u_n}"),
                    InlineKeyboardButton("💬 CHANNEL", url="t.me/DamienSoukara")],
                    [InlineKeyboardButton("©️ ＬＯＧＩＮ : ＤＡＭＩＥＮ-Ｘ", callback_data="add_to_grp")
                    ]]
                )
            )
        except MediaEmpty:
            if recurs_count >= 2:
                return
            await _refresh_id(message)
            return await _send_botstart(message, caption_text, u_n, recurs_count + 1)


    @userge.bot.on_callback_query(filters.regex(pattern=r"^add_to_grp$"))
    async def add_to_grp(_, callback_query: CallbackQuery): 
        u_id = callback_query.from_user.id 
        if u_id == Config.OWNER_ID:
            botname = (await userge.bot.get_me()).username
            msg = "**✅ Login Successfully :** \n\n <u>Note:</u>  <i>👑 Admin Privilege Required !</i>\n\n<b>⚙ Available Commands :</b> \n\n● /bot_fwd - Enable / Disable Bot Forwards, (Works Only In Bot Pm) \n● /ban - Ban A User From Bot PM [user_id/user_name] Reason Or [Reply To Forwarded Message With Reason] \n● /broadcast - Send A Broadcast Message To Users In Your StartList (Can Work Outside Bot PM)  [Reply To A Message] \n● /unbban -  Unban Users That Are In BotBanList [user_id/user_name] Check bblist For Banned Users. \n● /bblist - Users Banned From Your Bot's PM \n● /users - Get A List Active Users Who Started Your Bot"
            add_bot = f"http://t.me/{botname}?startgroup=start"
            i_bot = f"https://t.me/{botname}?start=inline"
            buttons = [[
                InlineKeyboardButton("🌪 Go Inline", switch_inline_query_current_chat=''),
                InlineKeyboardButton("👨‍💻 Main Menu", callback_data="mm".encode()),
                ],
                [
                InlineKeyboardButton("🧠 Inline Help", url=i_bot),
                InlineKeyboardButton("➕ Press To Add", url=add_bot),
               ]]
            await callback_query.edit_message_text(
                    msg,
                    reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await callback_query.answer("⚠️ ONLY MY OWNER CAN DO THAT ! ⚠️", show_alert=True)


@userge.on_cmd("users", about={
    'header': "Get a list Active Users Who started your Bot",
    'examples': "{tr}users"},
    allow_channels=False)
async def bot_users(message: Message):
    """Users Who Stated Your Bot By : /start"""
    msg = ""
    async for c in BOT_START.find():  
        msg += f"● ID: <code>{c['user_id']}</code>\n   <b>Name:</b> {c['firstname']},  <b>Date:</b> `{c['date']}`\n"
    await message.edit_or_send_as_file(
        f"<u><i><b>Bot PM Userlist</b></i></u>\n\n{msg}" if msg else "`Nobody Does it Better`")
