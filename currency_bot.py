import os
import requests
import logging
from dotenv import load_dotenv
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
SECRET_TOKEN = os.getenv('SECRET_TOKEN')

print("API_TOKEN:", API_TOKEN)
print("WEBHOOK_URL:", WEBHOOK_URL)
print("SECRET_TOKEN:", SECRET_TOKEN)

if not all([API_TOKEN, WEBHOOK_URL]):
    logger.error("Missing required environment variables")
    exit(1)

# Currency data
CURRENCIES = {
    'USD': '🇺🇸 US Dollar',
    'EUR': '🇪🇺 Euro',
    'GBP': '🇬🇧 British Pound',
    'GHS': '🇬🇭 Ghanaian Cedi',
    'CAD': '🇨🇦 Canadian Dollar',
    'AUD': '🇦🇺 Australian Dollar'
}

# Keyboard configurations
def get_currency_keyboard():
    """Create reply keyboard for currency selection"""
    buttons = [
        [KeyboardButton(f"{CURRENCIES['USD']}"), KeyboardButton(f"{CURRENCIES['EUR']}")],
        [KeyboardButton(f"{CURRENCIES['GBP']}"), KeyboardButton(f"{CURRENCIES['GHS']}")],
        [KeyboardButton(f"{CURRENCIES['CAD']}"), KeyboardButton(f"{CURRENCIES['AUD']}")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)

RESTART_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("✅ Yes, restart", callback_data="yes")],
    [InlineKeyboardButton("❌ No, exit", callback_data="no")]
])

START_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🚀 Start Conversion", callback_data="start_conversion")],
    [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
])

HELP_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("📚 See Supported Currencies", callback_data="show_currencies")],
    [InlineKeyboardButton("🔄 Start Conversion", callback_data="start_conversion")],
    [InlineKeyboardButton("🔙 Back to Start", callback_data="back_to_start")]
])

SUPPORT_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔄 Start Conversion", callback_data="start_conversion")],
    [InlineKeyboardButton("🔙 Back to Start", callback_data="back_to_start")]
])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with interactive buttons"""
    context.user_data.clear()
    message = "💰 *Welcome to Currency Converter Bot*\nWhat would you like to do?"
    
    if update.message:
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=START_KEYBOARD
        )
    else:
        await update.callback_query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=START_KEYBOARD
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help menu with buttons"""
    message = (
        "🛠 *Help Center*\n\n"
        "This bot converts between different currencies using real-time exchange rates.\n\n"
        "🔹 *How to Use*\n"
        "1. Select source currency\n"
        "2. Choose target currency\n"
        "3. Enter the amount\n"
        "4. Get your conversion result\n\n"
        "You can restart the process anytime."
    )
    
    if update.message:
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=HELP_KEYBOARD
        )
    else:
        await update.callback_query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=HELP_KEYBOARD
        )

async def show_currencies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display supported currencies"""
    currencies_list = "\n".join([f"- {name} ({code})" for code, name in CURRENCIES.items()])
    message = (
        f"🌍 *Supported Currencies*\n\n{currencies_list}\n\n"
        "Select from the keyboard when converting."
    )
    
    await update.callback_query.edit_message_text(
        message,
        parse_mode='Markdown',
        reply_markup=SUPPORT_KEYBOARD
    )

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text inputs through conversation steps"""
    step = context.user_data.get('step')
    text = update.message.text.strip()
    
    if step == 'source_currency':
        # Match the full currency name to get the code
        for code, name in CURRENCIES.items():
            if name in text:
                context.user_data['source'] = code
                context.user_data['step'] = 'target_currency'
                await update.message.reply_text(
                    "Now select target currency:",
                    reply_markup=get_currency_keyboard()
                )
                return
        
        await update.message.reply_text(
            "⚠️ Please select a currency from the keyboard",
            reply_markup=get_currency_keyboard()
        )
        
    elif step == 'target_currency':
        for code, name in CURRENCIES.items():
            if name in text:
                context.user_data['target'] = code
                context.user_data['step'] = 'amount'
                await update.message.reply_text(
                    "💵 Enter amount to convert:",
                    reply_markup=None
                )
                return
        
        await update.message.reply_text(
            "⚠️ Please select a currency from the keyboard",
            reply_markup=get_currency_keyboard()
        )
        
    elif step == 'amount':
        try:
            amount = float(text)
            if amount <= 0:
                await update.message.reply_text("❌ Amount must be greater than 0")
                return
            await convert_currency(update, context, amount)
        except ValueError:
            await update.message.reply_text(
                "❌ Please enter a valid number (e.g., 100 or 50.5)\n"
                "Don't include currency symbols."
            )

async def convert_currency(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: float):
    """Perform currency conversion and show result"""
    source = context.user_data['source']
    target = context.user_data['target']
    
    try:
        await update.message.reply_text("⏳ Fetching exchange rates...")
        response = requests.get(f'https://api.exchangerate-api.com/v4/latest/{source}')
        response.raise_for_status()
        data = response.json()
        rate = data['rates'][target]
        result = amount * rate
        
        await update.message.reply_text(
            f"🔀 *Conversion Result*\n"
            f"`{amount:,.2f} {CURRENCIES[source]} = {result:,.2f} {CURRENCIES[target]}`\n\n"
            f"📊 Exchange Rate:\n"
            f"`1 {source} = {rate:.4f} {target}`",
            parse_mode='Markdown',
        )
        await update.message.reply_text(
            "🔄 Convert another amount?",
            reply_markup=RESTART_KEYBOARD
        )
        context.user_data['step'] = 'confirm_restart'
        
    except requests.RequestException as e:
        logger.error(f"API Error: {e}")
        await update.message.reply_text(
            "⚠️ Failed to get exchange rates. Please try again later.\n"
            "You can /start a new conversion."
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all inline button presses"""
    query = update.callback_query
    await query.answer()

    if query.data == "start_conversion":
        context.user_data.clear()
        context.user_data['step'] = 'source_currency'
        await query.edit_message_text(
            "🔹 *Step 1/3*\nSelect source currency:",
            parse_mode='Markdown'
        )
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Choose from the keyboard below:",
            reply_markup=get_currency_keyboard()
        )

    elif query.data == "help":
        await help_command(update, context)

    elif query.data == "show_currencies":
        await show_currencies(update, context)

    elif query.data == "back_to_start":
        await start(update, context)

    elif query.data == "yes":  # Restart confirmation
        context.user_data.clear()
        context.user_data['step'] = 'source_currency'
        await query.edit_message_text("🔄 Starting new conversion...")
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="🔹 *Step 1/3*\nSelect source currency:",
            parse_mode='Markdown',
            reply_markup=get_currency_keyboard()
        )

    elif query.data == "no":  # Exit confirmation
        await query.edit_message_text(
            "✨ Thank you for using the bot!\n"
            "Click below to begin again.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Start New Conversion", callback_data="start_conversion")]
            ])
        )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log the error and send a message to the user if possible."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    # Try to notify the user
    try:
        if update and hasattr(update, 'message') and update.message:
            await update.message.reply_text("⚠️ An unexpected error occurred. Please try again later.")
        elif update and hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text("⚠️ An unexpected error occurred. Please try again later.")
    except Exception as e:
        logger.error(f"Failed to send error message to user: {e}")

# Application setup
def setup_application():
    """Set up the Telegram application with handlers"""
    application = Application.builder().token(API_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    application.add_handler(CallbackQueryHandler(handle_callback))
    # Register error handler
    application.add_error_handler(error_handler)
    
    return application

async def set_webhook(application):
    """Configure webhook for an existing application"""
    await application.bot.set_webhook(
        url=f"{WEBHOOK_URL}/api/webhook",
        secret_token=SECRET_TOKEN
    )

# Initialize single application instance
app = setup_application()

# To set webhook (run once after deployment):
# import asyncio; asyncio.run(set_webhook(app))