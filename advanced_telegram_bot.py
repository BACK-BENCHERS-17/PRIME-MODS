import logging
import json
import random
import asyncio
import hashlib
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

# 🔑 Bot Configuration
BOT_TOKEN = "8292988709:AAG6zzTSraLJKQgwtN6SlCwCwrap738k7vQ"
BOT_USERNAME = "FREE_KEY_xBOT"
ADMIN_ID = 6178010957
DEVELOPER_USERNAME = "@BACK_BENCHERS17"
WELCOME_IMAGE_ID = "AgACAgUAAxkBAAMCaLBNGaOOGQEBE7ZazhjQ5zuhp5YAAvXFMRsTz4lVipP-1pwKygMBAAMCAAN4AAM2BA"

# 🔑 Channel Configuration
FORCE_CHANNELS = [
    {"id": -1002628079220, "link": "https://t.me/+d6AcqSlHiag1MmZl", "name": "Channel 1"},
    {"id": -1002449787641, "link": "https://t.me/+Kv3f2aL-yyEzYjFl", "name": "Channel 2"}
]

# 📁 Data Files (in-memory storage for single file)
USERS_DATA = {}
REFERRALS_DATA = {}
PROFILES_DATA = {}
ACHIEVEMENTS_DATA = {}
LEADERBOARD_DATA = {}
GAMES_DATA = {}
BOT_STATS = {
    "total_users": 0,
    "total_keys": 0,
    "total_games": 0,
    "daily_users": 0,
    "last_reset": datetime.now().date().isoformat()
}

# 🎮 Game Configuration
GAMES_CONFIG = {
    "guess_number": {"name": "🎯 Number Guessing", "reward": 25, "description": "Guess the secret number!"},
    "trivia": {"name": "🧠 Trivia Challenge", "reward": 35, "description": "Test your knowledge!"},
    "riddle": {"name": "🤔 Riddle Master", "reward": 45, "description": "Solve brain teasers!"},
    "memory": {"name": "🧩 Memory Game", "reward": 55, "description": "Challenge your memory!"},
    "math": {"name": "🔢 Math Quiz", "reward": 30, "description": "Solve math problems!"},
    "word": {"name": "📝 Word Puzzle", "reward": 40, "description": "Find hidden words!"}
}

# 🏆 Achievement System
ACHIEVEMENTS = {
    "first_key": {"name": "First Key", "emoji": "🔑", "description": "Generated your first key", "reward": 100},
    "social_butterfly": {"name": "Social Butterfly", "emoji": "👥", "description": "Referred 5 users", "reward": 200},
    "master_recruiter": {"name": "Master Recruiter", "emoji": "🌟", "description": "Referred 25 users", "reward": 500},
    "game_novice": {"name": "Game Novice", "emoji": "🎮", "description": "Won 10 games", "reward": 150},
    "game_master": {"name": "Game Master", "emoji": "🏆", "description": "Won 100 games", "reward": 1000},
    "daily_warrior": {"name": "Daily Warrior", "emoji": "📅", "description": "30-day streak", "reward": 300},
    "quiz_champion": {"name": "Quiz Champion", "emoji": "🧠", "description": "Perfect score on trivia", "reward": 250},
    "speed_demon": {"name": "Speed Demon", "emoji": "⚡", "description": "Won game in under 10 seconds", "reward": 200},
    "fortune_seeker": {"name": "Fortune Seeker", "emoji": "💰", "description": "Earned 1000 coins", "reward": 100},
    "social_legend": {"name": "Social Legend", "emoji": "👑", "description": "Referred 100 users", "reward": 2000}
}

# 🌍 Multi-language Support
LANGUAGES = {
    "en": {
        "welcome": "🔥 <b>FF H4CK BOT</b> 🔥\n━━━━━━━━━━━━━━━━━━━━━\n\n💀 <i>Free Fire Ultimate Hacks</i>\n⚡ Headshot, Aimbot, ESP & More!\n🛡️ Anti-Ban Protection Enabled\n\n🎯 <b>Level:</b> {} | 💎 <b>Coins:</b> {}\n🔥 <b>Daily Streak:</b> {} days\n\n🚀 <b>Ready to dominate?</b>\n━━━━━━━━━━━━━━━━━━━━━",
        "join_channels": "🚨 Join all channels to unlock FF H4CK features:",
        "referral_needed": "⚠️ Need <b>{} friends</b> to unlock your hack key!\n\n📊 Progress: {}/{} friends invited",
        "key_generated": "🎉 FF H4CK KEY UNLOCKED!\n\n🔑 Your Key: <code>{}</code>\n⏰ Valid until: {}\n🔄 Uses: {}\n\n💀 Ready to destroy enemies!"
    }
}

# ---------------- Logging Configuration ----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------------- Utility Functions ----------------
def get_current_time():
    """Get current timestamp."""
    return datetime.now().isoformat()

def generate_user_id():
    """Generate unique user ID."""
    return str(random.randint(100000000, 999999999))

def hash_string(text: str) -> str:
    """Hash a string using SHA256."""
    return hashlib.sha256(text.encode()).hexdigest()[:8]

def format_number(num: int) -> str:
    """Format large numbers with K, M notation."""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

# ---------------- Data Management Functions ----------------
def get_user_profile(user_id: int) -> Dict:
    """Get or create user profile with default values."""
    user_id_str = str(user_id)
    
    if user_id_str not in PROFILES_DATA:
        PROFILES_DATA[user_id_str] = {
            "level": 1,
            "xp": 0,
            "coins": 0,
            "keys_generated": 0,
            "games_won": 0,
            "games_lost": 0,
            "referrals": 0,
            "streak": 0,
            "last_daily": None,
            "language": "en",
            "achievements": [],
            "created_at": get_current_time(),
            "total_playtime": 0,
            "favorite_game": None,
            "premium_until": None,
            "vip_level": 0,
            "notification_settings": {
                "daily_tips": True,
                "game_alerts": True,
                "achievement_alerts": True
            },
            "game_stats": {game: {"wins": 0, "losses": 0, "best_score": 0} for game in GAMES_CONFIG},
            "inventory": {"power_ups": 0, "hints": 3, "time_freeze": 0},
            "daily_challenges": {"completed": 0, "last_reset": get_current_time()},
            "social_stats": {"messages_sent": 0, "commands_used": 0}
        }
    
    return PROFILES_DATA[user_id_str]

def update_user_profile(user_id: int, updates: Dict) -> None:
    """Update user profile with new data."""
    user_id_str = str(user_id)
    if user_id_str in PROFILES_DATA:
        PROFILES_DATA[user_id_str].update(updates)

def add_coins(user_id: int, amount: int) -> int:
    """Add coins to user account."""
    profile = get_user_profile(user_id)
    profile["coins"] += amount
    update_user_profile(user_id, {"coins": profile["coins"]})
    return profile["coins"]

def add_xp(user_id: int, amount: int) -> Dict:
    """Add XP to user and handle level ups."""
    profile = get_user_profile(user_id)
    profile["xp"] += amount
    
    # Calculate level based on XP (exponential scaling)
    new_level = int((profile["xp"] / 100) ** 0.5) + 1
    level_up = new_level > profile["level"]
    old_level = profile["level"]
    profile["level"] = new_level
    
    # Level up rewards
    if level_up:
        coin_reward = new_level * 50
        profile["coins"] += coin_reward
    
    update_user_profile(user_id, profile)
    
    return {
        "level_up": level_up, 
        "old_level": old_level,
        "new_level": new_level, 
        "total_xp": profile["xp"],
        "coin_reward": coin_reward if level_up else 0
    }

def check_achievements(user_id: int) -> List[str]:
    """Check and award new achievements."""
    profile = get_user_profile(user_id)
    new_achievements = []
    
    for achievement_id, achievement in ACHIEVEMENTS.items():
        if achievement_id not in profile["achievements"]:
            earned = False
            
            if achievement_id == "first_key" and profile["keys_generated"] >= 1:
                earned = True
            elif achievement_id == "social_butterfly" and profile["referrals"] >= 5:
                earned = True
            elif achievement_id == "master_recruiter" and profile["referrals"] >= 25:
                earned = True
            elif achievement_id == "game_novice" and profile["games_won"] >= 10:
                earned = True
            elif achievement_id == "game_master" and profile["games_won"] >= 100:
                earned = True
            elif achievement_id == "daily_warrior" and profile["streak"] >= 30:
                earned = True
            elif achievement_id == "fortune_seeker" and profile["coins"] >= 1000:
                earned = True
            elif achievement_id == "social_legend" and profile["referrals"] >= 100:
                earned = True
            
            if earned:
                profile["achievements"].append(achievement_id)
                profile["coins"] += achievement["reward"]
                new_achievements.append(achievement_id)
    
    if new_achievements:
        update_user_profile(user_id, profile)
    
    return new_achievements

# ---------------- Key Generation System ----------------
def generate_key(key_type: str = "standard", user_level: int = 1) -> Dict:
    """Generate different types of keys based on user level."""
    key_types = {
        "standard": {"prefix": "PRIME", "duration": 30, "uses": 1, "min_level": 1},
        "premium": {"prefix": "ULTRA", "duration": 90, "uses": 3, "min_level": 5},
        "vip": {"prefix": "ROYAL", "duration": 180, "uses": 5, "min_level": 10},
        "elite": {"prefix": "DIVINE", "duration": 365, "uses": 10, "min_level": 20},
        "legendary": {"prefix": "ETERNAL", "duration": 999, "uses": -1, "min_level": 50}
    }
    
    # Auto-upgrade based on level
    available_types = [k for k, v in key_types.items() if user_level >= v["min_level"]]
    if key_type not in available_types:
        key_type = available_types[-1] if available_types else "standard"
    
    config = key_types[key_type]
    key_id = hash_string(f"{time.time()}{random.randint(1000, 9999)}")
    
    return {
        "key": f"{config['prefix']}-{key_id.upper()}",
        "type": key_type.title(),
        "created": get_current_time(),
        "expires": (datetime.now() + timedelta(days=config["duration"])).strftime("%Y-%m-%d"),
        "uses_remaining": config["uses"],
        "active": True,
        "features": get_key_features(key_type)
    }

def get_key_features(key_type: str) -> List[str]:
    """Get features available for each key type."""
    features = {
        "standard": ["Basic Mods", "Daily Updates"],
        "premium": ["Advanced Mods", "Priority Support", "Custom Themes"],
        "vip": ["All Mods", "24/7 Support", "Beta Features", "No Ads"],
        "elite": ["Exclusive Mods", "Personal Assistant", "Custom Development"],
        "legendary": ["Everything Unlocked", "VIP Discord", "Personal Developer"]
    }
    return features.get(key_type, features["standard"])

# ---------------- Game System ----------------
class GameEngine:
    """Advanced game engine with multiple game types."""
    
    @staticmethod
    def start_number_guessing(difficulty: str = "normal") -> Dict:
        """Start number guessing game with difficulty levels."""
        difficulties = {
            "easy": {"range": (1, 50), "attempts": 8, "multiplier": 1.0},
            "normal": {"range": (1, 100), "attempts": 7, "multiplier": 1.5},
            "hard": {"range": (1, 200), "attempts": 6, "multiplier": 2.0},
            "expert": {"range": (1, 500), "attempts": 5, "multiplier": 3.0}
        }
        
        config = difficulties.get(difficulty, difficulties["normal"])
        return {
            "type": "guess_number",
            "difficulty": difficulty,
            "target": random.randint(*config["range"]),
            "range": config["range"],
            "attempts": 0,
            "max_attempts": config["attempts"],
            "multiplier": config["multiplier"],
            "hints": [],
            "start_time": time.time()
        }
    
    @staticmethod
    def process_guess(session: Dict, guess: int) -> Dict:
        """Process guess with enhanced feedback."""
        session["attempts"] += 1
        target = session["target"]
        
        if guess == target:
            time_taken = time.time() - session["start_time"]
            speed_bonus = max(0, 100 - int(time_taken))
            base_reward = int(GAMES_CONFIG["guess_number"]["reward"] * session["multiplier"])
            total_reward = base_reward + speed_bonus
            
            return {
                "status": "win", 
                "message": f"🎉 Perfect! The number was {target}!\n⏱️ Time: {time_taken:.1f}s\n⚡ Speed bonus: +{speed_bonus}",
                "reward": total_reward,
                "speed_bonus": speed_bonus
            }
        elif session["attempts"] >= session["max_attempts"]:
            return {"status": "lose", "message": f"💔 Game over! The number was {target}"}
        else:
            diff = abs(guess - target)
            if diff <= 5:
                proximity = "🔥 Very close!"
            elif diff <= 15:
                proximity = "🌡️ Getting warm!"
            elif diff <= 30:
                proximity = "❄️ Getting cold!"
            else:
                proximity = "🧊 Very far!"
            
            direction = "📈 Too low!" if guess < target else "📉 Too high!"
            remaining = session["max_attempts"] - session["attempts"]
            
            return {
                "status": "continue",
                "message": f"{direction} {proximity}\n🎯 Attempts remaining: {remaining}"
            }
    
    @staticmethod
    def get_trivia_question(category: str = "general") -> Dict:
        """Get trivia questions by category."""
        questions = {
            "general": [
                {
                    "question": "🌍 What is the largest planet in our solar system?",
                    "options": ["Earth", "Jupiter", "Saturn", "Neptune"],
                    "correct": 1,
                    "explanation": "Jupiter is the largest planet, with a mass greater than all other planets combined!"
                },
                {
                    "question": "🏛️ Which ancient wonder was located in Alexandria?",
                    "options": ["Hanging Gardens", "Lighthouse", "Colossus", "Mausoleum"],
                    "correct": 1,
                    "explanation": "The Lighthouse of Alexandria was one of the Seven Wonders of the Ancient World!"
                }
            ],
            "science": [
                {
                    "question": "🧬 What does DNA stand for?",
                    "options": ["Deoxyribonucleic Acid", "Dynamic Nuclear Acid", "Digital Network Access", "Direct Neural Activity"],
                    "correct": 0,
                    "explanation": "DNA (Deoxyribonucleic Acid) carries genetic information in living organisms!"
                }
            ],
            "gaming": [
                {
                    "question": "🎮 Which game popularized the battle royale genre?",
                    "options": ["PUBG", "Fortnite", "Apex Legends", "Call of Duty"],
                    "correct": 0,
                    "explanation": "PUBG (PlayerUnknown's Battlegrounds) was the first major battle royale game!"
                }
            ]
        }
        
        category_questions = questions.get(category, questions["general"])
        question = random.choice(category_questions)
        question["category"] = category
        return question
    
    @staticmethod
    def get_math_problem(difficulty: str = "normal") -> Dict:
        """Generate math problems based on difficulty."""
        if difficulty == "easy":
            a, b = random.randint(1, 20), random.randint(1, 20)
            operations = ["+", "-"]
        elif difficulty == "normal":
            a, b = random.randint(10, 100), random.randint(1, 50)
            operations = ["+", "-", "*"]
        else:  # hard
            a, b = random.randint(10, 200), random.randint(2, 20)
            operations = ["+", "-", "*", "//"]
        
        op = random.choice(operations)
        if op == "+":
            answer = a + b
            question = f"🔢 What is {a} + {b}?"
        elif op == "-":
            answer = a - b
            question = f"🔢 What is {a} - {b}?"
        elif op == "*":
            answer = a * b
            question = f"🔢 What is {a} × {b}?"
        else:  # division
            answer = a // b
            question = f"🔢 What is {a} ÷ {b}? (integer division)"
        
        # Generate multiple choice options
        options = [answer]
        while len(options) < 4:
            wrong = answer + random.randint(-10, 10)
            if wrong not in options and wrong >= 0:
                options.append(wrong)
        
        random.shuffle(options)
        correct = options.index(answer)
        
        return {
            "question": question,
            "options": [str(opt) for opt in options],
            "correct": correct,
            "answer": answer,
            "difficulty": difficulty
        }
    
    @staticmethod
    def get_riddle() -> Dict:
        """Get a random riddle."""
        riddles = [
            {
                "question": "🤔 I have keys but no locks. I have space but no room. You can enter but can't go outside. What am I?",
                "answer": "keyboard",
                "hint": "You use it to type!",
                "explanation": "A keyboard has keys, space bar, enter key, but no physical locks or rooms!"
            },
            {
                "question": "🤔 What gets wet while drying?",
                "answer": "towel",
                "hint": "You use it after a shower!",
                "explanation": "A towel gets wet when it dries you off!"
            },
            {
                "question": "🤔 I'm tall when I'm young, and I'm short when I'm old. What am I?",
                "answer": "candle",
                "hint": "It gives light and melts!",
                "explanation": "A candle starts tall and gets shorter as it burns!"
            },
            {
                "question": "🤔 What has hands but can't hold anything?",
                "answer": "clock",
                "hint": "It tells time!",
                "explanation": "A clock has hands (hour and minute hands) but can't physically hold objects!"
            }
        ]
        return random.choice(riddles)

def get_active_game(user_id: int) -> Optional[Dict]:
    """Get user's active game session."""
    return GAMES_DATA.get(str(user_id))

def set_active_game(user_id: int, game_data: Dict) -> None:
    """Set user's active game session."""
    GAMES_DATA[str(user_id)] = game_data

def clear_active_game(user_id: int) -> None:
    """Clear user's active game session."""
    GAMES_DATA.pop(str(user_id), None)


# ---------------- Bot State Management ----------------
async def is_member(bot, user_id: int) -> bool:
    """Check if user is member of all required channels."""
    for channel in FORCE_CHANNELS:
        try:
            member = await bot.get_chat_member(channel["id"], user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception as e:
            logger.error(f"Error checking membership for {user_id}: {e}")
            return False
    return True

def get_user_language(user_id: int) -> str:
    """Get user's preferred language."""
    profile = get_user_profile(user_id)
    return profile.get("language", "en")

def get_text(user_id: int, key: str, *args) -> str:
    """Get localized text for user."""
    lang = get_user_language(user_id)
    text = LANGUAGES.get(lang, LANGUAGES["en"]).get(key, key)
    if args:
        return text.format(*args)
    return text

def calculate_referral_requirement(level: int) -> int:
    """Calculate referrals needed based on user level."""
    base_requirement = 3  # Start with 3 referrals
    return max(1, base_requirement + (level - 1))

# ---------------- Keyboard Generators ----------------
def get_join_keyboard() -> InlineKeyboardMarkup:
    """Generate join channels keyboard with enhanced design."""
    buttons = []
    for i, channel in enumerate(FORCE_CHANNELS):
        buttons.append([InlineKeyboardButton(f"📢 Join {channel['name']}", url=channel["link"])])
    
    buttons.append([InlineKeyboardButton("✅ I've Joined All Channels", callback_data="check_join")])
    buttons.append([InlineKeyboardButton("🔄 Refresh Status", callback_data="refresh_status")])
    
    return InlineKeyboardMarkup(buttons)

def get_main_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Generate enhanced main menu keyboard."""
    profile = get_user_profile(user_id)
    level = profile["level"]
    
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"🔑 Generate Key (Lv.{level})", callback_data="generate_key"),
            InlineKeyboardButton(f"👥 Referrals ({profile['referrals']})", callback_data="referrals")
        ],
        [
            InlineKeyboardButton("🎮 Gaming Zone", callback_data="games_menu"),
            InlineKeyboardButton(f"👤 Profile (Lv.{level})", callback_data="profile")
        ],
        [
            InlineKeyboardButton("🏆 Leaderboards", callback_data="leaderboard"),
            InlineKeyboardButton(f"💰 Shop ({profile['coins']} coins)", callback_data="shop")
        ],
        [
            InlineKeyboardButton("🎯 Daily Challenges", callback_data="daily_challenges"),
            InlineKeyboardButton("🏅 Achievements", callback_data="achievements")
        ],
        [
            InlineKeyboardButton(f"👨‍💻 Developer: {DEVELOPER_USERNAME}", url=f"https://t.me/{DEVELOPER_USERNAME.replace('@', '')}"),
            InlineKeyboardButton("⚙️ Settings", callback_data="settings")
        ],
        [InlineKeyboardButton("ℹ️ Help & Tutorial", callback_data="help")]
    ])

def get_games_keyboard() -> InlineKeyboardMarkup:
    """Generate enhanced games menu."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎯 Number Guessing", callback_data="game_guess_number"),
            InlineKeyboardButton("🧠 Trivia Quiz", callback_data="game_trivia")
        ],
        [
            InlineKeyboardButton("🔢 Math Challenge", callback_data="game_math"),
            InlineKeyboardButton("🤔 Riddle Master", callback_data="game_riddle")
        ],
        [
            InlineKeyboardButton("🧩 Memory Game", callback_data="game_memory"),
            InlineKeyboardButton("📝 Word Puzzle", callback_data="game_word")
        ],
        [
            InlineKeyboardButton("🎲 Random Game", callback_data="game_random"),
            InlineKeyboardButton("🏆 Tournament Mode", callback_data="game_tournament")
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
    ])


def get_shop_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Generate shop menu."""
    profile = get_user_profile(user_id)
    coins = profile["coins"]
    
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"💡 Hints x3 (50 coins)", callback_data="buy_hints"),
            InlineKeyboardButton(f"⚡ Power-Up (100 coins)", callback_data="buy_powerup")
        ],
        [
            InlineKeyboardButton(f"❄️ Time Freeze (150 coins)", callback_data="buy_timefreeze"),
            InlineKeyboardButton(f"🎯 Double Rewards (200 coins)", callback_data="buy_double")
        ],
        [
            InlineKeyboardButton(f"👑 VIP Pass (500 coins)", callback_data="buy_vip"),
            InlineKeyboardButton(f"🎨 Custom Theme (300 coins)", callback_data="buy_theme")
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
    ])

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Generate admin panel keyboard."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Bot Statistics", callback_data="admin_stats"),
            InlineKeyboardButton("👥 User Management", callback_data="admin_users")
        ],
        [
            InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast"),
            InlineKeyboardButton("🎮 Game Statistics", callback_data="admin_games")
        ],
        [
            InlineKeyboardButton("🏆 Manage Leaderboard", callback_data="admin_leaderboard"),
            InlineKeyboardButton("🎁 Send Rewards", callback_data="admin_rewards")
        ],
        [
            InlineKeyboardButton("🔧 Bot Settings", callback_data="admin_settings"),
            InlineKeyboardButton("📝 View Logs", callback_data="admin_logs")
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
    ])

# ---------------- Command Handlers ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced start command with comprehensive features."""
    user = update.effective_user
    args = context.args

    # Update bot stats
    BOT_STATS["total_users"] = len(PROFILES_DATA)
    today = datetime.now().date().isoformat()
    if BOT_STATS["last_reset"] != today:
        BOT_STATS["daily_users"] = 0
        BOT_STATS["last_reset"] = today
    BOT_STATS["daily_users"] += 1

    # Initialize user profile
    profile = get_user_profile(user.id)
    
    # Handle referral links
    if args and args[0].startswith("ref"):
        try:
            ref_id = int(args[0].replace("ref", ""))
            if ref_id != user.id and str(ref_id) in PROFILES_DATA:
                # Update referrer's stats
                ref_profile = get_user_profile(ref_id)
                ref_profile["referrals"] += 1
                update_user_profile(ref_id, ref_profile)
                
                # Rewards for both users
                xp_result = add_xp(ref_id, 50)
                add_coins(ref_id, 100)
                add_coins(user.id, 50)  # Welcome bonus for new user
                
                # Check achievements
                new_achievements = check_achievements(ref_id)
                
                # Send notification to referrer
                try:
                    notification = f"🎉 New referral bonus!\n👤 {user.first_name} joined\n💰 +100 coins, +50 XP"
                    if new_achievements:
                        notification += f"\n🏆 New achievements unlocked!"
                    
                    await context.bot.send_message(chat_id=ref_id, text=notification)
                except:
                    pass
        except ValueError:
            pass

    # Check channel membership
    if not await is_member(context.bot, user.id):
        await update.message.reply_text(
            get_text(user.id, "join_channels"),
            reply_markup=get_join_keyboard()
        )
        return

    # Save user
    USERS_DATA[str(user.id)] = {
        "username": user.username,
        "first_name": user.first_name,
        "last_seen": get_current_time()
    }

    # Daily check-in system
    today = datetime.now().date().isoformat()
    if profile.get("last_daily") != today:
        # Reset if streak broken (more than 1 day gap)
        if profile.get("last_daily"):
            last_date = datetime.fromisoformat(profile["last_daily"]).date()
            if (datetime.now().date() - last_date).days > 1:
                profile["streak"] = 0
        
        profile["streak"] += 1
        profile["last_daily"] = today
        update_user_profile(user.id, profile)
        
        # Daily rewards based on streak
        base_xp = 25
        base_coins = 50
        streak_bonus = min(profile["streak"] * 5, 100)  # Max 100 bonus
        
        daily_result = add_xp(user.id, base_xp + streak_bonus)
        add_coins(user.id, base_coins + streak_bonus)
        
        streak_msg = f"\n🎁 Daily Check-in Bonus!\n💰 +{base_coins + streak_bonus} coins\n⭐ +{base_xp + streak_bonus} XP\n🔥 {profile['streak']}-day streak!"
        
        # Check for achievements
        new_achievements = check_achievements(user.id)
        if new_achievements:
            streak_msg += f"\n🏆 New achievements unlocked!"
    else:
        streak_msg = f"\n🔥 Current streak: {profile['streak']} days!"

    # Welcome message with user stats
    profile = get_user_profile(user.id)  # Refresh profile data
    caption = get_text(user.id, "welcome", profile["level"], format_number(profile["coins"]), profile["streak"]) + streak_msg

    await update.message.reply_photo(
        photo=WELCOME_IMAGE_ID,
        caption=caption,
        parse_mode="HTML",
        reply_markup=get_main_keyboard(user.id)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comprehensive help command."""
    help_text = """
🤖 <b>PRIME MODS BOT - Ultimate Guide</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🔑 Key Generation System:</b>
• Generate premium keys through referrals
• Key types: Standard → Premium → VIP → Elite → Legendary
• Higher levels unlock better keys automatically

<b>👥 Referral System:</b>
• Share your unique referral link
• Earn coins, XP, and achievements
• Requirements scale with your level

<b>🎮 Gaming Zone (6 Games):</b>
• Number Guessing - Multiple difficulties
• Trivia Quiz - Various categories
• Math Challenge - Test your skills
• Riddle Master - Brain teasers
• Memory Game - Challenge memory
• Word Puzzle - Find hidden words

<b>🏆 Achievements & Progression:</b>
• 10 unique achievements to unlock
• Level up system with XP
• Daily streak rewards
• Coin-based economy

<b>💰 Shop System:</b>
• Buy hints, power-ups, and premium features
• VIP passes for exclusive benefits
• Custom themes and utilities

<b>🌐 Utilities & Features:</b>
• Weather information
• Cryptocurrency prices
• Daily facts and motivational quotes
• Random generators and fortune cookies

<b>📊 Advanced Features:</b>
• Personal statistics tracking
• Leaderboard competitions
• Daily challenges
• Multi-language support
• Admin panel (for admins)

<b>💡 Pro Tips:</b>
• Play games daily for bonus coins
• Maintain your streak for bigger rewards
• Refer friends to unlock better keys faster
• Check achievements regularly

Need specific help? Use the menu buttons! 🚀
"""
    
    await update.message.reply_text(
        help_text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
        ])
    )

# ---------------- Callback Query Handlers ----------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced callback handler with all features."""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data

    # Initialize user profile
    profile = get_user_profile(user.id)

    try:
        # Main menu navigation
        if data == "back_to_main":
            profile = get_user_profile(user.id)  # Refresh data
            caption = get_text(user.id, "welcome", profile["level"], format_number(profile["coins"]), profile["streak"])
            await query.edit_message_caption(
                caption=caption,
                parse_mode="HTML",
                reply_markup=get_main_keyboard(user.id)
            )

        # User Profile
        elif data == "profile":
            level = profile["level"]
            xp = profile["xp"]
            next_level_xp = (level ** 2) * 100
            current_level_xp = ((level - 1) ** 2) * 100
            progress_xp = xp - current_level_xp
            needed_xp = next_level_xp - current_level_xp
            progress = min((progress_xp / needed_xp) * 20, 20)
            progress_bar = "█" * int(progress) + "░" * (20 - int(progress))
            
            # Calculate win rate
            total_games = profile["games_won"] + profile["games_lost"]
            win_rate = (profile["games_won"] / total_games * 100) if total_games > 0 else 0
            
            profile_text = f"""
👤 <b>{user.first_name}'s Profile</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>Level:</b> {level} ⭐ <b>XP:</b> {xp:,}
{progress_bar} {progress_xp}/{needed_xp}

💰 <b>Coins:</b> {format_number(profile['coins'])}
🔑 <b>Keys Generated:</b> {profile['keys_generated']}

🎮 <b>Gaming Stats:</b>
• Games Won: {profile['games_won']}
• Games Lost: {profile['games_lost']}
• Win Rate: {win_rate:.1f}%

👥 <b>Social Stats:</b>
• Referrals: {profile['referrals']}
• Daily Streak: {profile['streak']} days

🏆 <b>Achievements:</b> {len(profile['achievements'])}/{len(ACHIEVEMENTS)}
🌍 <b>Language:</b> {profile['language'].upper()}
📅 <b>Member Since:</b> {profile['created_at'][:10]}

🎯 <b>Status:</b> {"👑 VIP Member" if profile['vip_level'] > 0 else "🌟 Standard Member"}
"""
            
            await query.edit_message_caption(
                caption=profile_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("🏆 Achievements", callback_data="achievements"),
                        InlineKeyboardButton("📊 Game Stats", callback_data="game_stats")
                    ],
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
                ])
            )

        # Key Generation
        elif data == "generate_key":
            level = profile["level"]
            required_refs = calculate_referral_requirement(level)
            current_refs = profile["referrals"]
            
            if current_refs < required_refs:
                link = f"https://t.me/{BOT_USERNAME}?start=ref{user.id}"
                progress = (current_refs / required_refs) * 10
                progress_bar = "█" * int(progress) + "░" * (10 - int(progress))
                
                await query.edit_message_caption(
                    caption=get_text(user.id, "referral_needed", required_refs, current_refs, required_refs) + 
                           f"\n{progress_bar}\n\n🔗 Your referral link:\n<code>{link}</code>",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📨 Share Link", url=f"https://t.me/share/url?url={link}")],
                        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
                    ])
                )
            else:
                # Generate key based on user level
                if level >= 50:
                    key_type = "legendary"
                elif level >= 20:
                    key_type = "elite"
                elif level >= 10:
                    key_type = "vip"
                elif level >= 5:
                    key_type = "premium"
                else:
                    key_type = "standard"
                
                key_data = generate_key(key_type, level)
                profile["keys_generated"] += 1
                update_user_profile(user.id, {"keys_generated": profile["keys_generated"]})
                
                # Update bot stats
                BOT_STATS["total_keys"] += 1
                
                # Achievement check
                new_achievements = check_achievements(user.id)
                achievement_msg = "\n🏆 Achievement unlocked!" if new_achievements else ""
                
                features_text = "\n🎯 <b>Features:</b>\n• " + "\n• ".join(key_data["features"])
                
                await query.edit_message_caption(
                    caption=get_text(user.id, "key_generated", key_data["key"], key_data["expires"], 
                                   "Unlimited" if key_data["uses_remaining"] == -1 else key_data["uses_remaining"]) +
                           f"\n🏷️ <b>Type:</b> {key_data['type']}" + features_text + achievement_msg,
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"📋 Copy: {key_data['key']}", callback_data=f"copy_{key_data['key']}")],
                        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
                    ])
                )

        # Games Menu
        elif data == "games_menu":
            await query.edit_message_caption(
                caption="🎮 <b>Gaming Zone - Choose Your Challenge!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🏆 Win games to earn coins and XP!\n🎯 Each game offers unique rewards\n⚡ Play daily for bonus multipliers!",
                parse_mode="HTML",
                reply_markup=get_games_keyboard()
            )

        # Game: Number Guessing
        elif data == "game_guess_number":
            # Check if user has active game
            active_game = get_active_game(user.id)
            if active_game and active_game["type"] == "guess_number":
                remaining = active_game["max_attempts"] - active_game["attempts"]
                await query.edit_message_caption(
                    caption=f"🎯 <b>Number Guessing Game Active!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🎲 Range: {active_game['range'][0]} - {active_game['range'][1]}\n🎯 Attempts remaining: {remaining}\n💡 Difficulty: {active_game['difficulty'].title()}\n\n📝 Send your guess as a number!",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("❌ Quit Game", callback_data="quit_game")],
                        [InlineKeyboardButton("🔙 Back to Games", callback_data="games_menu")]
                    ])
                )
            else:
                await query.edit_message_caption(
                    caption="🎯 <b>Number Guessing Game</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🎲 I'm thinking of a number...\n🎯 Your job is to guess it!\n💰 Rewards based on difficulty\n⚡ Speed bonus available!\n\n🎚️ Choose difficulty:",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton("🟢 Easy (1-50)", callback_data="start_guess_easy"),
                            InlineKeyboardButton("🟡 Normal (1-100)", callback_data="start_guess_normal")
                        ],
                        [
                            InlineKeyboardButton("🔴 Hard (1-200)", callback_data="start_guess_hard"),
                            InlineKeyboardButton("⚫ Expert (1-500)", callback_data="start_guess_expert")
                        ],
                        [InlineKeyboardButton("🔙 Back to Games", callback_data="games_menu")]
                    ])
                )

        # Start number guessing with difficulty
        elif data.startswith("start_guess_"):
            difficulty = data.replace("start_guess_", "")
            game_session = GameEngine.start_number_guessing(difficulty)
            set_active_game(user.id, game_session)
            
            diff_info = {
                "easy": "🟢 Easy: 1-50, 8 attempts",
                "normal": "🟡 Normal: 1-100, 7 attempts", 
                "hard": "🔴 Hard: 1-200, 6 attempts",
                "expert": "⚫ Expert: 1-500, 5 attempts"
            }
            
            await query.edit_message_caption(
                caption=f"🎯 <b>Number Guessing Started!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{diff_info[difficulty]}\n🎲 I've picked my number!\n⚡ Quick guesses get bonus points\n\n📝 Send your first guess!",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Quit Game", callback_data="quit_game")],
                    [InlineKeyboardButton("💡 Get Hint", callback_data="game_hint")]
                ])
            )

        # Game: Trivia
        elif data == "game_trivia":
            question = GameEngine.get_trivia_question("general")
            set_active_game(user.id, {"type": "trivia", "question": question, "start_time": time.time()})
            
            options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(question["options"])])
            
            await query.edit_message_caption(
                caption=f"🧠 <b>Trivia Challenge</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{question['question']}\n\n{options_text}\n\n📝 Reply with A, B, C, or D!",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("A", callback_data="trivia_0"),
                        InlineKeyboardButton("B", callback_data="trivia_1"),
                        InlineKeyboardButton("C", callback_data="trivia_2"),
                        InlineKeyboardButton("D", callback_data="trivia_3")
                    ],
                    [InlineKeyboardButton("❌ Quit Game", callback_data="quit_game")]
                ])
            )

        # Trivia answer handling
        elif data.startswith("trivia_"):
            active_game = get_active_game(user.id)
            if active_game and active_game["type"] == "trivia":
                answer = int(data.split("_")[1])
                question = active_game["question"]
                time_taken = time.time() - active_game["start_time"]
                
                if answer == question["correct"]:
                    # Calculate rewards
                    base_reward = GAMES_CONFIG["trivia"]["reward"]
                    speed_bonus = max(0, 50 - int(time_taken)) if time_taken < 10 else 0
                    total_coins = base_reward + speed_bonus
                    
                    # Update user stats
                    profile["games_won"] += 1
                    add_coins(user.id, total_coins)
                    xp_result = add_xp(user.id, 30)
                    update_user_profile(user.id, {"games_won": profile["games_won"]})
                    
                    # Check achievements
                    new_achievements = check_achievements(user.id)
                    clear_active_game(user.id)
                    
                    result_msg = f"🎉 <b>Correct!</b>\n\n✅ {question['explanation']}\n💰 +{total_coins} coins\n⭐ +30 XP"
                    if speed_bonus > 0:
                        result_msg += f"\n⚡ Speed bonus: +{speed_bonus}"
                    if xp_result["level_up"]:
                        result_msg += f"\n🎊 Level up! Now level {xp_result['new_level']}"
                    
                else:
                    profile["games_lost"] += 1
                    update_user_profile(user.id, {"games_lost": profile["games_lost"]})
                    clear_active_game(user.id)
                    
                    result_msg = f"❌ <b>Wrong Answer!</b>\n\n✅ Correct: {question['options'][question['correct']]}\n📚 {question['explanation']}\n💪 Better luck next time!"
                
                await query.edit_message_caption(
                    caption=result_msg,
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 Play Again", callback_data="game_trivia")],
                        [InlineKeyboardButton("🔙 Back to Games", callback_data="games_menu")]
                    ])
                )

        # Math Game
        elif data == "game_math":
            problem = GameEngine.get_math_problem("normal")
            set_active_game(user.id, {"type": "math", "problem": problem, "start_time": time.time()})
            
            options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(problem["options"])])
            
            await query.edit_message_caption(
                caption=f"🔢 <b>Math Challenge</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{problem['question']}\n\n{options_text}\n\n📝 Choose the correct answer!",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("A", callback_data="math_0"),
                        InlineKeyboardButton("B", callback_data="math_1"),
                        InlineKeyboardButton("C", callback_data="math_2"),
                        InlineKeyboardButton("D", callback_data="math_3")
                    ],
                    [InlineKeyboardButton("❌ Quit Game", callback_data="quit_game")]
                ])
            )

        # Math answer handling
        elif data.startswith("math_"):
            active_game = get_active_game(user.id)
            if active_game and active_game["type"] == "math":
                answer = int(data.split("_")[1])
                problem = active_game["problem"]
                time_taken = time.time() - active_game["start_time"]
                
                if answer == problem["correct"]:
                    base_reward = GAMES_CONFIG["math"]["reward"]
                    speed_bonus = max(0, 40 - int(time_taken)) if time_taken < 8 else 0
                    total_coins = base_reward + speed_bonus
                    
                    profile["games_won"] += 1
                    add_coins(user.id, total_coins)
                    xp_result = add_xp(user.id, 25)
                    update_user_profile(user.id, {"games_won": profile["games_won"]})
                    
                    clear_active_game(user.id)
                    
                    result_msg = f"🎉 <b>Correct!</b> {problem['answer']}\n\n💰 +{total_coins} coins\n⭐ +25 XP"
                    if speed_bonus > 0:
                        result_msg += f"\n⚡ Speed bonus: +{speed_bonus}"
                    if xp_result["level_up"]:
                        result_msg += f"\n🎊 Level up! Now level {xp_result['new_level']}"
                        
                else:
                    profile["games_lost"] += 1
                    update_user_profile(user.id, {"games_lost": profile["games_lost"]})
                    clear_active_game(user.id)
                    
                    result_msg = f"❌ <b>Wrong!</b> Correct answer: {problem['answer']}\n\n💪 Keep practicing!"
                
                await query.edit_message_caption(
                    caption=result_msg,
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 Play Again", callback_data="game_math")],
                        [InlineKeyboardButton("🔙 Back to Games", callback_data="games_menu")]
                    ])
                )

        # Riddle Game
        elif data == "game_riddle":
            riddle = GameEngine.get_riddle()
            set_active_game(user.id, {"type": "riddle", "riddle": riddle, "start_time": time.time(), "hint_used": False})
            
            await query.edit_message_caption(
                caption=f"🤔 <b>Riddle Master</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{riddle['question']}\n\n🧠 Think carefully and send your answer!\n💡 You can ask for a hint if needed",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💡 Get Hint", callback_data="riddle_hint")],
                    [InlineKeyboardButton("❌ Quit Game", callback_data="quit_game")]
                ])
            )

        # Riddle hint
        elif data == "riddle_hint":
            active_game = get_active_game(user.id)
            if active_game and active_game["type"] == "riddle":
                riddle = active_game["riddle"]
                active_game["hint_used"] = True
                set_active_game(user.id, active_game)
                
                await query.answer(f"💡 Hint: {riddle['hint']}", show_alert=True)


        # Shop
        elif data == "shop":
            profile = get_user_profile(user.id)
            await query.edit_message_caption(
                caption=f"🛒 <b>Premium Shop</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n💰 Your Coins: {format_number(profile['coins'])}\n🎯 Buy power-ups and premium items\n✨ Enhance your gaming experience\n\n🛍️ Choose an item:",
                parse_mode="HTML",
                reply_markup=get_shop_keyboard(user.id)
            )

        # Shop purchases
        elif data.startswith("buy_"):
            item = data.replace("buy_", "")
            profile = get_user_profile(user.id)
            
            prices = {
                "hints": 50, "powerup": 100, "timefreeze": 150,
                "double": 200, "vip": 500, "theme": 300
            }
            
            if item in prices and profile["coins"] >= prices[item]:
                profile["coins"] -= prices[item]
                
                if item == "hints":
                    profile["inventory"]["hints"] += 3
                elif item == "powerup":
                    profile["inventory"]["power_ups"] += 1
                elif item == "timefreeze":
                    profile["inventory"]["time_freeze"] += 1
                elif item == "vip":
                    profile["vip_level"] = 1
                
                update_user_profile(user.id, profile)
                await query.answer(f"✅ Purchase successful! -{prices[item]} coins", show_alert=True)
            else:
                await query.answer("❌ Insufficient coins!", show_alert=True)

        # Achievements
        elif data == "achievements":
            profile = get_user_profile(user.id)
            user_achievements = profile["achievements"]
            
            achievement_list = []
            for achievement_id, achievement in ACHIEVEMENTS.items():
                status = "✅" if achievement_id in user_achievements else "🔒"
                achievement_list.append(f"{status} {achievement['emoji']} {achievement['name']}")
            
            achievements_text = f"""
🏆 <b>Achievement Gallery</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Progress: {len(user_achievements)}/{len(ACHIEVEMENTS)} unlocked

{chr(10).join(achievement_list)}

💰 Total Rewards Earned: {sum(ACHIEVEMENTS[a]['reward'] for a in user_achievements)} coins
"""
            
            await query.edit_message_caption(
                caption=achievements_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
                ])
            )

        # Leaderboard
        elif data == "leaderboard":
            # Sort users by referrals, then by level
            sorted_users = sorted(
                [(uid, profile) for uid, profile in PROFILES_DATA.items()],
                key=lambda x: (x[1]["referrals"], x[1]["level"]),
                reverse=True
            )[:10]
            
            leaderboard_text = "🏆 <b>Global Leaderboard</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
            for i, (user_id, user_profile) in enumerate(sorted_users):
                user_data = USERS_DATA.get(user_id, {})
                name = user_data.get("first_name", "Anonymous")[:15]
                leaderboard_text += f"{medals[i]} <b>{name}</b>\n"
                leaderboard_text += f"   👥 {user_profile['referrals']} referrals • Lv.{user_profile['level']}\n\n"
            
            await query.edit_message_caption(
                caption=leaderboard_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
                ])
            )

        # Quit game
        elif data == "quit_game":
            clear_active_game(user.id)
            await query.edit_message_caption(
                caption="❌ Game ended. No worries, try again anytime!",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎮 New Game", callback_data="games_menu")],
                    [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
                ])
            )

        # Copy key
        elif data.startswith("copy_"):
            key = data.replace("copy_", "")
            await query.answer(f"✅ Key copied: {key}", show_alert=True)

        # Admin panel
        elif data.startswith("admin_") and user.id == ADMIN_ID:
            if data == "admin_stats":
                stats_text = f"""
📊 <b>Bot Statistics</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 <b>Users:</b>
• Total Users: {len(PROFILES_DATA)}
• Daily Active: {BOT_STATS['daily_users']}
• New Today: {len([p for p in PROFILES_DATA.values() if p['created_at'][:10] == datetime.now().date().isoformat()])}

🎮 <b>Games:</b>
• Total Games Played: {sum(p['games_won'] + p['games_lost'] for p in PROFILES_DATA.values())}
• Active Game Sessions: {len(GAMES_DATA)}

🔑 <b>Keys:</b>
• Total Keys Generated: {sum(p['keys_generated'] for p in PROFILES_DATA.values())}
• Keys Today: {BOT_STATS.get('keys_today', 0)}

💰 <b>Economy:</b>
• Total Coins in Circulation: {sum(p['coins'] for p in PROFILES_DATA.values()):,}
• Average User Level: {sum(p['level'] for p in PROFILES_DATA.values()) / len(PROFILES_DATA):.1f}
"""
                await query.edit_message_caption(
                    caption=stats_text,
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 Refresh", callback_data="admin_stats")],
                        [InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel")]
                    ])
                )

        # Check join
        elif data == "check_join":
            if not await is_member(context.bot, user.id):
                await query.answer("❌ Please join all channels first!", show_alert=True)
                return
            
            # Save user and show welcome
            USERS_DATA[str(user.id)] = {
                "username": user.username,
                "first_name": user.first_name,
                "last_seen": get_current_time()
            }
            
            profile = get_user_profile(user.id)
            caption = get_text(user.id, "welcome", profile["level"], format_number(profile["coins"]), profile["streak"])
            
            await query.edit_message_caption(
                caption=f"✅ <b>Welcome to PRIME MODS!</b>\n\n{caption}",
                parse_mode="HTML",
                reply_markup=get_main_keyboard(user.id)
            )

        # Refresh status
        elif data == "refresh_status":
            if await is_member(context.bot, user.id):
                await query.answer("✅ All channels joined! Welcome!", show_alert=True)
                # Redirect to main menu
                profile = get_user_profile(user.id)
                caption = get_text(user.id, "welcome", profile["level"], format_number(profile["coins"]), profile["streak"])
                await query.edit_message_caption(
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=get_main_keyboard(user.id)
                )
            else:
                await query.answer("❌ Please join all required channels first!", show_alert=True)

    except Exception as e:
        logger.error(f"Error in button handler: {e}")
        await query.answer("⚠️ An error occurred. Please try again.", show_alert=True)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages for games and interactions."""
    user = update.effective_user
    
    # Check if message exists
    if not update.message or not update.message.text:
        return
        
    text = update.message.text.strip()
    
    # Check if user has active game
    active_game = get_active_game(user.id)
    
    if active_game:
        if active_game["type"] == "guess_number":
            try:
                guess = int(text)
                result = GameEngine.process_guess(active_game, guess)
                
                if result["status"] == "win":
                    # Award coins and XP
                    profile = get_user_profile(user.id)
                    profile["games_won"] += 1
                    
                    reward = result["reward"]
                    add_coins(user.id, reward)
                    xp_result = add_xp(user.id, 40)
                    update_user_profile(user.id, {"games_won": profile["games_won"]})
                    
                    # Check achievements
                    new_achievements = check_achievements(user.id)
                    clear_active_game(user.id)
                    
                    # Update bot stats
                    BOT_STATS["total_games"] += 1
                    
                    response = f"{result['message']}\n💰 +{reward} coins\n⭐ +40 XP"
                    if xp_result["level_up"]:
                        response += f"\n🎊 Level up! Now level {xp_result['new_level']}"
                    if new_achievements:
                        response += f"\n🏆 New achievements unlocked!"
                    
                    await update.message.reply_text(
                        response,
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🔄 Play Again", callback_data="game_guess_number")],
                            [InlineKeyboardButton("🔙 Games Menu", callback_data="games_menu")]
                        ])
                    )
                    
                elif result["status"] == "lose":
                    profile = get_user_profile(user.id)
                    profile["games_lost"] += 1
                    update_user_profile(user.id, {"games_lost": profile["games_lost"]})
                    clear_active_game(user.id)
                    
                    await update.message.reply_text(
                        result["message"],
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🔄 Try Again", callback_data="game_guess_number")],
                            [InlineKeyboardButton("🔙 Games Menu", callback_data="games_menu")]
                        ])
                    )
                    
                else:  # continue
                    set_active_game(user.id, active_game)
                    await update.message.reply_text(result["message"])
                    
            except ValueError:
                await update.message.reply_text("🔢 Please send a valid number!")
                
        elif active_game["type"] == "riddle":
            riddle = active_game["riddle"]
            user_answer = text.lower().strip()
            correct_answer = riddle["answer"].lower()
            
            if user_answer == correct_answer or user_answer in correct_answer:
                # Calculate reward (less if hint was used)
                base_reward = GAMES_CONFIG["riddle"]["reward"]
                hint_penalty = 10 if active_game.get("hint_used") else 0
                final_reward = base_reward - hint_penalty
                
                profile = get_user_profile(user.id)
                profile["games_won"] += 1
                
                add_coins(user.id, final_reward)
                xp_result = add_xp(user.id, 50)
                update_user_profile(user.id, {"games_won": profile["games_won"]})
                
                clear_active_game(user.id)
                
                response = f"🎉 <b>Correct!</b>\n\n📚 {riddle['explanation']}\n💰 +{final_reward} coins\n⭐ +50 XP"
                if hint_penalty:
                    response += f"\n💡 (-{hint_penalty} coins for using hint)"
                if xp_result["level_up"]:
                    response += f"\n🎊 Level up! Now level {xp_result['new_level']}"
                
                await update.message.reply_text(
                    response,
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 Another Riddle", callback_data="game_riddle")],
                        [InlineKeyboardButton("🔙 Games Menu", callback_data="games_menu")]
                    ])
                )
            else:
                await update.message.reply_text(
                    f"❌ Not quite right! Try again.\n💡 Hint: {riddle['hint']}"
                )
    
    else:
        # Regular message responses
        if text.lower() in ["hi", "hello", "hey"]:
            await update.message.reply_text(
                f"👋 Hello {user.first_name}! Ready for some gaming action?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🚀 Let's Go!", callback_data="back_to_main")]
                ])
            )
        elif "help" in text.lower():
            await help_command(update, context)
        else:
            await update.message.reply_text(
                "🤔 I didn't understand that. Use the menu buttons or type /help for assistance!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📱 Main Menu", callback_data="back_to_main")]
                ])
            )

# Admin Commands
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced broadcast command with image support and detailed stats."""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Admin access required.")
        return

    message = " ".join(context.args)
    if not message:
        await update.message.reply_text(
            "⚠️ <b>Broadcast Usage:</b>\n\n"
            "<code>/broadcast Your message here</code>\n\n"
            "📷 <b>To broadcast with image:</b>\n"
            "1. Send an image to this chat\n"
            "2. In caption, write: /broadcast Your message\n\n"
            "📊 Will show delivery statistics when complete!",
            parse_mode="HTML"
        )
        return

    users = list(USERS_DATA.keys())
    total_users = len(users)
    success_count = 0
    failed_count = 0
    start_time = time.time()
    
    # Send progress message
    progress_msg = await update.message.reply_text(
        f"📡 <b>Broadcasting to {total_users} users...</b>\n"
        f"⏳ Please wait...",
        parse_mode="HTML"
    )
    
    # Check if the command was sent with an image
    photo_to_send = None
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        photo_to_send = update.message.reply_to_message.photo[-1].file_id
    elif update.message.photo:
        photo_to_send = update.message.photo[-1].file_id
    
    for i, user_id in enumerate(users):
        try:
            if photo_to_send:
                # Send with custom image
                await context.bot.send_photo(
                    chat_id=int(user_id),
                    photo=photo_to_send,
                    caption=f"🔥 <b>FF H4CK BOT - Official Update</b> 🔥\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                            f"{message}\n\n"
                            f"👨‍💻 Developer: {DEVELOPER_USERNAME}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🚀 Open FF H4CK BOT", callback_data="back_to_main")]
                    ])
                )
            else:
                # Send with default image
                await context.bot.send_photo(
                    chat_id=int(user_id),
                    photo=WELCOME_IMAGE_ID,
                    caption=f"🔥 <b>FF H4CK BOT - Official Update</b> 🔥\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                            f"{message}\n\n"
                            f"👨‍💻 Developer: {DEVELOPER_USERNAME}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🚀 Open FF H4CK BOT", callback_data="back_to_main")]
                    ])
                )
            success_count += 1
            
            # Update progress every 50 users
            if (i + 1) % 50 == 0:
                await progress_msg.edit_text(
                    f"📡 <b>Broadcasting Progress</b>\n\n"
                    f"✅ Sent: {success_count}\n"
                    f"❌ Failed: {failed_count}\n"
                    f"📈 Progress: {i + 1}/{total_users} ({((i + 1)/total_users)*100:.1f}%)\n"
                    f"⏳ Please wait...",
                    parse_mode="HTML"
                )
            
            await asyncio.sleep(0.05)  # Rate limiting
            
        except Exception as e:
            failed_count += 1
            logger.error(f"Failed to send broadcast to {user_id}: {e}")
    
    # Calculate stats
    end_time = time.time()
    duration = end_time - start_time
    success_rate = (success_count / total_users) * 100 if total_users > 0 else 0
    
    # Send final statistics
    await progress_msg.edit_text(
        f"📢 <b>Broadcast Completed!</b>\n\n"
        f"📊 <b>Statistics:</b>\n"
        f"✅ Successfully sent: <b>{success_count}</b>\n"
        f"❌ Failed to send: <b>{failed_count}</b>\n"
        f"📈 Success rate: <b>{success_rate:.1f}%</b>\n"
        f"⏱️ Duration: <b>{duration:.1f} seconds</b>\n"
        f"📡 Messages per second: <b>{success_count/duration:.1f}</b>\n\n"
        f"👨‍💻 Admin: {DEVELOPER_USERNAME}",
        parse_mode="HTML"
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics (admin only)."""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Admin access required.")
        return
    
    total_users = len(PROFILES_DATA)
    total_games = sum(p["games_won"] + p["games_lost"] for p in PROFILES_DATA.values())
    total_coins = sum(p["coins"] for p in PROFILES_DATA.values())
    avg_level = sum(p["level"] for p in PROFILES_DATA.values()) / total_users if total_users > 0 else 0
    
    stats_text = f"""
📊 <b>Bot Statistics Dashboard</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 <b>Users:</b> {total_users}
🎮 <b>Games Played:</b> {total_games:,}
💰 <b>Total Coins:</b> {total_coins:,}
📊 <b>Average Level:</b> {avg_level:.1f}
🔑 <b>Keys Generated:</b> {sum(p['keys_generated'] for p in PROFILES_DATA.values())}
🏆 <b>Achievements Unlocked:</b> {sum(len(p['achievements']) for p in PROFILES_DATA.values())}

⚡ <b>Today:</b>
• Daily Users: {BOT_STATS['daily_users']}
• Active Games: {len(GAMES_DATA)}
"""
    
    await update.message.reply_text(stats_text, parse_mode="HTML")

# ---------------- Main Function ----------------
def main():
    """Start the bot with all enhanced features."""
    print("🔥 Initializing FF H4CK BOT...")
    print("🎮 Loading gaming system...")
    print("🏆 Setting up achievements...")
    print("💰 Initializing economy...")
    print("📱 Loading hack key system...")
    print("📢 Setting up broadcast system...")
    
    application = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_handler))

    print("✅ All systems loaded!")
    print("🔥 FF H4CK BOT is running with advanced features:")
    print("   • 6 Different Mini-Games with Rewards")
    print("   • 10 Unique Achievements to Unlock")
    print("   • Advanced Level & XP System")
    print("   • Coin Economy & Premium Shop")
    print("   • Enhanced Broadcast System")
    print("   • Admin Panel & Statistics")
    print("   • Daily Login Streaks & Bonuses")
    print("   • Referral/Invite System")
    print("   • Global Leaderboards")
    print("   • Free Fire Hack Key Generation")
    print(f"   • Developer Contact: {DEVELOPER_USERNAME}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()