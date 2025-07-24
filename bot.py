import os
import pandas as pd
from PIL import Image
from io import BytesIO
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Environment Variables
TOKEN = os.getenv("BOT_TOKEN", "8096176082:AAHCOopkSJbdLXkS837xNWPHJTKolxfu3x8")
URL = os.getenv("WEBHOOK_URL", "https://kl-faculty-bot.onrender.com")

# Load Faculty Data
faculty_df = pd.read_csv("faculty_data.csv")

# Flask App
app = Flask(__name__)

# Telegram Bot and Application
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# Resize logo for consistency
def resize_logo(path="logo.png", size=(150, 100)):
    img = Image.open(path)
    img = img.resize(size)
    byte_io = BytesIO()
    img.save(byte_io, format="PNG")
    byte_io.seek(0)
    return byte_io

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open("logo.png", "rb"),
        caption=(
            "👋 *Welcome to KL Faculty Finder Bot!*\n\n"
            "🔎 Search by:\n"
            "👤 Name (e.g., `Sarvani`)\n"
            "🆔 Emp No (e.g., `210354`)\n"
            "🏢 Department (e.g., `Data Science`)\n\n"
            "📨 Just type and send your query!"
        ),
        parse_mode="Markdown"
    )

# Message handler for queries
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

# Add Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Webhook endpoint for Telegram
@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update_data = request.get_json(force=True)
    update = Update.de_json(update_data, bot)
    await application.process_update(update)
    return "ok"

# Health check
@app.route("/")
def index():
    return "KL Faculty Bot is running!"

# Start the app
if __name__ == "__main__":
    import asyncio

    async def main():
        # Set webhook
        await application.initialize()
        await bot.set_webhook(f"{URL}/{TOKEN}")
        print("Webhook set!")
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

    asyncio.run(main())

