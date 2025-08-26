import logging
import json
import os
from datetime import datetime
from typing import Dict, Any
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token from environment variable or use placeholder
TOKEN = os.environ.get('BOT_TOKEN', '8179385543:AAFr4IyXL3UPqC3aw9WAbUFwSTiW3UY1Lu8')

# Initialize bot
bot = telebot.TeleBot(TOKEN)

# Channel information - customize this
CHANNEL_INFO = {
    "name": "MEMO",
    "description": "My channel MEMO, created in late 2024,"
    " is built as a collaborative hub for programmers across different domains to learn, "
    "share, and grow together. It focuses on empowering developers by providing resources and guidance "
    "in Machine Learning (ML), Artificial Intelligence (AI), and Web Development, while also tackling tricky "
    "real-world coding problems alongside the founder of MEMO. The vision behind the channel is not only"
    " to offer tutorials and resources but also to create a community where programmers can connect,"
    " exchange knowledge, and support each other in solving challenges. By combining practical"
    " problem-solving with cutting-edge technology insights, MEMO stands as a space for both beginners "
    "and experienced developers to continuously improve and stay ahead in the rapidly evolving world of "
    "tech.",
    "topics": ["Machine Learning", "Python", "Deep Learning", "Data Science", "AI"],
    "resources": {
        "beginner": [
            {"name": "Python Basics", "url": "https://yourchannel.com/python-basics"},
            {"name": "ML Introduction", "url": "https://yourchannel.com/ml-intro"}
        ],
        "intermediate": [
            {"name": "Data Visualization", "url": "https://yourchannel.com/data-viz"},
            {"name": "ML Algorithms", "url": "https://yourchannel.com/ml-algorithms"}
        ]
    },
    "admin_contact": "@yourusername"
}

# Store user questions
user_questions: Dict[int, Dict[str, Any]] = {}

# Create data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

def save_question(user_id: int, username: str, question: str) -> Dict[str, Any]:
    questions_file = 'data/questions.json'
    questions = []
    if os.path.exists(questions_file):
        try:
            with open(questions_file, 'r', encoding='utf-8') as f:
                questions = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            questions = []
    question_data = {
        "user_id": user_id,
        "username": username,
        "question": question,
        "timestamp": datetime.now().isoformat(),
        "answered": False
    }
    questions.append(question_data)
    with open(questions_file, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    return question_data

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("About Channel", callback_data='about'),
        InlineKeyboardButton("Resources", callback_data='resources')
    )
    keyboard.add(
        InlineKeyboardButton("Ask Question", callback_data='ask_question'),
        InlineKeyboardButton("Contact Admin", callback_data='contact')
    )
    keyboard.add(
        InlineKeyboardButton("Help", callback_data='help_menu')
    )
    bot.send_message(
        message.chat.id,
        f"Hi {message.from_user.first_name}! 👋\n\n"
        f"Welcome to {CHANNEL_INFO['name']} Bot!\n\n"
        "I'm here to help you with everything related to machine learning and programming.",
        reply_markup=keyboard
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "🆘 *Help Menu*\n\n"
        "Here are the available commands and options:\n"
        "/start - Show the main menu\n"
        "/help - Show this help message\n\n"
        "You can also use the buttons to:\n"
        "• Learn about the channel\n"
        "• Access learning resources\n"
        "• Ask a programming or ML question\n"
        "• Contact the admin\n\n"
        "To ask a question, click 'Ask Question' and type your question.\n"
        "If you need further assistance, contact the admin.\n"
        "And also join the channel(https://t.me/codewithmemo) for more updates."
    )
    bot.send_message(
        message.chat.id,
        help_text,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == 'about':
        topics_list = "\n".join([f"• {topic}" for topic in CHANNEL_INFO['topics']])
        bot.edit_message_text(
            f"📢 About {CHANNEL_INFO['name']} 📢\n\n"
            f"{CHANNEL_INFO['description']}\n\n"
            f"Topics we cover:\n{topics_list}",
            call.message.chat.id,
            call.message.message_id
        )
    elif call.data == 'resources':
        beginner = "\n".join([f"[{r['name']}]({r['url']})" for r in CHANNEL_INFO['resources']['beginner']])
        intermediate = "\n".join([f"[{r['name']}]({r['url']})" for r in CHANNEL_INFO['resources']['intermediate']])
        bot.edit_message_text(
            f"📚 *Resources*\n\n"
            f"*Beginner:*\n{beginner}\n\n"
            f"*Intermediate:*\n{intermediate}",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
    elif call.data == 'ask_question':
        user_questions[call.from_user.id] = {"state": "awaiting_question"}
        bot.edit_message_text(
            "❓ Please type your question. "
            "Our team will respond as soon as possible!",
            call.message.chat.id,
            call.message.message_id
        )
    elif call.data == 'contact':
        bot.edit_message_text(
            f"👨‍💼 Contact Admin 👨‍💼\n\n"
            f"📚 About Me: I am a third-year Information Systems student at "
            f"Addis Ababa University, passionate about technology, programming, and problem-solving.\n"
            f" I enjoy working on projects related to Machine Learning, Artificial Intelligence, and Web "
            f"Development, while also helping others overcome tricky coding challenges.\n"
            f"📞 Mobile: +251 922 545 447\n"
            f"💬 Telegram: @ze_meryma_21",
            call.message.chat.id,
            call.message.message_id
        )
    elif call.data == 'help_menu':
        help_text = (
            "🆘 *Help Menu*\n\n"
            "Here are the available commands and options:\n"
            "/start - Show the main menu\n"
            "/help - Show this help message\n\n"
            "You can also use the buttons to:\n"
            "• Learn about the channel\n"
            "• Access learning resources\n"
            "• Ask a programming or ML question\n"
            "• Contact the admin\n\n"
            "To ask a question, click 'Ask Question' and type your question.\n"
            "If you need further assistance, contact the admin.\n"
            "And also join the channel(https://t.me/codewithmemo) for more updates."
        )
        bot.edit_message_text(
            help_text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    if user_id in user_questions and user_questions[user_id].get("state") == "awaiting_question":
        save_question(user_id, username, message.text)
        bot.send_message(
            message.chat.id,
            "✅ Question Received! ✅\n\n"
            "Thank you for your question! Our team will review it and respond soon."
        )
        user_questions[user_id] = {"state": "idle"}
    else:
        bot.send_message(
            message.chat.id,
            "Thanks for your message! Use /start to see available options."
        )

if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()