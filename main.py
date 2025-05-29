import logging
import time
import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Bot configuration
API_ID = 28837889
API_HASH = "9d5e9c5b8abcf8b7b930abd259de254e"
BOT_TOKEN = "your_bot_token"
BOT_USERNAME = "Copyright_bypasser_Bot"
OWNER_ID = 7577853954
OWNER_USERNAME = "@whosekirito"

app = Client("text_terminator", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Databases
gban_users = set()
authorized_users = set()
active_groups = set()
active_users = set()
message_store = {}
edit_delete_delay = 300  # Default: 5 minutes

# Forbidden keywords
FORBIDDEN_KEYWORDS = ["porn", "xxx", "sex", "NCERT", "XII", "page", "Ans"]

# Random start images
START_IMAGES = [
    "https://te.legra.ph/file/91f7216bb3be22f56531f-739148697cae01723a.jpg",
    "https://te.legra.ph/file/256cee3fd6df57154b60c-a44015b807a066e5f0.jpg",
    "https://te.legra.ph/file/17e3f2924a6860af68df8-9f0a23409cf1ff7b63.jpg",
    "https://te.legra.ph/file/f54fc67bf2129d8f4dd77-75ebfc809d1dc23972.jpg"
]

# Start command
@app.on_message(filters.command("start"))
async def start(_, msg):
    buttons = [
        [InlineKeyboardButton("➕ Add Me", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        [
            InlineKeyboardButton("💸 Donate", url="https://t.me/Kirito_Bots/10"),
            InlineKeyboardButton("👑 Owner", url=f"https://t.me/{OWNER_USERNAME[1:]}")
        ],
        [
            InlineKeyboardButton("💬 Support", url="https://t.me/whosekirito_Support"),
            InlineKeyboardButton("📢 Updates", url="https://t.me/Kirito_Bots")
        ]
    ]
    if msg.chat.type == "private":
        active_users.add(msg.chat.id)
        await msg.reply_photo(
            photo=random.choice(START_IMAGES),
            caption="<b>˹ Rᴏxʏ Cᴏᴘʏʀɪɢʜᴛ Bʏᴘᴀssᴇʀ ˼</b>\n\n⚡ 
Wᴇʟᴄᴏᴍᴇ I ᴀᴍ Rᴏxʏ Cᴏᴘʏʀɪɢʜᴛ Bʏᴘᴀssᴇʀ ᴡʜɪᴄʜ ᴅᴇᴛᴇᴄᴛs ᴄᴏᴘʏʀɪɢʜᴛ ᴍᴀᴛᴇʀɪᴀʟ ᴀɴᴅ ᴀᴜᴛᴏᴅᴇʟᴇᴛᴇs ɪᴛ.⚡.   ⚡ Hᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ: Aᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ɢɪᴠᴇ ᴍᴏᴅᴇʀᴀᴛᴏʀ ʀɪɢʜᴛs ✨ ",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        active_groups.add(msg.chat.id)
        await msg.reply("✅ Bot activated! All protections enabled.")

# GBAN
@app.on_message(filters.command("gban") & filters.user(OWNER_ID))
async def global_ban(_, message: Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        gban_users.add(user_id)
        await message.reply(f"🚫 User {user_id} globally banned!")
    else:
        await message.reply("❌ Reply to a user's message to ban them!")

# Broadcast
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(_, message: Message):
    if not message.reply_to_message:
        await message.reply("❌ Please reply to a message to broadcast")
        return

    broadcast_msg = message.reply_to_message
    total = failed = 0
    progress = await message.reply("📢 Starting broadcast...")

    for group in active_groups:
        try:
            await broadcast_msg.copy(group)
            total += 1
            await asyncio.sleep(0.5)
        except Exception as e:
            logging.error(f"Failed to send to {group}: {e}")
            failed += 1

    for user in active_users:
        try:
            await broadcast_msg.copy(user)
            total += 1
            await asyncio.sleep(0.5)
        except:
            failed += 1

    await progress.edit_text(f"✅ Broadcast complete!\n\n• Sent: {total}\n• Failed: {failed}")

# Forbidden keywords
@app.on_message(filters.group)
async def handle_message(_, message: Message):
    if message.chat.id not in active_groups:
        active_groups.add(message.chat.id)

    message_store[message.id] = {
        "chat_id": message.chat.id,
        "time": time.time()
    }

    if message.from_user and message.from_user.id in gban_users:
        await message.delete()
        return

    text = message.text or message.caption or ""
    if any(keyword.lower() in text.lower() for keyword in FORBIDDEN_KEYWORDS):
        await message.delete()
        await message.reply(f"⚠️ @{message.from_user.username} Copyright violation!")

# Handle edited messages
@app.on_edited_message(filters.group)
async def handle_edits(_, edited_message: Message):
    user = edited_message.from_user

    if user and user.id in authorized_users:
        return

    await edited_message.reply(
        f"⚠️ @{user.username} your edited message will be deleted after {edit_delete_delay} seconds.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Updates", url="https://t.me/Kirito_Bots")]
        ])
    )

    await asyncio.sleep(edit_delete_delay)
    try:
        await edited_message.delete()
    except Exception as e:
        logging.warning(f"Failed to delete edited message: {e}")

# Authorize user
@app.on_message(filters.command("auth") & filters.group)
async def authorize_user(_, message: Message):
    member = await app.get_chat_member(message.chat.id, message.from_user.id)
    if not (member.status in ("administrator", "creator")):
        return await message.reply("❌ You must be an admin to authorize users.")

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        authorized_users.add(user_id)
        await message.reply(f"✅ User {user_id} authorized.")
    else:
        await message.reply("ℹ️ Reply to a user's message to authorize them.")

# Unauthorize user
@app.on_message(filters.command("unauth") & filters.group)
async def unauthorize_user(_, message: Message):
    member = await app.get_chat_member(message.chat.id, message.from_user.id)
    if not (member.status in ("administrator", "creator")):
        return await message.reply("❌ You must be an admin to unauthorize users.")

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        authorized_users.discard(user_id)
        await message.reply(f"🚫 User {user_id} unauthorized.")
    else:
        await message.reply("ℹ️ Reply to a user's message to unauthorize them.")

# List authorized users
@app.on_message(filters.command("authusers") & filters.group)
async def list_auth_users(_, message: Message):
    if not authorized_users:
        await message.reply("⚠️ No users are currently authorized.")
    else:
        await message.reply("✅ Authorized Users:\n" + "\n".join(str(uid) for uid in authorized_users))

# Set delay
@app.on_message(filters.command("setdelay") & filters.group)
async def set_delay(_, message: Message):
    global edit_delete_delay
    if len(message.command) != 2 or not message.command[1].isdigit():
        return await message.reply("⏱️ Usage: /setdelay <seconds>")
    edit_delete_delay = int(message.command[1])
    await message.reply(f"✅ Delay set to {edit_delete_delay} seconds.")

# Track new groups
@app.on_chat_member_updated()
async def track_new_groups(_, chat_member):
    if chat_member.new_chat_member and chat_member.new_chat_member.user.id == (await app.get_me()).id:
        active_groups.add(chat_member.chat.id)

# Cleanup old message store
async def cleanup_store():
    current_time = time.time()
    to_delete = [msg_id for msg_id, data in message_store.items() if current_time - data["time"] > 86400]
    for msg_id in to_delete:
        del message_store[msg_id]

# Scheduler
scheduler = AsyncIOScheduler()
scheduler.add_job(cleanup_store, 'interval', hours=6)
scheduler.start()

print("⚡ Bot is running...")
app.run()
