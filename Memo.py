import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, List
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token from environment variable
TOKEN = os.environ.get('BOT_TOKEN', '8179385543:AAFr4IyXL3UPqC3aw9WAbUFwSTiW3UY1Lu8')

# Initialize bot
bot = telebot.TeleBot(TOKEN)

# Admin user ID for @Kelly_2121 - YOUR ACTUAL ID FROM @userinfobot
ADMIN_IDS = [7575562460]  # ← THIS IS YOUR CORRECT USER ID

# Channel information
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
    "admin_contact": "@Kelly_2121"
}
# Store user questions and admin states
user_questions: Dict[int, Dict[str, Any]] = {}
admin_states: Dict[int, Dict[str, Any]] = {}

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
    
    # Generate a unique question ID
    if questions:
        last_id = max([q.get('id', 0) for q in questions])
        new_id = last_id + 1
    else:
        new_id = 1
    
    question_data = {
        "id": new_id,
        "user_id": user_id,
        "username": username,
        "question": question,
        "timestamp": datetime.now().isoformat(),
        "answered": False,
        "answer": None,
        "answered_by": None,
        "answered_at": None
    }
    questions.append(question_data)
    
    with open(questions_file, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    
    return question_data

def get_unanswered_questions() -> List[Dict[str, Any]]:
    questions_file = 'data/questions.json'
    if not os.path.exists(questions_file):
        return []
    
    try:
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        return [q for q in questions if not q.get('answered', False)]
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def get_question_by_id(question_id: int) -> Dict[str, Any]:
    questions_file = 'data/questions.json'
    if not os.path.exists(questions_file):
        return None
    
    try:
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        for q in questions:
            if q.get('id') == question_id:
                return q
        return None
    except (json.JSONDecodeError, FileNotFoundError):
        return None

def update_question_answer(question_id: int, answer: str, admin_username: str) -> bool:
    questions_file = 'data/questions.json'
    if not os.path.exists(questions_file):
        return False
    
    try:
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        
        updated = False
        for q in questions:
            if q.get('id') == question_id:
                q['answered'] = True
                q['answer'] = answer
                q['answered_by'] = admin_username
                q['answered_at'] = datetime.now().isoformat()
                updated = True
                break
        
        if updated:
            with open(questions_file, 'w', encoding='utf-8') as f:
                json.dump(questions, f, indent=2, ensure_ascii=False)
        
        return updated
    except (json.JSONDecodeError, FileNotFoundError):
        return False

def is_admin(user_id: int) -> bool:
    is_admin_user = user_id in ADMIN_IDS
    logger.info(f"User {user_id} admin check: {is_admin_user}")
    return is_admin_user

def create_main_keyboard(is_admin_user=False):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    if is_admin_user:
        markup.add(
            KeyboardButton("View Questions"),
            KeyboardButton("Channel Info")
        )
    else:
        markup.add(
            KeyboardButton("About Channel"),
            KeyboardButton("Resources")
        )
        markup.add(
            KeyboardButton("Ask Question"),
            KeyboardButton("Contact Admin")
        )
        markup.add(KeyboardButton("Help"))
    
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    logger.info(f"User {message.from_user.id} started the bot")
    if is_admin(message.from_user.id):
        # Admin menu with quick replies
        bot.send_message(
            message.chat.id,
            f"Hi Admin {message.from_user.first_name}! 👋\n\n"
            f"Welcome to {CHANNEL_INFO['name']} Admin Panel!\n\n"
            "You can view and answer user questions from here.",
            reply_markup=create_main_keyboard(is_admin_user=True)
        )
    else:
        # User menu with quick replies
        bot.send_message(
            message.chat.id,
            f"Hi {message.from_user.first_name}! 👋\n\n"
            f"Welcome to {CHANNEL_INFO['name']} Bot!\n\n"
            "I'm here to help you with everything related to machine learning and programming.",
            reply_markup=create_main_keyboard()
        )

@bot.message_handler(commands=['debug'])
def debug_command(message):
    if is_admin(message.from_user.id):
        questions = get_unanswered_questions()
        debug_info = (
            f"Admin ID: {message.from_user.id}\n"
            f"Configured Admin IDs: {ADMIN_IDS}\n"
            f"Is Admin: {is_admin(message.from_user.id)}\n"
            f"Unanswered Questions: {len(questions)}\n"
            f"Data file exists: {os.path.exists('data/questions.json')}"
        )
        bot.send_message(message.chat.id, f"Debug Info:\n{debug_info}")
    else:
        bot.send_message(message.chat.id, "This command is for admins only.")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "🆘 *Help Menu*\n\n"
        "Here is the available commands and options: \n"
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
        parse_mode='Markdown',
        reply_markup=create_main_keyboard(is_admin(message.from_user.id))
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    # Handle quick reply button responses
    if message.text == "About Channel":
        topics_list = "\n".join([f"• {topic}" for topic in CHANNEL_INFO['topics']])
        bot.send_message(
            message.chat.id,
            f"📢 About {CHANNEL_INFO['name']} 📢\n\n"
            f"{CHANNEL_INFO['description']}\n\n"
            f"Topics we cover:\n{topics_list}",
            reply_markup=create_main_keyboard(is_admin(user_id))
        )
    
    elif message.text == "Resources":
        beginner = "\n".join([f"[{r['name']}]({r['url']})" for r in CHANNEL_INFO['resources']['beginner']])
        intermediate = "\n".join([f"[{r['name']}]({r['url']})" for r in CHANNEL_INFO['resources']['intermediate']])
        bot.send_message(
            message.chat.id,
            f"📚 *Resources*\n\n"
            f"*Beginner:*\n{beginner}\n\n"
            f"*Intermediate:*\n{intermediate}",
            parse_mode='Markdown',
            reply_markup=create_main_keyboard(is_admin(user_id))
        )
    
    elif message.text == "Ask Question":
        user_questions[user_id] = {"state": "awaiting_question"}
        bot.send_message(
            message.chat.id,
            "❓ Please type your question. "
            "Our admin @Kelly_2121 will respond as soon as possible!",
            reply_markup=ReplyKeyboardRemove()
        )
    
    elif message.text == "Contact Admin":
        bot.send_message(
            message.chat.id,
            f"👨‍💼 Contact Admin 👨‍💼\n\n"
            f"Admin: @Kelly_2121\n\n"
            f"Feel free to contact our admin directly for any questions or assistance. "
            f"You can also use the 'Ask Question' button to submit your questions through the bot.",
            reply_markup=create_main_keyboard(is_admin(user_id))
        )
    
    elif message.text == "Help":
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
            parse_mode='Markdown',
            reply_markup=create_main_keyboard(is_admin(user_id))
        )
    
    elif message.text == "View Questions" and is_admin(user_id):
        questions = get_unanswered_questions()
        if not questions:
            bot.send_message(
                message.chat.id,
                "No unanswered questions at the moment.",
                reply_markup=create_main_keyboard(is_admin=True)
            )
            return
        
        # Show first question with inline navigation
        question = questions[0]
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("Answer", callback_data=f"admin_answer_{question['id']}"),
            InlineKeyboardButton("Next", callback_data=f"admin_next_{1}_{len(questions)}")
        )
        
        bot.send_message(
            message.chat.id,
            f"Question #{question['id']} from @{question['username']}:\n\n"
            f"{question['question']}\n\n"
            f"Asked at: {datetime.fromisoformat(question['timestamp']).strftime('%Y-%m-%d %H:%M')}",
            reply_markup=keyboard
        )
    
    elif message.text == "Channel Info" and is_admin(user_id):
        topics_list = "\n".join([f"• {topic}" for topic in CHANNEL_INFO['topics']])
        bot.send_message(
            message.chat.id,
            f"📢 About {CHANNEL_INFO['name']} 📢\n\n"
            f"{CHANNEL_INFO['description']}\n\n"
            f"Topics we cover:\n{topics_list}",
            reply_markup=create_main_keyboard(is_admin=True)
        )
    
    # Handle user questions
    elif user_id in user_questions and user_questions[user_id].get("state") == "awaiting_question":
        question_data = save_question(user_id, username, message.text)
        bot.send_message(
            message.chat.id,
            "✅ Question Received! ✅\n\n"
            f"Your question (ID: {question_data['id']}) has been recorded. "
            "Our admin @Kelly_2121 will respond soon.",
            reply_markup=create_main_keyboard(is_admin(user_id))
        )
        user_questions[user_id] = {"state": "idle"}
        
        # Notify admins about new question
        for admin_id in ADMIN_IDS:
            try:
                bot.send_message(
                    admin_id,
                    f"❓ New Question #{question_data['id']} from @{username}:\n\n"
                    f"{message.text}\n\n"
                    f"Use /start to view and answer questions."
                )
                logger.info(f"Notification sent to admin {admin_id}")
            except Exception as e:
                logger.error(f"Failed to notify admin {admin_id}: {e}")
                # Try to notify the admin about the error
                try:
                    bot.send_message(
                        admin_id,
                        f"⚠️ Error sending notification: {e}\n\n"
                        f"Check if the bot can message you and your user ID is correct."
                    )
                except:
                    pass
    
    # Handle admin answers
    elif user_id in admin_states and admin_states[user_id].get("state") == "answering_question":
        question_id = admin_states[user_id]["question_id"]
        question = get_question_by_id(question_id)
        
        if question and update_question_answer(question_id, message.text, "@Kelly_2121"):
            # Send answer to user
            try:
                bot.send_message(
                    question['user_id'],
                    f"📩 Answer to your question (ID: {question_id}):\n\n"
                    f"{message.text}\n\n"
                    f"Answered by: @Kelly_2121"
                )
            except Exception as e:
                logger.error(f"Failed to send answer to user {question['user_id']}: {e}")
                bot.send_message(
                    user_id,
                    f"❌ Could not send answer to user. They may have blocked the bot or never started it."
                )
            
            # Confirm to admin
            bot.send_message(
                user_id,
                f"✅ Answer sent to user @{question['username']} for question #{question_id}.",
                reply_markup=create_main_keyboard(is_admin=True)
            )
        else:
            bot.send_message(
                user_id,
                "❌ Failed to send answer. Question might not exist.",
                reply_markup=create_main_keyboard(is_admin=True)
            )
        
        admin_states[user_id] = {"state": "idle"}
    
    else:
        if is_admin(user_id):
            bot.send_message(
                message.chat.id,
                "Welcome admin! Use the quick reply buttons to manage questions.",
                reply_markup=create_main_keyboard(is_admin=True)
            )
        else:
            bot.send_message(
                message.chat.id,
                "Thanks for your message! Use the buttons below to interact with me.",
                reply_markup=create_main_keyboard()
            )

# Keep the callback handlers for admin navigation
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    logger.info(f"Callback from user {user_id}: {call.data}")
    
    # Admin-specific callbacks (for question navigation)
    if call.data.startswith('admin_next_') and is_admin(user_id):
        # Extract current index and total from callback data
        parts = call.data.split('_')
        current_index = int(parts[2])
        total_questions = int(parts[3])
        
        questions = get_unanswered_questions()
        if not questions:
            bot.edit_message_text(
                "No unanswered questions at the moment.",
                call.message.chat.id,
                call.message.message_id
            )
            return
        
        # Calculate next index
        next_index = (current_index + 1) % total_questions
        question = questions[next_index]
        
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("Answer", callback_data=f"admin_answer_{question['id']}"),
            InlineKeyboardButton("Next", callback_data=f"admin_next_{next_index}_{total_questions}")
        )
        
        bot.edit_message_text(
            f"Question #{question['id']} from @{question['username']}:\n\n"
            f"{question['question']}\n\n"
            f"Asked at: {datetime.fromisoformat(question['timestamp']).strftime('%Y-%m-%d %H:%M')}",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )
    
    elif call.data.startswith('admin_answer_') and is_admin(user_id):
        question_id = int(call.data.split('_')[2])
        admin_states[user_id] = {"state": "answering_question", "question_id": question_id}
        
        bot.edit_message_text(
            f"Please type your answer for question #{question_id}:",
            call.message.chat.id,
            call.message.message_id
        )

if __name__ == '__main__':
    print("Bot is running...")
    print(f"Admin IDs configured: {ADMIN_IDS}")
    bot.infinity_polling()

