import os
import time
import logging
import pyrogram
import aiohttp
import requests
import aiofiles
from random import randint
from progress import progress
from config import Config
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InlineQuery, InputTextMessageContent

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

DOWNLOAD = "./"


APP_ID = Config.APP_ID
API_HASH = Config.API_HASH
BOT_TOKEN = Config.BOT_TOKEN

   
OC_AnonFilesBot = Client(
    "AnonFilesBot",
    api_id=APP_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN)


START_TEXT = """
<b>Hey There,
I can upload any media files to __Anonfile.com__


Hit 'How To Use' button to find out more about how to use me</b>
"""

START_BUTTONS = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('How To Use', callback_data='help')
        ]]
    )

HELP_BUTTONS = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('Home', callback_data='home'),
        ]]
    )
HELP_TEXT = """
AnonFilesBot Help!

Send me any media file, I will upload it to anonfiles.com and give the download link
"""


@OC_AnonFilesBot.on_message(filters.command(["start"]))
async def start(bot, update):
    text = START_TEXT
    reply_markup = START_BUTTONS
    await update.reply_text(
        text=text,
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )

@OC_AnonFilesBot.on_message(filters.channel & (filters.document | filters.video | filters.audio ) & ~filters.edited, group=-1)
async def upload(client, message):
    file_caption = f"{message.caption}" 
    m = await message.edit(file_caption + "\n" + "━━━━━━━━━━━━━━━━━━━" + "\n"  + "`Uploading to filechan`")
    now = time.time()
    sed = await OC_AnonFilesBot.download_media(
                message, DOWNLOAD,
          progress=progress,
          progress_args=(
            file_caption + "\n" "━━━━━━━━━━━━━━━━━━━" + "\n" + "`Uploading to filechan` \n\n**ETA:** ", 
            m,
            now
            )
        )
    try:
        files = {'file': open(sed, 'rb')}
        await m.edit(file_caption + "\n" "━━━━━━━━━━━━━━━━━━━" + "\n" + "`Generating Link`**")
        callapi = requests.post("https://api.filechan.org/upload", files=files)
        text = callapi.json()
        output = f"""
{file_caption}
━━━━━━━━━━━━━━━━━━━
[🔗Download Link]({text['data']['file']['url']['full']}`)"""
        btn = InlineKeyboardMarkup(
                                [[InlineKeyboardButton("📥 𝘿𝙤𝙬𝙣𝙡𝙤𝙖𝙙 📥", url=f"{text['data']['file']['url']['full']}")]])
        await m.edit(output)
    except Exception:
        OC_AnonFilesBot.send_message(message.chat.id, text="Something Went Wrong!")
       
    os.remove(sed)



@OC_AnonFilesBot.on_callback_query()
async def cb_data(bot, update):
    if update.data == "home":
        await update.message.edit_text(
            text=START_TEXT,
            disable_web_page_preview=True,
            reply_markup=START_BUTTONS
        )
    elif update.data == "help":
        await update.message.edit_text(
            text=HELP_TEXT,
            disable_web_page_preview=True,
            reply_markup=HELP_BUTTONS
        )
    else:
        await update.message.delete()

OC_AnonFilesBot.start()
print("""AnonFilesBot Is Started!
Send me any media file, I will upload it to anonfiles.com and give the download link
""")
idle()
