#!/usr/bin/env python3
"""
FF H4CK ☠️ Telegram Bot
Single-file implementation with referral system, force join, and code generation
Optimized for Render.com deployment
"""

import logging
import json
import random
import asyncio
import hashlib
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import telegram
from keep_alive import keep_alive
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

# 🔑 Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "8292988709:AAG6zzTSraLJKQgwtN6SlCwCwrap738k7vQ")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6178010957"))
BOT_USERNAME = "FF_H4CK_BOT"
DEVELOPER_USERNAME = "@BACK_BENCHERS17"
WELCOME_IMAGE_ID = "AgACAgUAAxkBAAMCaLBNGaOOGQEBE7ZazhjQ5zuhp5YAAvXFMRsTz4lVipP-1pwKygMBAAMCAAN4AAM2BA"

# 🔑 Channel Configuration - Users must join these channels
FORCE_CHANNELS = [
    {"id": -1002628079220, "link": "https://t.me/+d6AcqSlHiag1MmZl", "name": "FF H4CK Channel 1"},
    {"id": -1002449787641, "link": "https://t.me/+Kv3f2aL-yyEzYjFl", "name": "FF H4CK Channel 2"}
]

# 📁 In-Memory Data Storage
USERS_DATA = {}  # {user_id: {user_info}}
REFERRALS_DATA = {}  # {user_id: [referred_user_ids]}
GENERATED_CODES = {}  # {code: {user_id, created_at, expires_at}}
BOT_STATS = {
    "total_users": 0,
    "total_codes": 0,
    "total_referrals": 0,
    "start_time": datetime.now()
}

# 🎨 Bot Messages and UI
WELCOME_MESSAGE = """
🔥 **FF H4CK BOT** 🔥
━━━━━━━━━━━━━━━━━━━━━

💀 **Free Fire Ultimate Hacks**
⚡ **Headshot, Aimbot, ESP & More!**
🛡️ **Anti-Ban Protection Enabled**
🎯 **100% Working on All Devices**

👤 **Player:** {}
🆔 **ID:** `{}`
📅 **Joined:** {}

🚀 **Get Started:**
• Join required channels
• Refer 5 friends
• Get your FF H4CK key!

━━━━━━━━━━━━━━━━━━━━━
💎 **Ready to destroy enemies?** 💎
"""

REFERRAL_MESSAGE = """
🔗 **REFER FRIENDS & EARN FF H4CK KEYS** 🔗
━━━━━━━━━━━━━━━━━━━━━━

📊 **Your Progress:**
👥 Referrals: **{}/5**
🎯 Status: **{}**

🔗 **Your Referral Link:**
`{}`

💡 **How it works:**
1️⃣ Share your link with FF players
2️⃣ They join through your link
3️⃣ Get 5 referrals = Unlock hack keys!
4️⃣ Generate unlimited FF H4CK keys

🎁 **Rewards:**
• 5 Referrals = Key Generator Access
• Premium FF H4CK Keys
• VIP Hacker Status

━━━━━━━━━━━━━━━━━━━━━━
"""

CODE_GENERATED_MESSAGE = """
🎉 **FF H4CK KEY UNLOCKED!** 🎉
━━━━━━━━━━━━━━━━━━━━━━

🔑 **Your Key:** `{}`
⏰ **Valid Until:** {}
🎯 **Type:** FF H4CK Premium
💎 **Features:** All Unlocked

⚡ **Included Hacks:**
• 🎯 Aimbot & Auto Headshot
• 👀 ESP (Enemy Location)
• 💰 Unlimited Diamonds  
• 🛡️ God Mode Protection
• 🚗 Speed Hack & Jump Hack
• 📦 All Skins & Items

🛡️ **Anti-Ban Protection:** ✅
📱 **All Devices Supported:** ✅

━━━━━━━━━━━━━━━━━━━━━━
💀 **Ready to destroy enemies!** 💀
"""

# ---------------- Logging Configuration ----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------------- Utility Functions ----------------
def get_current_time():
    """Get current timestamp."""
    return datetime.now()

def format_datetime(dt):
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def generate_referral_code(user_id: int) -> str:
    """Generate unique referral code for user."""
    return f"PM{user_id}{random.randint(1000, 9999)}"

def generate_mod_code() -> str:
    """Generate FF H4CK key."""
    prefix = "PRIME"
    # Generate 6-character alphanumeric suffix like 2683UE
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    suffix = ''.join(random.choices(chars, k=6))
    return f"{prefix}-{suffix}"

def is_user_admin(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id == ADMIN_ID

# ---------------- User Management Functions ----------------
def get_user_data(user_id: int) -> Dict:
    """Get or create user data."""
    user_id_str = str(user_id)
    
    if user_id_str not in USERS_DATA:
        USERS_DATA[user_id_str] = {
            "user_id": user_id,
            "username": None,
            "first_name": None,
            "joined_date": get_current_time(),
            "referral_code": generate_referral_code(user_id),
            "referred_by": None,
            "codes_generated": 0,
            "last_activity": get_current_time(),
            "is_premium": False,
            "channels_joined": [],
            "total_referrals": 0
        }
        
        # Initialize referrals list
        if user_id_str not in REFERRALS_DATA:
            REFERRALS_DATA[user_id_str] = []
        
        BOT_STATS["total_users"] += 1
    
    return USERS_DATA[user_id_str]

def update_user_activity(user_id: int):
    """Update user last activity."""
    user_data = get_user_data(user_id)
    user_data["last_activity"] = get_current_time()

def add_referral(referrer_id: int, referred_id: int) -> bool:
    """Add referral and return success status."""
    referrer_str = str(referrer_id)
    referred_str = str(referred_id)
    
    # Don't allow self-referral
    if referrer_id == referred_id:
        return False
    
    # Check if already referred
    if referred_str in REFERRALS_DATA.get(referrer_str, []):
        return False
    
    # Add referral
    if referrer_str not in REFERRALS_DATA:
        REFERRALS_DATA[referrer_str] = []
    
    REFERRALS_DATA[referrer_str].append(referred_str)
    
    # Update referrer's data
    referrer_data = get_user_data(referrer_id)
    referrer_data["total_referrals"] = len(REFERRALS_DATA[referrer_str])
    
    # Update referred user's data
    referred_data = get_user_data(referred_id)
    referred_data["referred_by"] = referrer_id
    
    BOT_STATS["total_referrals"] += 1
    return True

def get_referral_count(user_id: int) -> int:
    """Get user's referral count."""
    return len(REFERRALS_DATA.get(str(user_id), []))

def can_generate_code(user_id: int) -> bool:
    """Check if user can generate codes (5+ referrals)."""
    return get_referral_count(user_id) >= 5

# ---------------- Channel Management ----------------
async def check_channel_membership(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> List[Dict]:
    """Check which channels user hasn't joined."""
    not_joined = []
    
    for channel in FORCE_CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel["id"], user_id)
            if member.status in ['left', 'kicked']:
                not_joined.append(channel)
        except Exception as e:
            logger.warning(f"Error checking membership for channel {channel['id']}: {e}")
            not_joined.append(channel)
    
    return not_joined

def create_channel_keyboard(channels: List[Dict]) -> InlineKeyboardMarkup:
    """Create inline keyboard for channel joining."""
    buttons = []
    
    for channel in channels:
        buttons.append([InlineKeyboardButton(
            f"📢 Join {channel['name']}", 
            url=channel['link']
        )])
    
    buttons.append([InlineKeyboardButton("✅ I Joined All Channels", callback_data="check_channels")])
    
    return InlineKeyboardMarkup(buttons)

# ---------------- Code Generation ----------------
def generate_premium_code(user_id: int) -> Dict:
    """Generate premium code for user."""
    code = generate_mod_code()
    expires_at = get_current_time() + timedelta(days=30)
    
    code_data = {
        "code": code,
        "user_id": user_id,
        "created_at": get_current_time(),
        "expires_at": expires_at,
        "is_active": True
    }
    
    GENERATED_CODES[code] = code_data
    
    # Update user stats
    user_data = get_user_data(user_id)
    user_data["codes_generated"] += 1
    user_data["is_premium"] = True
    
    BOT_STATS["total_codes"] += 1
    
    return code_data

# ---------------- Bot Handlers ----------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    user_id = user.id
    
    # Update user info
    user_data = get_user_data(user_id)
    user_data["username"] = user.username
    user_data["first_name"] = user.first_name
    update_user_activity(user_id)
    
    # Check for referral
    if context.args:
        referral_code = context.args[0]
        # Extract referrer ID from code (format: PM{user_id}{random})
        try:
            if referral_code.startswith("PM"):
                referrer_id = int(referral_code[2:-4])  # Remove PM prefix and last 4 digits
                if add_referral(referrer_id, user_id):
                    # Notify referrer
                    try:
                        await context.bot.send_message(
                            referrer_id,
                            f"🎉 **NEW REFERRAL!** 🎉\n\n"
                            f"👤 {user.first_name} joined through your link!\n"
                            f"📊 Total Referrals: **{get_referral_count(referrer_id)}/5**\n\n"
                            f"{'🔓 **Code Generator Unlocked!**' if can_generate_code(referrer_id) else '🔒 Need more referrals to unlock codes'}"
                        )
                    except:
                        pass
        except:
            pass
    
    # Check channel membership
    not_joined_channels = await check_channel_membership(context, user_id)
    
    if not_joined_channels:
        # User needs to join channels
        message = (
            "🚨 **JOIN REQUIRED CHANNELS** 🚨\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📢 **You must join all channels to access PRIME MODS:**\n\n"
            "🔒 **Access Locked Until You Join**"
        )
        
        keyboard = create_channel_keyboard(not_joined_channels)
        await update.message.reply_text(message, reply_markup=keyboard, parse_mode='Markdown')
    else:
        # Welcome message
        welcome_text = WELCOME_MESSAGE.format(
            user.first_name,
            user_id,
            format_datetime(user_data["joined_date"])
        )
        
        # Main menu keyboard
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Refer Friends", callback_data="referrals")],
            [InlineKeyboardButton("🔑 Generate FF H4CK Key", callback_data="generate_code")],
            [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
        ])
        
        # Send welcome image first, then text
        try:
            await update.message.reply_photo(
                photo=WELCOME_IMAGE_ID,
                caption=welcome_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        except:
            # Fallback to text message if image fails
            await update.message.reply_text(welcome_text, reply_markup=keyboard, parse_mode='Markdown')

async def referrals_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle referrals display."""
    query = update.callback_query
    user_id = query.from_user.id
    
    referral_count = get_referral_count(user_id)
    user_data = get_user_data(user_id)
    referral_link = f"https://t.me/{BOT_USERNAME}?start={user_data['referral_code']}"
    
    status = "🔓 **UNLOCKED**" if referral_count >= 5 else "🔒 **LOCKED**"
    
    message = REFERRAL_MESSAGE.format(
        referral_count,
        status,
        referral_link
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Share Link", url=f"https://t.me/share/url?url={referral_link}&text=🔥%20JOIN%20FF%20H4CK%20BOT%20🔥%0A%0A💀%20Get%20FREE%20Fire%20Ultimate%20Hacks!%0A⚡%20Aimbot,%20ESP,%20God%20Mode%20&%20More!%0A🛡️%20Anti-Ban%20Protection%20Enabled%0A%0A🎯%20Click%20this%20link%20to%20join:%0A{referral_link}%0A%0A🔥%20Let's%20dominate%20together!")],
        [InlineKeyboardButton("🔄 Refresh", callback_data="referrals")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ])
    
    try:
        await query.edit_message_media(
            media=InputMediaPhoto(
                media=WELCOME_IMAGE_ID,
                caption=message,
                parse_mode='Markdown'
            ),
            reply_markup=keyboard
        )
    except:
        await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def generate_code_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle code generation."""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not can_generate_code(user_id):
        message = (
            "🔒 **CODE GENERATION LOCKED** 🔒\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 **Current Referrals:** {get_referral_count(user_id)}/5\n"
            f"❌ **Need {5 - get_referral_count(user_id)} more referrals**\n\n"
            "🔗 **Share your referral link to unlock!**"
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Get Referral Link", callback_data="referrals")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ])
    else:
        # Generate code
        code_data = generate_premium_code(user_id)
        
        message = CODE_GENERATED_MESSAGE.format(
            code_data["code"],
            format_datetime(code_data["expires_at"])
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔑 Generate Another", callback_data="generate_code")],
            [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ])
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user stats display."""
    query = update.callback_query
    user_id = query.from_user.id
    user_data = get_user_data(user_id)
    
    referral_count = get_referral_count(user_id)
    
    message = (
        f"📊 **YOUR STATISTICS** 📊\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 **User ID:** `{user_id}`\n"
        f"📅 **Joined:** {format_datetime(user_data['joined_date'])}\n"
        f"👥 **Referrals:** {referral_count}/5\n"
        f"🔑 **Codes Generated:** {user_data['codes_generated']}\n"
        f"💎 **Premium Status:** {'✅ Active' if user_data['is_premium'] else '❌ Inactive'}\n"
        f"⏰ **Last Activity:** {format_datetime(user_data['last_activity'])}\n\n"
        f"🎯 **Status:** {'🔓 Code Generator Unlocked' if can_generate_code(user_id) else '🔒 Need more referrals'}"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="stats")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ])
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle help display."""
    query = update.callback_query
    
    message = (
        "🔥 **FF H4CK HELP CENTER** 🔥\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 **How to unlock FF H4CK keys:**\n"
        "1️⃣ Join all required channels (mandatory)\n"
        "2️⃣ Share your referral link with 5 friends\n"
        "3️⃣ Once they join = Key generator unlocked!\n"
        "4️⃣ Generate unlimited premium FF H4CK keys\n\n"
        "⚡ **Available Hacks:**\n"
        "• 🎯 Aimbot & Auto Headshot\n"
        "• 👁️ ESP (See enemies through walls)\n"
        "• 💎 Unlimited Diamonds & Coins\n"
        "• 🛡️ God Mode (Invincibility)\n"
        "• 🚗 Speed Hack & Wall Hack\n"
        "• 📦 All Skins & Items Unlocked\n\n"
        "🔹 **Quick Commands:**\n"
        "• `/start` - Start the bot\n"
        "• `/stats` - View your progress\n\n"
        "🆘 **Need Support?**\n"
        f"• Contact: {DEVELOPER_USERNAME}\n"
        "• Join our main channel for updates\n\n"
        "⚠️ **Important Tips:**\n"
        "• Share link in FF gaming groups for fast referrals\n"
        "• Keys are valid for 30 days\n"
        "• Works on all devices (Android/iOS)\n"
        "• Use responsibly to avoid game detection\n"
        "• Anti-ban protection included in all keys"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ])
    
    try:
        await query.edit_message_media(
            media=InputMediaPhoto(
                media=WELCOME_IMAGE_ID,
                caption=message,
                parse_mode='Markdown'
            ),
            reply_markup=keyboard
        )
    except:
        await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu display."""
    query = update.callback_query
    user = query.from_user
    user_id = user.id
    user_data = get_user_data(user_id)
    
    welcome_text = WELCOME_MESSAGE.format(
        user.first_name,
        user_id,
        format_datetime(user_data["joined_date"])
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Refer Friends", callback_data="referrals")],
        [InlineKeyboardButton("🔑 Generate Code", callback_data="generate_code")],
        [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ])
    
    await query.edit_message_text(welcome_text, reply_markup=keyboard, parse_mode='Markdown')

async def check_channels_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle channel membership verification."""
    query = update.callback_query
    user_id = query.from_user.id
    
    not_joined_channels = await check_channel_membership(context, user_id)
    
    if not_joined_channels:
        message = (
            "❌ **STILL NEED TO JOIN** ❌\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🚨 **You haven't joined all channels yet!**\n\n"
            "📢 **Please join the channels below:**"
        )
        
        keyboard = create_channel_keyboard(not_joined_channels)
        await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')
    else:
        # All channels joined, show main menu
        await main_menu_handler(update, context)

# ---------------- Admin Commands ----------------
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin panel."""
    user_id = update.effective_user.id
    
    if not is_user_admin(user_id):
        await update.message.reply_text("❌ **Access Denied!** You are not authorized to use this command.")
        return
    
    uptime = datetime.now() - BOT_STATS["start_time"]
    
    message = (
        f"👑 **ADMIN PANEL** 👑\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 **Bot Statistics:**\n"
        f"• Users: {BOT_STATS['total_users']}\n"
        f"• Codes Generated: {BOT_STATS['total_codes']}\n"
        f"• Total Referrals: {BOT_STATS['total_referrals']}\n"
        f"• Uptime: {uptime.days}d {uptime.seconds//3600}h\n\n"
        f"🔧 **Admin Commands:**\n"
        f"• `/broadcast <message>` - Send to all users\n"
        f"• `/stats_admin` - Detailed statistics\n"
        f"• `/users` - List recent users"
    )
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast message to all users."""
    user_id = update.effective_user.id
    
    if not is_user_admin(user_id):
        await update.message.reply_text("❌ **Access Denied!**")
        return
    
    if not context.args:
        await update.message.reply_text("📢 **Usage:** `/broadcast <your message>`")
        return
    
    broadcast_text = " ".join(context.args)
    
    # Add broadcast header
    message = (
        f"📢 **ADMIN BROADCAST** 📢\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{broadcast_text}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 **PRIME MODS** ☠️"
    )
    
    sent_count = 0
    failed_count = 0
    
    status_message = await update.message.reply_text("📤 **Broadcasting message...**")
    
    for user_id_str in USERS_DATA:
        try:
            await context.bot.send_message(int(user_id_str), message, parse_mode='Markdown')
            sent_count += 1
        except Exception as e:
            failed_count += 1
            logger.warning(f"Failed to send broadcast to {user_id_str}: {e}")
        
        # Update status every 10 users
        if (sent_count + failed_count) % 10 == 0:
            await status_message.edit_text(f"📤 **Broadcasting...** {sent_count + failed_count}/{len(USERS_DATA)}")
    
    final_message = (
        f"✅ **Broadcast Complete!**\n\n"
        f"📤 **Sent:** {sent_count}\n"
        f"❌ **Failed:** {failed_count}\n"
        f"📊 **Total:** {sent_count + failed_count}"
    )
    
    await status_message.edit_text(final_message)

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle users list command."""
    user_id = update.effective_user.id
    
    if not is_user_admin(user_id):
        await update.message.reply_text("❌ **Access Denied!**")
        return
    
    # Get recent users (last 20)
    recent_users = sorted(
        USERS_DATA.items(), 
        key=lambda x: x[1]['joined_date'], 
        reverse=True
    )[:20]
    
    message = "👥 **RECENT USERS** (Last 20)\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for user_id_str, user_data in recent_users:
        name = user_data.get('first_name', 'Unknown')
        username = user_data.get('username', 'No username')
        referrals = get_referral_count(int(user_id_str))
        codes = user_data['codes_generated']
        
        message += f"👤 **{name}** (@{username})\n"
        message += f"🆔 `{user_id_str}` | 👥 {referrals} refs | 🔑 {codes} codes\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

# ---------------- Callback Query Router ----------------
async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries."""
    query = update.callback_query
    await query.answer()
    
    update_user_activity(query.from_user.id)
    
    if query.data == "referrals":
        await referrals_handler(update, context)
    elif query.data == "generate_code":
        await generate_code_handler(update, context)
    elif query.data == "stats":
        await stats_handler(update, context)
    elif query.data == "help":
        await help_handler(update, context)
    elif query.data == "main_menu":
        await main_menu_handler(update, context)
    elif query.data == "check_channels":
        await check_channels_handler(update, context)

# ---------------- Text Command Handlers ----------------
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command."""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    update_user_activity(user_id)
    
    referral_count = get_referral_count(user_id)
    
    message = (
        f"📊 **YOUR STATISTICS** 📊\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 **User ID:** `{user_id}`\n"
        f"📅 **Joined:** {format_datetime(user_data['joined_date'])}\n"
        f"👥 **Referrals:** {referral_count}/5\n"
        f"🔑 **Codes Generated:** {user_data['codes_generated']}\n"
        f"💎 **Premium Status:** {'✅ Active' if user_data['is_premium'] else '❌ Inactive'}\n"
        f"⏰ **Last Activity:** {format_datetime(user_data['last_activity'])}\n\n"
        f"🎯 **Status:** {'🔓 Code Generator Unlocked' if can_generate_code(user_id) else '🔒 Need more referrals'}"
    )
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /referrals command."""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    update_user_activity(user_id)
    
    referral_count = get_referral_count(user_id)
    referral_link = f"https://t.me/{BOT_USERNAME}?start={user_data['referral_code']}"
    
    status = "🔓 **UNLOCKED**" if referral_count >= 5 else "🔒 **LOCKED**"
    
    message = REFERRAL_MESSAGE.format(
        referral_count,
        status,
        referral_link
    )
    
    await update.message.reply_text(message, parse_mode='Markdown')

# ---------------- Error Handler ----------------
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by Updates."""
    logger.error(f"Update {update} caused error {context.error}")

# ---------------- Main Function ----------------
def main():
    """Start the bot."""
    # Start keep_alive server for Render
    keep_alive()
    
    # Validate bot token
    if BOT_TOKEN == "8292988709:AAG6zzTSraLJKQgwtN6SlCwCwrap738k7vQ":
        logger.info("✅ Using provided bot token")
    else:
        logger.error("❌ Please check your BOT_TOKEN!")
        return
    
    try:
        # Create application with updated method for compatibility
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(CommandHandler("referrals", referral_command))
        application.add_handler(CommandHandler("admin", admin_command))
        application.add_handler(CommandHandler("broadcast", broadcast_command))
        application.add_handler(CommandHandler("users", users_command))
        
        application.add_handler(CallbackQueryHandler(callback_query_handler))
        
        # Error handler
        application.add_error_handler(error_handler)
        
        # Start bot
        logger.info("🚀 FF H4CK Bot starting...")
        logger.info(f"👑 Admin ID: {ADMIN_ID}")
        logger.info(f"📢 Channels to join: {len(FORCE_CHANNELS)}")
        logger.info("🌐 Keep-alive server started for Render")
        
        # Run the bot with proper error handling for Render
        application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"❌ Bot failed to start: {e}")
        # Keep the process alive even if bot fails
        import time
        while True:
            time.sleep(3600)  # Sleep for 1 hour

if __name__ == "__main__":
    main()
