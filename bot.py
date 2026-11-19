import logging
import os
import random

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# --- تنظیمات اصلی (از بخش Variables در Railway خوانده می‌شود) ---
TOKEN = os.environ.get("BOT_TOKEN")
_admin_env = os.environ.get("ADMIN_ID", "").strip()
ADMIN_ID = int(_admin_env) if _admin_env.isdigit() else None

POEMS = [
    "«راز دل با کس مگو، جز با حریمِ این سکوت...\nهر چه در سینه نهان داری، به دستِ باد سپار.»\n\nپیامت را نگارنده باش (متن، عکس، ویس یا آوا):",
    "«در این سراچه بی‌پایان، هیچ ردپایی از تو نمی‌ماند؛\nحرف‌هایت را بی‌پروا بر سنگِ این خلوت حک کن.»\n\nهر چه در دل داری، به قلم آور:",
    "«از خویش بگو و هر چه از غبارِ روزگار بر دل نشسته...\nاینجا آواژ، محرمِ رازِ بی‌نامِ توست.»\n\nنوشته یا پیام خود را بفرست:",
    "«پنهان مکن ز ما، که سخن را بهانه‌ایست...\nبی‌نام و نشان، حکایتِ دل را به ما رسان.»\n\nپیامت را بفرست، که شنواست گوشِ این خلوت:",
]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_ID
    user_id = update.effective_user.id
    newly_claimed = False

    # اگر ADMIN_ID تنظیم نشده باشد، اولین کسی که /start بزند مدیر می‌شود
    if ADMIN_ID is None:
        ADMIN_ID = user_id
        newly_claimed = True
        logger.info("Admin claimed by user id %s", user_id)

    if user_id == ADMIN_ID:
        bot_username = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start=anon"
        text = (
            "سلام مدیر عزیز! 👋\n\n"
            f"لینک اختصاصی پیام ناشناس آواژ:\n{link}\n\n"
            "پیام‌ها بدون هیچ مشخصاتی از فرستنده برایتان می‌آید. "
            "برای پاسخ دادن، روی همان پیام ریپلای کنید."
        )
        if newly_claimed:
            text += (
                f"\n\n🔐 شناسه شما: {user_id}\n"
                "برای اینکه بعد از ری‌استارت ربات کس دیگری مدیر نشود، "
                "در Railway بخش Variables متغیری به نام ADMIN_ID بسازید "
                "و این عدد را در آن بگذارید."
            )
        await update.message.reply_text(text)
    else:
        await update.message.reply_text(random.choice(POEMS))


async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = update.effective_user.id
    message = update.message

    # --- پیام از طرف مدیر: پاسخ به یک فرستنده ---
    if sender_id == ADMIN_ID:
        if message.reply_to_message:
            replied_msg_id = message.reply_to_message.message_id
            target_user_id = context.bot_data.get(replied_msg_id)

            if target_user_id:
                try:
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text="📩 پاسخی از سوی خلوتِ آواژ رسید:",
                    )
                    await context.bot.copy_message(
                        chat_id=target_user_id,
                        from_chat_id=message.chat_id,
                        message_id=message.message_id,
                    )
                    await message.reply_text("✅ پاسخ با موفقیت ابلاغ شد.")
                except Exception:
                    await message.reply_text(
                        "❌ خطا در ارسال پاسخ (شاید مخاطب ربات را مسدود کرده است)."
                    )
            else:
                await message.reply_text(
                    "⚠️ ردپایی از فرستنده این پیام در حافظه یافت نشد "
                    "(بعد از ری‌استارت ربات، پیام‌های قدیمی قابل پاسخ نیستند)."
                )
        else:
            await message.reply_text("💡 برای پاسخ‌دهی، حتماً روی پیام مورد نظر ریپلای کنید.")
        return

    # --- پیام از طرف یک کاربر عادی: ارسال ناشناس برای مدیر ---
    if ADMIN_ID is None:
        await message.reply_text("⏳ ربات هنوز آماده نیست. کمی بعد دوباره تلاش کن.")
        return

    try:
        copied = await context.bot.copy_message(
            chat_id=ADMIN_ID,
            from_chat_id=message.chat_id,
            message_id=message.message_id,
        )
        context.bot_data[copied.message_id] = sender_id

        await message.reply_text(
            "✅ نجوا و پیام تو به مقصد رسید. باز هم سخنی بود، همین‌جا بازگو کن."
        )
    except Exception:
        logger.exception("Failed to forward message")
        await message.reply_text("❌ خطایی در ارسال رخ داد. لختی دیگر تلاش کن.")


def main():
    if not TOKEN:
        raise SystemExit("متغیر BOT_TOKEN تنظیم نشده است (Railway > Variables).")

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start, filters=filters.ChatType.PRIVATE))
    application.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & filters.ALL & ~filters.COMMAND, handle_messages
        )
    )
    print("ربات آواژ با وقار تمام روشن شد...")
    application.run_polling()


if __name__ == "__main__":
    main()
