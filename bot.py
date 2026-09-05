import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from config import BOT_TOKEN
from core.aggregator import search_channels

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Selamat datang di Bot IPTV!\n\n"
        "Ketik nama channel TV yang ingin kamu cari (contoh: Vidio, Indosiar, SCTV, RCTI, HBO)."
    )

async def handle_channel_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    if not query:
        return

    status_msg = await update.message.reply_text(
        f"🔍 Mencari stream untuk: <b>{query}</b>...", 
        parse_mode="HTML"
    )

    results = await search_channels(query)

    if not results:
        await status_msg.edit_text(
            f"❌ Channel <b>{query}</b> tidak ditemukan.", 
            parse_mode="HTML"
        )
        return

    response = f"📺 <b>Hasil pencarian untuk '{query}':</b>\n\n"
    for item in results[:5]:  # Mengambil 5 hasil teratas
        name = item.get("name", "Unknown")
        url = item.get("url", "")
        source = item.get("source", "IPTV")
        response += f"🔹 <b>{name}</b> (<i>{source}</i>)\n🔗 <code>{url}</code>\n\n"

    await status_msg.edit_text(
        response, 
        parse_mode="HTML", 
        disable_web_page_preview=True
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_channel_search))

    print("Bot IPTV berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
