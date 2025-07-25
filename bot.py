import logging
import os
import pandas as pd
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ✅ Load .env file
load_dotenv()

# ✅ Get bot token from environment
TOKEN = os.environ.get("BOT_TOKEN")

# ✅ Load faculty data
faculty_df = pd.read_csv("faculty_data.csv")

# ✅ Handle /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open("logo.png", "rb"),
        caption=(
            "👋 *Welcome to KL Faculty Finder Bot!*\n\n"
            "🔎 Search by:\n"
            "👤 Name (e.g., `Uday Kumar`)\n"
            "🆔 Emp No (e.g., `31007`)\n"
            "🏢 Department (e.g., `Computer Science`)\n\n"
            "📨 Just type and send your query!"
        ),
        parse_mode="Markdown"
    )

# ✅ Handle search messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower()
    matches = faculty_df[
        faculty_df.apply(lambda row:
            query in str(row['emp_no']).lower() or
            query in str(row['name']).lower() or
            query in str(row['department']).lower(), axis=1)
    ]

    if matches.empty:
        await update.message.reply_text("❌ No matching faculty found.")
    else:
        for _, row in matches.iterrows():
            response = (
                f"👤 *{row['name']}*\n"
                f"🆔 ID: {row['emp_no']}\n"
                f"🎓 Qualification: {row['qualification']}\n"
                f"🏷️ Designation: {row['designation']}\n"
                f"🏢 Department: {row['department']}\n"
                f"🌐 Campus: {row['campus']}"
            )
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=open("logo.png", "rb"),
                caption=response,
                parse_mode="Markdown"
            )

# ✅ Main entry point
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

