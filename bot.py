import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

from info import BOT_TOKEN, BRANDING_TEXT, ADMINS, FILE_STORE_CHANNELS, LOG_CHANNEL, AUTO_DELETE_TIME, AUTH_CHANNEL
from ads import get_verify_link, get_tutorial_link, update_links, save_user_data, log_to_channel
from pymongo import MongoClient
from info import MONGO_URI_MAIN

client_db = MongoClient(MONGO_URI_MAIN)
db = client_db["vjbot"]
channels_col = db["channels"]

bot = Client("VJ-FILTER-BOT", bot_token=BOT_TOKEN)

# --------------------- Utility ---------------------
async def is_approved_chat(chat_id):
    approved = channels_col.find_one({"_id": "channels", "approved": chat_id})
    return approved or chat_id in FILE_STORE_CHANNELS

async def check_auth_channel(user_id):
    if not AUTH_CHANNEL:
        return True
    try:
        member = await bot.get_chat_member(AUTH_CHANNEL, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except UserNotParticipant:
        return False
    except:
        return False
    return False

# --------------------- /start ---------------------
@bot.on_message(filters.command("start"))
async def start(_, m):
    save_user_data(m.from_user.id, {"last_action": "start"})
    await m.reply_text(
        "Welcome!\nSearch your series or movie...",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Jacpotfilm", url="https://jacpotfilm.link")]
        ])
    )

# --------------------- Search ---------------------
@bot.on_message(filters.text & ~filters.command("start"))
async def search_handler(_, m):
    if not await is_approved_chat(m.chat.id) and m.chat.type != "private":
        return
    save_user_data(m.from_user.id, {"last_action": "search", "chat_id": m.chat.id, "query": m.text})
    await log_to_channel(bot, f"User {m.from_user.id} searched '{m.text}' in chat {m.chat.id}")
    await m.reply_text(
        f"Select season for {m.text}:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Season 1", callback_data="season1")],
            [InlineKeyboardButton("Season 2", callback_data="season2")]
        ])
    )

# --------------------- Season Callback ---------------------
@bot.on_callback_query(filters.regex("season"))
async def season_handler(_, q):
    save_user_data(q.from_user.id, {"last_action": "season", "season": q.data})
    await log_to_channel(bot, f"User {q.from_user.id} selected {q.data} in chat {q.message.chat.id}")
    await q.message.edit_text(
        f"Select episode:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Episode 1", callback_data="ep1")],
            [InlineKeyboardButton("Episode 2", callback_data="ep2")]
        ])
    )

# --------------------- Episode Callback ---------------------
@bot.on_callback_query(filters.regex("ep"))
async def episode_handler(_, q):
    user_id = q.from_user.id
    
    # Auth check
    if not await check_auth_channel(user_id):
        join_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("Join Channel", url=f"https://t.me/{str(AUTH_CHANNEL).replace('-100','')}")],
            [InlineKeyboardButton("Try Again", callback_data=q.data)]
        ])
        await q.message.edit_text("❌ You must join our channel first to access videos!", reply_markup=join_button)
        return

    # Normal flow
    ep = q.data.upper()
    verify_link = get_verify_link()
    tutorial = get_tutorial_link()

    buttons = [[InlineKeyboardButton("Verify Link", url=verify_link)]]
    if tutorial:
        buttons.append([InlineKeyboardButton("Tutorial", url=tutorial)])
    buttons.append([InlineKeyboardButton("Copy Link", switch_inline_query_current_chat=verify_link)])

    await q.message.edit_text(
        f"{ep}              {BRANDING_TEXT}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# --------------------- Admin Commands ---------------------
@bot.on_message(filters.command("ads.link") & filters.user(ADMINS))
async def set_verify_link(_, m):
    await m.reply_text("Send the new verify link:")
    new_msg = await bot.listen(m.chat.id, filters=filters.text & filters.user(ADMINS))
    update_links(verify_link=new_msg.text.strip())
    await m.reply_text(f"Verify link updated:\n{new_msg.text.strip()}")

@bot.on_message(filters.command("tutorial.link") & filters.user(ADMINS))
async def set_tutorial_link(_, m):
    await m.reply_text("Send the new tutorial link:")
    new_msg = await bot.listen(m.chat.id, filters=filters.text & filters.user(ADMINS))
    update_links(tutorial_link=new_msg.text.strip())
    await m.reply_text(f"Tutorial link updated:\n{new_msg.text.strip()}")

# --------------------- Connect / Approve / Disconnect ---------------------
@bot.on_message(filters.command("connect") & filters.user(ADMINS))
async def connect_channel(_, m):
    channel_id = int(m.text.split()[1])
    channels_col.update_one({"_id": "channels"}, {"$addToSet": {"pending": channel_id}}, upsert=True)
    await m.reply_text(f"Channel {channel_id} added to pending approval.")

@bot.on_message(filters.command("approve") & filters.user(ADMINS))
async def approve_channel(_, m):
    channel_id = int(m.text.split()[1])
    channels_col.update_one({"_id": "channels"}, {"$pull": {"pending": channel_id}, "$addToSet": {"approved": channel_id}}, upsert=True)
    await m.reply_text(f"Channel {channel_id} approved!")

@bot.on_message(filters.command("disconnect") & filters.user(ADMINS))
async def disconnect_channel(_, m):
    channel_id = int(m.text.split()[1])
    channels_col.update_one({"_id": "channels"}, {"$pull": {"approved": channel_id}}, upsert=True)
    await m.reply_text(f"Channel {channel_id} disconnected.")

# --------------------- Start Bot ---------------------
print("Bot started...")
bot.run()
