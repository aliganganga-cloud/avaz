import logging
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- تنظیمات اصلی ---
TOKEN = "9184914203:AAF2PerYE2SeHFhAnceMLZN15nGsmj6qv-s"
ADMIN_ID = None  # اولین کسی که /start بزند مدیر می‌شود

POEMS = [
    "«راز دل با کس مگو، جز با حریمِ این سکوت...\nهر چه در سینه نهان داری، به دستِ باد سپار.»\n\nپیامت را نگارنده باش (متن، عکس، ویس یا آوا):",
    "«در این سراچه بی‌پایان، هیچ ردپایی از تو نمی‌ماند؛\nحرف‌هایت را بی‌پروا بر سنگِ این خلوت حک کن.»\n\nهر چه در دل داری، به قلم آور:",
    "«از خویش بگو و هر چه از غبارِ روزگار بر دل نشسته...\nاینجا آواژ، محرمِ رازِ بی‌نامِ توست.»\n\nنوشته یا پیام خود را بفرست:",
    "«پنهان مکن ز ما، که سخن را بهانه‌ایست...
بی‌نام و نشان، حکایتِ دل را به ما رسان.»\n\nپیامت را بفرست، که شنواست گوشِ این خلوت:"
]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_ID
    user_id = update.effective_user.id
    
    if ADMIN_ID is None:
        ADMIN_ID = user_id

    if user_id == ADMIN_ID:
        bot_username = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start=anon"
        await update.message.reply_text(
            f"سلام مدیر عزیز! 👋\n\n"
            f"لینک اختصاصی پیام ناشناس آواژ:\n{link}\n\n"
            f"پیام‌های دریافتی همراه با مشخصات کامل فرستنده برایتان ارسال خواهد شد."
        )
    else:
        welcome_poem = random.choice(POEMS)
        await update.message.reply_text(welcome_poem)

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user
    sender_id = sender.id
    message = update.message

    if sender_id == ADMIN_ID:
        if message.reply_to_message:
            replied_msg_id = message.reply_to_message.message_id
            target_user_id = context.bot_data.get(replied_msg_id)
            
            if target_user_id:
                try:
                    await context.bot.send_message(chat_id=target_user_id, text="📩 پاسخی از سوی خلوتِ آواژ رسید:")
                    await message.copy(chat_id=target_user_id)
                    await message.reply_text("✅ پاسخ با موفقیت ابلاغ شد.")
                except Exception:
                    await message.reply_text("❌ خطا در ارسال پاسخ (شاید مخاطب ربات را مسدود کرده است).")
            else:
                await message.reply_text("⚠️ ردپایی از فرستنده این پیام در حافظه یافت نشد.")
        else:
            await message.reply_text("💡 برای پاسخ‌دهی، حتماً روی پیام مورد نظر ریپلای کنید.")
        return

    try:
        username_str = f"@{sender.username}" if sender.username else "ندارد"
        name_str = sender.first_name if sender.first_name else "ناشناس"
        
        info_text = (
            f"📬 **نجوایی تازه در آواژ:**\n"
            f"👤 نام: {name_str}\n"
            f"🆔 یوزرنیم: {username_str}\n"
            f"🔢 شناسه: `{sender_id}`\n"
            f"-------------------"
        )
        
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=info_text,
            parse_mode="Markdown"
        )
        
        forwarded_msg = await message.copy(chat_id=ADMIN_ID)
        context.bot_data[forwarded_msg.message_id] = sender_id
        
        await message.reply_text("✅ نجوا و پیام تو به مقصد رسید. باز هم سخنی بود، همین‌جا بازگو کن.")
    except Exception:
        await message.reply_text("❌ خطایی در ارسال رخ داد. لختی دیگر تلاش کن.")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_messages))
    print("ربات آواژ با وقار تمام روشن شد...")
    application.run_polling()

if __name__ == "__main__":
    main()
