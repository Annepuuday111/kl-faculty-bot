import logging
import pandas as pd
from PIL import Image
from io import BytesIO
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8096176082:AAHCOopkSJbdLXkS837xNWPHJTKolxfu3x8"
faculty_df = pd.read_csv("faculty_data.csv")

def resize_logo(path="logo.png", size=(150, 100)):
    img = Image.open(path)
    img = img.resize(size, Image.ANTIALIAS)
    byte_io = BytesIO()
    img.save(byte_io, format="PNG")
    byte_io.seek(0)
    return byte_io

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

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

