from core.logger import logger 
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.validator import validate_name, validate_email, validate_phone
from core.database import save_lead, get_lead_by_telegram_id
from config import Config

# Possible states a user can be in,think of it like steps in form
WAITING_NAME = 'waiting_name'
WAITING_EMAIL = 'waiting_email'
WAITING_PHONE = 'waiting_phone'
WAITING_SERVICE = 'waiting_service'
WAITING_REQUIREMENT = 'waiting_requirement'
DONE = 'done'

def get_user_data(context) -> dict:
    """
    Returns current user's collected data.
    context.user_data is a dictionary Telegram gives us
    that persists throughout the conversation automatically.
    No need for separate memory.py this time!
    """
    if 'lead' not in  context.user_data:
        context.user_data['lead'] = {
            "state": WAITING_NAME,
            "name": None,
            "email": None,
            "phone": None,
            "service": None,
            "requirement":None
        }
    return context.user_data['lead']

def get_service_keyboard() -> InlineKeyboardMarkup:
    """Builds service selection buttons from config"""
    keyboard = []
    for i, service in enumerate(Config.SERVICES):
        # Use index number instead of full service name
        # "service_0" instead of "service_Web Development"
        keyboard.append([
            InlineKeyboardButton(service, callback_data=f"svc_{i}")
        ])
    return InlineKeyboardMarkup(keyboard)

#  ──── /start handler ────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Reset data every time user types /start
    context.user_data['lead'] = {
        "state": WAITING_NAME,
        "name": None,
        "email": None,
        "phone": None,
        "service": None,
        "requirement": None
    }
    logger.info(f"New user started: {user.id} - {user.first_name}")

    await update.message.reply_text(
        f"👋 Welcome to *{Config.COMPANY_NAME}*!\n\n"
        f"I'm *{Config.AGENT_NAME}*, your assistant.\n\n"
        "I'll collect your details so our team can get back to you.\n\n"
        "Let's start! What's your *full name*?",
        parse_mode="Markdown"
    )

# ──── Main message handler ──────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.effective_message.text.strip()

    await context.bot.send_chat_action(
    chat_id=update.effective_chat.id,
    action="typing"
    )
    
    lead = get_user_data(context)
    state = lead['state']

    # Route to correct handler based on current state
    if state == WAITING_NAME:
        await handle_name(update, context, lead, text)
    elif state == WAITING_EMAIL:
        await handle_email(update, context, lead, text)
    elif state == WAITING_PHONE:
        await handle_phone(update, context, lead, text)
    elif state == WAITING_REQUIREMENT:
        await handle_requirement(update, context, lead, text)
    elif state == DONE:
        await update.message.reply_text(
            "✅ We already have your details!\n\n"
            "Our team will contact your soon.\n"
            "Type /start to submit a new request"
        )    

# ──── Individual step handlers ──────────────────────────────

async def handle_name(update, context, lead, text):
    if not validate_name(text):
        await update.message.reply_text(
            "❌ Please enter a valid name.\n"
            "Example: *John Smith* or *Michael J*",
            parse_mode="Markdown"
        )
        return
    
    # Save name and move to next state
    lead['name'] = text
    lead['state'] = WAITING_EMAIL

    logger.info(f"Name collected: {text}")

    await update.message.reply_text(
        f"Nice to meet you, *{text}*! 😊\n\n"
        "what's your *email address*?",
        parse_mode="Markdown"
    )

async def handle_email(update, context, lead, text):
    if not validate_email(text):
        await update.message.reply_text(
            "❌ Please enter a valid email.\n"
            "Example: *john@gmail.com*",
            parse_mode='Markdown'
        )
        return
    
    lead['email'] = text
    lead['state'] = WAITING_PHONE

    logger.info(f"Email collected: {text}")

    await update.message.reply_text(
        "Got it! 📧\n\n"
        "What's your *phone number*?\n"
        "Include country code before phone number.\n" 
        "Example: *+1-800-555-0199* or *+44 7911 123456*",
        parse_mode='Markdown'
    )

async def handle_phone(update, context, lead, text):
    if not validate_phone(text):
        await update.message.reply_text(
            "❌ Please enter a valid phone number.\n"
            "Example: *+1-800-555-0199* or *+44 7911 123456*",
            parse_mode='Markdown'
        )
        return
    
    lead['phone'] = text
    lead['state'] = WAITING_SERVICE

    logger.info(f"Phone number collected: {text}")

    await update.message.reply_text(
        "Perfect! 📱\n\n"
        "What service are you interested in?\n"
        "Please choose from options below:",
        reply_markup=get_service_keyboard()
    )

async def handle_requirement(update, context, lead, text):
    user_id = update.effective_user.id

    # check length
    if len(text) > Config.MAX_REQUIREMENT_LENGTH:
        await update.message.reply_text(
            f"❌ Please keep your requirement under"
            f"{Config.MAX_REQUIREMENT_LENGTH} characters.\n"
            f"Current length: {len(text)}"
        )
        return
    if len(text) < 10:
        await update.message.reply_text(
            "❌ Please describe your requirement in at least 10 characters."
        )
        return
    
    lead['requirement'] = text
    lead['state'] = DONE

    # Save to database
    success = save_lead(
        telegram_id=user_id,
        name=lead["name"],
        email=lead["email"],
        phone=lead["phone"],
        service=lead["service"],
        requirement=text
        )
    
    if success:
        logger.info(f"Lead saved successfully for user {user_id}")
        await update.message.reply_text(
            f"✅ *Thank you, {lead['name']}!*\n\n"
            f"We've received your request for *{lead['service']}*"
            f"*{Config.FOLLOWUP_HOURS} hours*.🙌\n\n"
            "Type /start to submit another request.",
            parse_mode='Markdown'
        )

        # Notify admin about new lead
        await notify_admin(context, lead, user_id)

    else:
        await update.message.reply_text(
            "⚠️ Somethimg went wrong saving your details.\n"
            "Please try again with /start"
        )

# ──── Button handler ────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # If it's an admin button, ignore it here
    # It will be handled in admin button handler
    if query.data.startswith("admin_"):
        return

    lead = get_user_data(context)

    # Handle service selection
    if query.data.startswith("svc_"):
        if lead['state'] != WAITING_SERVICE:
            await query.answer("Please follow the steps from /start")
            return
        
        # Get service name using index from config
        index = int(query.data.replace("svc_", ""))
        service = Config.SERVICES[index]
        
        lead["service"] = service
        lead["state"] = WAITING_REQUIREMENT

        logger.info(f"Service selected: {service}")

        await query.edit_message_text(
            f"Great choice! You selected *{service}* 👍\n\n"
            "Please *briefly describe* your requirement. \n"
            "The more details you give, the better we can help:",
            parse_mode='Markdown'
        )

# ──── Admin notification ────────────────────────────────────
async def notify_admin(context, lead: dict, user_id: int):
    """Sends instant notification to admin when new lead arrives"""
    try:
        message = (
            f"🔔 *New Lead Received!*\n\n"
            f"👤 Name: {lead['name']}\n"
            f"📧 Email: {lead['email']}\n"
            f"📱 Phone: {lead['phone']}\n"
            f"🛠 Service: {lead['service']}\n"
            f"📝 Requirement: {lead['requirement']}\n"
            f"🆔 Telegram ID: `{user_id}`"
        )

        await context.bot.send_message(
            chat_id=Config.ADMIN_ID,
            text=message,
            parse_mode="Markdown"
        )

        logger.info(f"Admin notified about new lead: {lead['name']}")
        
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")

