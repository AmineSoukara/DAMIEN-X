"""Fun plugin"""

import asyncio
from re import search

from pyrogram import filters
from pyrogram.types import CallbackQuery

from userge import Config, Message, userge


@userge.on_cmd("alive", about={"header": "Just For Fun"}, allow_channels=False)
async def alive_inline(message: Message):
    bot = await userge.bot.get_me()
    x = await userge.get_inline_bot_results(bot.username, "alive")
    y = await userge.send_inline_bot_result(
        chat_id=message.chat.id, query_id=x.query_id, result_id=x.results[0].id
    )
    await message.delete()
    await asyncio.sleep(90)
    await userge.delete_messages(message.chat.id, y.updates[0].id)


if userge.has_bot:

    @userge.bot.on_callback_query(filters.regex(pattern=r"^settings_btn$"))
    async def alive_cb(_, callback_query: CallbackQuery):
        if Config.HEROKU_APP:
            dynos_saver = _parse_arg(Config.RUN_DYNO_SAVER)
        else:
            dynos_saver = "Not Supported"
        alive_s = "• ➕ Extra Plugins : {}\n".format(
            _parse_arg(Config.LOAD_UNOFFICIAL_PLUGINS)
        )
        alive_s += f"• 👤 Sudo : {_parse_arg(Config.SUDO_ENABLED)}\n"
        alive_s += f"• ⚠️ AntiSpam : {_parse_arg(Config.ANTISPAM_SENTRY)}\n"
        alive_s += f"• 💾 Dyno Saver : {dynos_saver}\n"
        alive_s += f"• 💬 Bot Forwards : {_parse_arg(Config.BOT_FORWARDS)}\n"
        alive_s += f"• 📝 PM Logger : {_parse_arg(Config.PM_LOGGING)}"
        await callback_query.answer(alive_s, show_alert=True)


def _parse_arg(arg: bool) -> str:
    return " ✅ Enabled" if arg else " ❌ Disabled"


async def check_media_link(media_link: str):
    alive_regex_ = r"http[s]?://(i\.imgur\.com|telegra\.ph/file|t\.me)/(\w+)(?:\.|/)(gif|jpg|png|jpeg|[0-9]+)(?:/([0-9]+))?"
    match = search(alive_regex_, media_link)
    if not match:
        return None, None
    if match.group(1) == "i.imgur.com":
        link = match.group(0)
        link_type = "url_gif" if match.group(3) == "gif" else "url_image"
    elif match.group(1) == "telegra.ph/file":
        link = match.group(0)
        link_type = "url_image"
    else:
        link_type = "tg_media"
        if match.group(2) == "c":
            chat_id = int("-100" + str(match.group(3)))
            message_id = match.group(4)
        else:
            chat_id = match.group(2)
            message_id = match.group(3)
        link = [chat_id, int(message_id)]
    return link_type, link
