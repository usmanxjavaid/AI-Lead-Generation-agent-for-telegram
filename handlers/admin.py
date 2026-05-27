import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.logger import logger
from core.database import (
    get_all_leads,
    get_stats,
    update_lead_status,
    export_leads_csv
)
from config import Config

# ── Helper: check if user is admin ───────────────────────
def is_admin(update: Update) -> bool:
    return update.effective_user.id == Config.ADMIN_ID

# ── /admin command ────────────────────────────────────────
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Access denied.")
        return
    
    total, new, contacted, converted = get_stats()
    keyboard = [
        [InlineKeyboardButton("📋 View Leads", callback_data="admin_leads")],
        [InlineKeyboardButton("📤 Export CSV", callback_data="admin_export")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔄 Update Status", callback_data="admin_status")],
    ]

    await update.message.reply_text(
        f"*📊 Admin Panel — {Config.COMPANY_NAME}*\n\n"
        f"📋 Total Leads: {total}\n"
        f"🔵 New: {new}\n"
        f"🟡 Contacted: {contacted}\n"
        f"🟢 Converted: {converted}\n",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ── /leads command ────────────────────────────────────────
async def leads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Access denied.")
        return
    
    all_leads = get_all_leads()

    if not all_leads:
        await update.message.reply_text("No leads yet.")
        return
    
    # show last 10 leads only to avoid huge messages
    msg = f"📋 *All Leads*\n"
    for lead in all_leads[:10]:
        msg += (
            f"🔹 *{lead['name']}*\n"
            f" 📧{lead['email']}\n"
            f" 📱{lead['phone']}\n"
            f" 🛠{lead['service']}"
            f" 📌Status: {lead['status']}\n"
            f" 🆔ID: `{lead['telegram_id']}`\n\n" 
        )
    await update.message.reply_text(msg, parse_mode="Markdown")

# ── /export command ───────────────────────────────────────
async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Access denied.")
        return

    await update.message.reply_text("⏳ Generating CSV file...") 

    filename = export_leads_csv()

    # Send the CSV file directly to telegram
    with open(filename, 'rb') as f:
        await update.message.reply_document(
            document=f,
            filename=os.path.basename(filename),
            caption="✅ Here are all your leads!"
        )

    logger.info(f"Leads exported by admin")

# ── /status command ───────────────────────────────────────
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Usage: /status 123456789 contacted
    Updates lead status: new contacted converted
    """
    if not is_admin(update):
        await update.message.reply_text("⛔ Access denied.")
        return

    # context.argd contains words after command
    # e.g., /status 12345 contacted → args would be ['12345', 'contacted']
    if len(context.args) != 2:
        await update.message.reply_text(
            "Usage: `/status [telegram_id] [status]`\n\n"
            "status options: `new` `contacted` `converted`",
            parse_mode='Markdown'
        )
        return
    
    valid_statuses = ['new', 'contacted', 'converted']

    telegram_id = context.args[0]
    new_status = context.args[1].lower()

    if new_status not in valid_statuses:
        await update.message.reply_text(
            f"❌ Invalid status.\n"
            f"Choose from `new` `contacted` `converted`",
             parse_mode='Markdown'
        )
        return
    
    success = update_lead_status(int(telegram_id), new_status)

    if success:
        await update.message.reply_text(
            f"✅ Lead `{telegram_id}` updated to *{new_status}*",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ Failed to update. Check ID.")

# ── /broadcast command ────────────────────────────────────
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Usage: /broadcast Hello Everyone! we have a new offer.
    Sends message to All leads who submitted their details.
    """
    if not is_admin(update):
        await update.message.reply_text('⛔ Access denied.')
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: `/broadcast your message here`",
            parse_mode='Markdown'
        )
        return
    
    # Join all words after /broadcast into one message
    message = " ".join(context.args)
    all_leads = get_all_leads()

    if not all_leads:
        await update.message.reply_text('No leads to broadcast to.')
        return
    
    sent=0
    failed=0

    await update.message.reply_text(
        f"📤 Sending to {len(all_leads)} leads..."
    )

    for lead in all_leads:
        try:
            await context.bot.send_message(
                chat_id = lead['telegram_id'],
                text=f"*📢 Message from {Config.COMPANY_NAME}:*\n\n{message}",
                parse_mode='Markdown'
            )
            sent += 1
        except Exception as e:
            # User may have blocked the bot
            logger.warning(f"Broadcast failed for {lead['telegram_id']}: {e}")
            failed += 1

    await update.message.reply_text(
        f"✅ Broadcast complete!\n\n"
        f"📤 Sent: {sent}\n"
        f"❌ Failed: {failed}"
        )
    logger.info(f"Broadcast sent: {sent} success, {failed} failed")

        
# ── Admin Button Handler ────────────────────────────────────
async def admin_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(update):
        await query.edit_message_text("⛔ Access denied.")
        return

    if query.data == "admin_leads":
        all_leads = get_all_leads()

        if not all_leads:
            await query.edit_message_text("No leads yet.")
            return

        msg = "📋 *All Leads*\n\n"
        for lead in all_leads[:10]:
            msg += (
                f"🔹 *{lead['name']}*\n"
                f"  📧 {lead['email']}\n"
                f"  📱 {lead['phone']}\n"
                f"  🛠 {lead['service']}\n"
                f"  📌 Status: {lead['status']}\n"
                f"  🆔 ID: `{lead['telegram_id']}`\n\n"
            )
        await query.edit_message_text(msg, parse_mode="Markdown")

    elif query.data == "admin_export":
        filename = export_leads_csv()
        with open(filename, 'rb') as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                caption="✅ Here are all your leads!"
            )

    elif query.data == "admin_broadcast":
        await query.edit_message_text(
            "📢 To broadcast a message use:\n\n"
            "`/broadcast your message here`",
            parse_mode="Markdown"
        )

    elif query.data == "admin_status":
        await query.edit_message_text(
            "🔄 To update a lead status use:\n\n"
            "`/status [telegram_id] [status]`\n\n"
            "Status options: `new` `contacted` `converted`",
            parse_mode="Markdown"
        )