import logging
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- تنظیمات اصلی ---
TOKEN = "9184914203:AAF2PerYE2SeHFhAnceMLZN15nGsmj6qv-s"
ADMIN_ID = None  # اولین نفری که /start بزند، به عنوان مدیر ثبت می‌شود

# اشعار کوتاه، کاریزماتیک و ادبی برای استقبال از مخاطب
POEMS = [
    "🕯️ «رازِ دل با کس مگو، جز با حریمِ این سکوت...\nهر چه در سینه نهان داری، به دستِ باد سپار.»\n\n🖋️ پیامت را نگارنده باش (متن، عکس، ویس یا آوا):",
    "🌑 «در این سراچه‌ی خاموش، هیچ ردپایی از تو نمی‌ماند؛\nحرف‌هایت را بی‌پروا بر سنگِ این خلوت حک کن.»\n\n🪶 هر چه در دل داری، به قلم آور:",
    "🖋️ «از خویش بگو و هر چه از غبارِ روزگار بر دل نشسته...\nاینجا آواژ، محرمِ رازِ بی‌نامِ توست.»\n\n✉️ نوشته یا پیام خود را بفرست:",
    "🪶 «پنهان مکن ز ما، که سخن را بهانه‌ایست...\nبی‌نام و نشان، حکایتِ دل را به ما رسان.»\n\n🎙️ پیامت را بفرست، که شنواست گوشِ این خلوت:",
    "🕯️ «گاهی یک حرفِ نگفته، سنگین‌تر از هزار سکوت است...\nآسوده بنویس؛ اینجا تنها صدای تو می‌ماند، بی‌هیچ نام و نشانی.»\n\n✉️ نجوای خود را ارسال کن:"
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
            f"درود بر مدیرِ آواژ 🕯️\n\n"
            f"🔗 لینک اختصاصی خلوتِ آواژ:\n{link}\n\n"
            f"تمامی پیام‌ها (متن، عکس، فیلم، ویس و آهنگ) همراه با مشخصات فرستنده برای شما ارسال می‌شوند. برای پاسخ‌دهی، کافیست روی پیام دریافتی Reply کنید."
        )
    else:
        welcome_poem = random.choice(POEMS)
        await update.message.reply_text(welcome_poem)

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user
    sender_id = sender.id
    message = update.message

    # حالت پاسخ‌دهی مدیر به پیام‌ها
    if sender_id == ADMIN_ID:
        if message.reply_to_message:
            replied_msg_id = message.reply_to_message.message_id
            target_user_id = context.bot_data.get(replied_msg_id)
            
            if target_user_id:
                try:
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text="🕯️ پاسخی از خلوتِ آواژ برایت رسید:"
                    )
                    await message.copy(chat_id=target_user_id)
                    await message.reply_text("✔️ پاسخ با موفقیت ابلاغ شد.")
                except Exception:
                    await message.reply_text("❌ ارسال پاسخ ممکن نشد (احتمالاً مخاطب ربات را مسدود کرده است).")
            else:
                await message.reply_text("⚠️ ردپایی از فرستنده‌ی این پیام در حافظه یافت نشد.")
        else:
            await message.reply_text("💡 برای پاسخ دادن، حتماً روی پیام مورد نظر Reply کنید.")
        return

    # حالت دریافت پیام از کاربر و ارسال به مدیر
    try:
        username_str = f"@{sender.username}" if sender.username else "ندارد"
        name_str = sender.first_name if sender.first_name else "ناشناس"
        
        info_text = (
            f"🕯️ **نجوایی تازه در آواژ:**\n"
            f"👤 نام: {name_str}\n"
            f"🆔 یوزرنیم: {username_str}\n"
            f"🔢 شناسه: `{sender_id}`\n"
            f"━━━━━━━━━━━━━━"
        )
        
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=info_text,
            parse_mode="Markdown"
        )
        
        forwarded_msg = await message.copy(chat_id=ADMIN_ID)
        context.bot_data[forwarded_msg.message_id] = sender_id
        
        await message.reply_text(
            "🪶 نجوای تو به مقصد رسید.\n"
            "اگر باز هم حرفی در سینه داری، این خلوت همچنان شنواست..."
        )
    except Exception:
        await message.reply_text("❌ خطایی در ارسال رخ داد. لختی دیگر دوباره تلاش کن.")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_messages))
    print("ربات آواژ با وقار تمام روشن شد...")
    application.run_polling()

if __name__ == "__main__":
    main()
