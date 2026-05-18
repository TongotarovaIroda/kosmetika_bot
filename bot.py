import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters, ConversationHandler
)

# === SOZLAMALAR ===
BOT_TOKEN = "8793133754:AAHqPVATWUjmHxeTqdSqbEPlXpfwbjbLRYE"
ADMIN_ID = 7052125734

# Holat bosqichlari
PHOTO, NAME, PHONE, ADDRESS = range(4)

logging.basicConfig(level=logging.INFO)

# === FOYDALANUVCHI BUYURTMA BOSHLAYDI ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Assalomu alaykum! Kosmetika do'konimizga xush kelibsiz! 💄\n\n"
        "📦 Buyurtma berish uchun kanaldan mahsulot rasmini yuboring:"
    )
    return PHOTO

# === RASM QABUL QILISH ===
async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data['photo_id'] = update.message.photo[-1].file_id
        await update.message.reply_text("✅ Rasm qabul qilindi!\n\n📝 Mahsulot nomini yozing:")
        return NAME
    else:
        await update.message.reply_text("❌ Iltimos, mahsulot rasmini yuboring!")
        return PHOTO

# === MAHSULOT NOMI ===
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['product_name'] = update.message.text
    await update.message.reply_text("📱 Telefon raqamingizni yozing (masalan: +998901234567):")
    return PHONE

# === TELEFON RAQAMI ===
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("📍 Manzilingizni yozing (viloyat, tuman, ko'cha):")
    return ADDRESS

# === MANZIL VA BUYURTMANI YAKUNLASH ===
async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['address'] = update.message.text
    user = update.message.from_user
    
    product_name = context.user_data['product_name']
    phone = context.user_data['phone']
    address = context.user_data['address']
    photo_id = context.user_data['photo_id']
    
    # Foydalanuvchiga tasdiqlash
    await update.message.reply_text(
        f"✅ Buyurtmangiz qabul qilindi!\n\n"
        f"📦 Mahsulot: {product_name}\n"
        f"📱 Telefon: {phone}\n"
        f"📍 Manzil: {address}\n\n"
        f"⏳ Tez orada siz bilan bog'lanamiz!"
    )
    
    # Adminга xabar yuborish
    caption = (
        f"🛒 YANGI BUYURTMA!\n\n"
        f"👤 Mijoz: {user.full_name}\n"
        f"🆔 Telegram ID: {user.id}\n"
        f"📦 Mahsulot: {product_name}\n"
        f"📱 Telefon: {phone}\n"
        f"📍 Manzil: {address}"
    )
    
    # Inline tugma — yuborilmoqda
    keyboard = [[InlineKeyboardButton("📦 Yuborilmoqda deb belgilash", callback_data=f"sent_{user.id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo_id,
        caption=caption,
        reply_markup=reply_markup
    )
    
    context.user_data.clear()
    return ConversationHandler.END

# === ADMIN TUGMASINI BOSADI ===
async def mark_sent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    customer_id = int(query.data.split("_")[1])
    
    # Mijozga xabar
    try:
        await context.bot.send_message(
            chat_id=customer_id,
            text=(
                "🚀 Xabar: Mahsulotingiz yuborilmoqda!\n\n"
                "📦 Buyurtmangiz yo'lda. Yaqin orada yetib boradi.\n"
                "📞 Savollar bo'lsa: bizga yozing!"
            )
        )
        await query.edit_message_caption(
            caption=query.message.caption + "\n\n✅ YUBORILDI — mijozga xabar ketdi!",
            reply_markup=None
        )
    except Exception as e:
        await query.edit_message_caption(
            caption=query.message.caption + f"\n\n❌ Xabar yuborishda xato: {e}",
            reply_markup=None
        )

# === BEKOR QILISH ===
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Buyurtma bekor qilindi. Qayta boshlash uchun /start yuboring.")
    context.user_data.clear()
    return ConversationHandler.END

# === BOTNI ISHGA TUSHIRISH ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHOTO: [MessageHandler(filters.ALL, get_photo)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(mark_sent, pattern="^sent_"))
    
    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()