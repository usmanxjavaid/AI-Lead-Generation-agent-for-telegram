from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from core.logger import logger
from core.database import init_db
from config import Config
import handlers.user as user
import handlers.admin as admin

def main():
    # Initialize database first
    init_db()

    # Build the bot application
    app = Application.builder().token(Config.TELEGRAM_TOKEN).build()

    # ---User handlers---
    app.add_handler(CommandHandler("start", user.start))
    app.add_handler(CallbackQueryHandler(admin.admin_button_handler, pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(user.button_handler, pattern="^svc_"))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        user.handle_message
    ))

    # ---Admin handlers---
    app.add_handler(CommandHandler("admin", admin.admin))
    app.add_handler(CommandHandler("leads", admin.leads))
    app.add_handler(CommandHandler("export", admin.export))
    app.add_handler(CommandHandler("status", admin.status))
    app.add_handler(CommandHandler("broadcast", admin.broadcast))
    async def error_handler(update, context):
        logger.error(f"Error: {context.error}")

    app.add_error_handler(error_handler)
    logger.info(f"{Config.AGENT_NAME} is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
