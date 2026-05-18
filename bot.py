import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, ConversationHandler

BOT_TOKEN = "8793133754:AAHqPVATWUjmHxeTqdSqbEPlXpfwbjbLRYE"
ADMIN_ID = 7052125734

PHOTO, NAME, PHONE, ADDRESS = range(4)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Assalomu alaykum! Kosmetika do'konimizga xush kelibsiz! 💄\n\n"
        "📦 Buyurtma berish uchun kanaldan mahsulot rasmini yuboring:"
    )
    return PHOTO


async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data["photo_id"] = update.message.photo[-1].file_id
        await update.message.reply_text("✅ Rasm qabul qilindi!\n\n📝 Mahsulot nomini yozing:")
        return NAME
    await update.message.reply_text("❌ Iltimos, mahsulot rasmini yuboring!")
    return PHOTO


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["product_name"] = update.message.text
    await update.message.reply_text("📱 Telefon raqamingizni yozing:")
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("📍 Manzilingizni yozing (viloyat, tuman, ko'cha):")
    return ADDRESS


async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    user = update.message.from_user

    product_name = context.user_data["product_name"]
    phone = context.user_data["phone"]
    address = context.user_data["address"]
    photo_id = context.user_data["photo_id"]

    await update.message.reply_text(
        f"✅ Buyurtmangiz qabul qilindi!\n\n"
        f"📦 Mahsulot: {product_name}\n"
        f"📱 Telefon: {phone}\n"
        f"📍 Manzil: {address}\n\n"
        f"⏳ Tez orada siz bilan bog'lanamiz!"
    )

    caption = (
        f"🛒 YANGI BUYURTMA!\n\n"
        f"👤 Mijoz: {user.full_name}\n"
        f"🆔 ID: {user.id}\n"
        f"📦 Mahsulot: {product_name}\n"
        f"📱 Telefon: {phone}\n"
        f"📍 Manzil: {address}"
    )

    keyboard = [[InlineKeyboardButton("📦 Yuborilmoqda deb belgilash", callback_data=f"sent_{user.id}")]]

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo_id,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    context.user_data.clear()
    return ConversationHandler.END


async def mark_sent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    customer_id = int(query.data.split("_")[1])

    try:
        await context.bot.send_message(
            chat_id=customer_id,
            text="🚀 Mahsulotingiz yuborilmoqda!\n\n📦 Buyurtmangiz yo'lda. Yaqin orada yetib boradi.\n📞 Savollar bo'lsa bizga yozing!"
        )
        await query.edit_message_caption(
            caption=query.message.caption + "\n\n✅ YUBORILDI!",
            reply_markup=None
        )
    except Exception as e:
        logger.error(f"Xato: {e}")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi. Qayta boshlash: /start")
    context.user_data.clear()
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHOTO: [MessageHandler(filters.ALL, get_photo)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv)
    application.add_handler(CallbackQueryHandler(mark_sent, pattern="^sent_"))

    logger.info("Bot ishga tushdi!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()