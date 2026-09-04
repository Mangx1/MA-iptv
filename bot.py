import os
import sys

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.aggregator import grouped_search
from config import BOT_TOKEN, ALLOWED_CHAT_ID


def allowed(update):
    if not ALLOWED_CHAT_ID:
        return True

    return str(update.effective_chat.id) == str(ALLOWED_CHAT_ID)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return

    await update.message.reply_text(
        "📺 MA-IPTV Bot\n\n"
        "Cari channel dengan:\n"
        "/live BBC News\n"
        "/live CNN\n"
        "/live sports\n\n"
        "Bot akan mencari stream publik yang tersedia."
    )


async def live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return

    query = " ".join(context.args).strip()

    if not query:
        await update.message.reply_text(
            "Contoh:\n/live BBC News"
        )
        return

    msg = await update.message.reply_text(
        f"🔎 Mencari: {query}..."
    )

    try:
        groups = grouped_search(query)

        if not groups:
            await msg.edit_text(
                f"❌ Tidak ditemukan:\n{query}"
            )
            return

        lines = [
            f"📺 HASIL: {query}\n"
        ]

        buttons = []

        shown = 0

        for group in groups:
            streams = group.get("streams", [])

            if not streams:
                continue

            lines.append(
                f"\n📡 {group['name']}"
            )

            for stream in streams[:3]:
                url = stream.get("url")

                if not url:
                    continue

                quality = stream.get("quality") or "?"
                source = stream.get("source") or "?"
                status = stream.get("status") or "unknown"

                lines.append(
                    f"  • {quality} | {source} | {status}"
                )

                buttons.append([
                    InlineKeyboardButton(
                        f"▶️ {group['name']} {quality}",
                        url=url
                    )
                ])

                shown += 1

                if shown >= 12:
                    break

            if shown >= 12:
                break

        if shown == 0:
            await msg.edit_text(
                "❌ Tidak ada stream yang bisa ditampilkan."
            )
            return

        keyboard = InlineKeyboardMarkup(buttons)

        await msg.edit_text(
            "\n".join(lines),
            reply_markup=keyboard,
            disable_web_page_preview=True
        )

    except Exception as e:
        print("BOT ERROR:", repr(e))

        await msg.edit_text(
            f"❌ Error saat mencari.\n\n{type(e).__name__}: {e}"
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("live", live)
    )

    print("MA-IPTV BOT AKTIF")
    print("Ketik /live BBC News di Telegram")

    app.run_polling()


if __name__ == "__main__":
    main()
