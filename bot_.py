import logging
import json
import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

# 🔑 Bot Token
BOT_TOKEN = "8292988709:AAG6zzTSraLJKQgwtN6SlCwCwrap738k7vQ"

# 🔑 Bot Username (without @)
BOT_USERNAME = "FREE_KEY_xBOT"

# 🔑 Admin ID
ADMIN_ID = 6178010957

# 🔑 Welcome Image File_ID
WELCOME_IMAGE_ID = "AgACAgUAAxkBAAMCaLBNGaOOGQEBE7ZazhjQ5zuhp5YAAvXFMRsTz4lVipP-1pwKygMBAAMCAAN4AAM2BA"

# 🔑 Private Channel IDs + Invite Links
FORCE_CHANNELS = [
    {"id": -1002628079220, "link": "https://t.me/+d6AcqSlHiag1MmZl"},  # Channel 1
    {"id": -1002449787641, "link": "https://t.me/+Kv3f2aL-yyEzYjFl"}   # Channel 2
]

# Files to save users and referrals
USERS_FILE = "users.json"
REF_FILE = "referrals.json"

# ---------------- Logging ----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------------- Helper Functions ----------------
def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(list(users), f)

def load_referrals():
    try:
        with open(REF_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_referrals(refs):
    with open(REF_FILE, "w") as f:
        json.dump(refs, f)

def generate_key():
    return "PRIME-" + str(random.randint(10000, 99999))

async def is_member(bot, user_id):
    """Check if user is in ALL required channels."""
    for ch in FORCE_CHANNELS:
        try:
            member = await bot.get_chat_member(ch["id"], user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

def get_join_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel 1", url=FORCE_CHANNELS[0]["link"])],
        [InlineKeyboardButton("📢 Join Channel 2", url=FORCE_CHANNELS[1]["link"])],
        [InlineKeyboardButton("✅ I've Joined", callback_data="check_join")]
    ])

def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤝 Refer To Generate Key", callback_data="refer")],
        [InlineKeyboardButton("🔑 Generate Key", callback_data="generate_key")]
    ])

def get_invite_keyboard(user_id):
    link = f"https://t.me/{BOT_USERNAME}?start=ref{user_id}"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📨 Invite Your Friends", url=link)]
    ])

def get_copy_keyboard(key):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📋 Copy Key: {key}", callback_data=f"copy_{key}")]
    ])

# ---------------- Handlers ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args  

    # Load referrals
    refs = load_referrals()
    if str(user.id) not in refs:
        refs[str(user.id)] = {"count": 0, "key": None}
        save_referrals(refs)

    # Handle referral
    if args and args[0].startswith("ref"):
        ref_id = args[0].replace("ref", "")
        if ref_id != str(user.id):
            if ref_id in refs:
                refs[ref_id]["count"] += 1
                if refs[ref_id]["count"] >= 5 and refs[ref_id]["key"] is None:
                    refs[ref_id]["key"] = generate_key()
                save_referrals(refs)

    # Force channel join check
    if not await is_member(context.bot, user.id):
        await update.message.reply_text(
            "🚨 To use this bot, you must join both channels below:",
            reply_markup=get_join_keyboard()
        )
        return

    # Save user
    users = load_users()
    users.add(user.id)
    save_users(users)

    caption = (
        "💀 <b>PRIME MODS ☠️</b>\n"
        "━━━━━━━━━━━━━━━\n\n"
        "🎮 <i>Free Fire Dark Hack Bot</i>\n"
        "🚀 Unlock premium mods, tricks & tools\n"
        "🛡️ Stay ahead of enemies with deadly powers!\n\n"
        "✨ <b>Choose an option below:</b>\n"
        "━━━━━━━━━━━━━━━\n"
    )

    await update.message.reply_photo(
        photo=WELCOME_IMAGE_ID,
        caption=caption,
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    refs = load_referrals()
    if str(user.id) not in refs:
        refs[str(user.id)] = {"count": 0, "key": None}
        save_referrals(refs)

    data = query.data

    if data == "refer":
        link = f"https://t.me/{BOT_USERNAME}?start=ref{user.id}"
        text = (
            "🎯 <b>Refer & Earn</b>\n"
            "━━━━━━━━━━━━━━━\n\n"
            "🔥 Unlock your <b>SECRET KEY</b> by inviting <b>5 friends</b>!\n\n"
            "📨 Your Unique Link:\n"
            f"<code>{link}</code>\n\n"
            "⚡ Share this link and watch your progress grow!\n"
            "━━━━━━━━━━━━━━━"
        )

        # Edit main message (so it doesn’t look empty)
        await query.edit_message_caption(
            caption="✅ Referral link sent in your DM!\n\nCheck your private chat with me 👇",
            parse_mode="HTML"
        )

        # Send DM with link + button
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📨 Invite Your Friends", url=link)]
                ])
            )
        except:
            await query.edit_message_caption(
                caption="⚠️ Please start me in DM first and click again!",
                parse_mode="HTML"
            )

    elif data == "generate_key":
        user_data = refs[str(user.id)]
        if user_data["count"] < 5:
            await query.edit_message_caption(
                caption=(
                    f"⚠️ You need <b>5 referrals</b> to unlock your key.\n\n"
                    f"📌 Current Progress: {user_data['count']} / 5"
                ),
                parse_mode="HTML",
                reply_markup=get_invite_keyboard(user.id)
            )
        else:
            if user_data["key"]:
                await query.edit_message_caption(
                    caption=f"🎉 Congratulations!\n\nYour Key: <code>{user_data['key']}</code>",
                    parse_mode="HTML",
                    reply_markup=get_copy_keyboard(user_data["key"])
                )
            else:
                refs[str(user.id)]["key"] = generate_key()
                save_referrals(refs)
                await query.edit_message_caption(
                    caption=f"🎉 Congratulations!\n\nYour Key: <code>{refs[str(user.id)]['key']}</code>",
                    parse_mode="HTML",
                    reply_markup=get_copy_keyboard(refs[str(user.id)]["key"])
                )

    elif data.startswith("copy_"):
        key = data.replace("copy_", "")
        await query.message.reply_text(
            f"✅ Your Key: <code>{key}</code>\n\nCopied successfully!",
            parse_mode="HTML"
        )

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    if not await is_member(context.bot, user.id):
        await query.edit_message_text(
            "❌ You haven't joined both channels yet.\n\nJoin now and click again:",
            reply_markup=get_join_keyboard()
        )
        return

    users = load_users()
    users.add(user.id)
    save_users(users)

    await query.edit_message_text(
        "✅ <b>Welcome Back!</b>\n\n🔥 You can now use the bot!",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file_id = photo.file_id
    await update.message.reply_photo(
        photo=WELCOME_IMAGE_ID,
        caption=f"📂 File ID:\n<code>{file_id}</code>",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    message = " ".join(context.args)
    if not message:
        await update.message.reply_text(
            "⚠️ Please provide a message to broadcast.\nUsage: `/broadcast Hello Users!`",
            parse_mode="Markdown"
        )
        return

    users = load_users()
    count = 0
    for user_id in users:
        try:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=WELCOME_IMAGE_ID,
                caption=f"📢 Broadcast:\n\n{message}",
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )
            count += 1
        except Exception as e:
            logger.error(f"Failed to send to {user_id}: {e}")

    await update.message.reply_text(f"✅ Broadcast sent to {count} users.")

# ---------------- Main ----------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot is running with referral + key system...")
    app.run_polling()

if __name__ == "__main__":
    main()