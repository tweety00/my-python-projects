from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import openpyxl
import os
from datetime import datetime

TOKEN = "8849290237:AAG6OFX3iDYBBvSyzHP8Zi4tsL285nIZyf8"
ADMIN_ID = 1550117523
PRICE_PER_NIGHT = 4500

def calculate_nights(checkin, checkout):
    try:
        d1 = datetime.strptime(checkin, "%d/%m/%Y")
        d2 = datetime.strptime(checkout, "%d/%m/%Y")
        return (d2 - d1).days
    except:
        return 0

def save_booking(data):
    file = "bookings.xlsx"
    if os.path.exists(file):
        wb = openpyxl.load_workbook(file)
        ws = wb.active
    else:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["الاسم", "اللقب", "الهاتف", "الرحلة", "الدخول", "الخروج", "الليالي", "كبار", "أطفال", "رضع", "السعر", "وقت الحجز"])
    ws.append([
        data["firstname"], data["lastname"], data["phone"],
        "منتجع الفردوس - بني حواء",
        data["checkin"], data["checkout"], data["nights"],
        data["adults"], data["children"], data["babies"],
        data["total"], datetime.now().strftime("%d/%m/%Y %H:%M")
    ])
    wb.save(file)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    keyboard = [
        [InlineKeyboardButton("🇩🇿 رحلات داخلية", callback_data="domestic")],
        [InlineKeyboardButton("✈️ رحلات خارجية", callback_data="international")],
    ]
    await update.message.reply_text(
        "🌍 مرحباً بكم في وكالة Be Tourist Travel!\n\n"
        "نقدم أفضل العروض السياحية 🇩🇿\n\n"
        "اختر نوع الرحلة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "domestic":
        keyboard = [
            [InlineKeyboardButton("🏖️ منتجع الفردوس - بني حواء", callback_data="trip_beni_hawa")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back")],
        ]
        await query.edit_message_text(
            "اختر وجهتك:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "international":
        await query.edit_message_text(
            "🔜 قريباً...",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back")]])
        )

    elif data == "trip_beni_hawa":
        text = (
            "🏖️ منتجع الفردوس - بني حواء\n\n"
            "🌊 المنتجع على بعد 100 متر من البحر\n"
            "🍽️ الإعاشة: نصف داخلي\n"
            "⏱️ أقل مدة: 7 أيام 6 ليالي\n\n"
            "🎁 الإضافات المجانية:\n"
            "🏊 بيسين مغلوقة\n"
            "🛁 جاكوزي\n"
            "🧖 صونا\n\n"
            "📅 من 12 جويلية إلى نهاية أوت 2026\n\n"
            "💰 الأسعار:\n"
            "👨 كبار +12: 4,500 دج/ليلة\n"
            "👦 أطفال 6-12: 2,250 دج/ليلة\n"
            "👶 أطفال -6: مجاناً 🎉"
        )
        keyboard = [
            [InlineKeyboardButton("🧮 احسب السعر", callback_data="calculate")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="domestic")],
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "calculate":
        context.user_data["trip"] = "beni_hawa"
        keyboard = [
            [InlineKeyboardButton("1️⃣", callback_data="adults_1"),
             InlineKeyboardButton("2️⃣", callback_data="adults_2"),
             InlineKeyboardButton("3️⃣", callback_data="adults_3"),
             InlineKeyboardButton("4️⃣", callback_data="adults_4")],
        ]
        await query.edit_message_text(
            "👨 كم عدد الكبار؟ (+12 سنة)",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("adults_"):
        adults = int(data.replace("adults_", ""))
        context.user_data["adults"] = adults
        keyboard = [
            [InlineKeyboardButton("0️⃣", callback_data="children_0"),
             InlineKeyboardButton("1️⃣", callback_data="children_1"),
             InlineKeyboardButton("2️⃣", callback_data="children_2"),
             InlineKeyboardButton("3️⃣", callback_data="children_3")],
        ]
        await query.edit_message_text(
            f"👨 الكبار: {adults}\n\n👦 كم عدد الأطفال؟ (6-12 سنة)",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("children_"):
        children = int(data.replace("children_", ""))
        context.user_data["children"] = children
        keyboard = [
            [InlineKeyboardButton("0️⃣", callback_data="babies_0"),
             InlineKeyboardButton("1️⃣", callback_data="babies_1"),
             InlineKeyboardButton("2️⃣", callback_data="babies_2"),
             InlineKeyboardButton("3️⃣", callback_data="babies_3")],
        ]
        await query.edit_message_text(
            f"👦 الأطفال 6-12: {children}\n\n👶 كم عدد الرضع؟ (-6 سنوات) مجاناً 🎉",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("babies_"):
        babies = int(data.replace("babies_", ""))
        context.user_data["babies"] = babies
        context.user_data["waiting"] = "checkin"
        await query.edit_message_text(
            "📅 أدخل تاريخ الدخول:\nمثال: 15/07/2026"
        )

    elif data == "confirm_booking":
        context.user_data["waiting"] = "firstname"
        await query.edit_message_text("📝 أدخل اسمك:")

    elif data == "cancel_booking":
        context.user_data.clear()
        await query.edit_message_text(
            "❌ تم إلغاء الحجز!\n\nاكتب /start للبداية من جديد"
        )

    elif data == "back":
        context.user_data.clear()
        keyboard = [
            [InlineKeyboardButton("🇩🇿 رحلات داخلية", callback_data="domestic")],
            [InlineKeyboardButton("✈️ رحلات خارجية", callback_data="international")],
        ]
        await query.edit_message_text(
            "🌍 مرحباً بكم في وكالة Be Tourist Travel!\n\nاختر نوع الرحلة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    waiting = context.user_data.get("waiting")

    if waiting == "checkin":
        context.user_data["checkin"] = text
        context.user_data["waiting"] = "checkout"
        await update.message.reply_text("📅 أدخل تاريخ الخروج:\nمثال: 22/07/2026")

    elif waiting == "checkout":
        nights = calculate_nights(context.user_data["checkin"], text)
        if nights < 6:
            await update.message.reply_text(
                "⚠️ أقل مدة إقامة هي 7 أيام 6 ليالي!\n"
                "أدخل تاريخ خروج صحيح:"
            )
            return

        context.user_data["checkout"] = text
        context.user_data["nights"] = nights

        adults = context.user_data["adults"]
        children = context.user_data["children"]
        babies = context.user_data["babies"]

        total_adults = adults * nights * PRICE_PER_NIGHT
        total_children = children * nights * (PRICE_PER_NIGHT / 2)
        total = total_adults + total_children

        context.user_data["total"] = total
        context.user_data["waiting"] = None

        text_summary = (
            f"🧮 حساب السعر:\n\n"
            f"🏖️ منتجع الفردوس - بني حواء\n"
            f"📅 {context.user_data['checkin']} → {context.user_data['checkout']}\n"
            f"🌙 {nights} ليالي\n\n"
            f"👨 كبار: {adults} × {nights} × {PRICE_PER_NIGHT:,} = {total_adults:,.0f} دج\n"
            f"👦 أطفال 6-12: {children} × {nights} × {PRICE_PER_NIGHT/2:,.0f} = {total_children:,.0f} دج\n"
            f"👶 رضع -6: {babies} × مجاناً 🎉\n\n"
            f"💰 المجموع الكلي: {total:,.0f} دج\n\n"
            f"هل تريد الحجز؟"
        )

        keyboard = [
            [InlineKeyboardButton("✅ نعم أحجز!", callback_data="confirm_booking")],
            [InlineKeyboardButton("❌ لا شكراً", callback_data="cancel_booking")],
        ]

        await update.message.reply_text(
            text_summary,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif waiting == "firstname":
        context.user_data["firstname"] = text
        context.user_data["waiting"] = "lastname"
        await update.message.reply_text("📝 أدخل لقبك:")

    elif waiting == "lastname":
        context.user_data["lastname"] = text
        context.user_data["waiting"] = "phone"
        await update.message.reply_text("📞 أدخل رقم هاتفك:")

    elif waiting == "phone":
        context.user_data["phone"] = text
        context.user_data["waiting"] = None

        booking_data = {
            "firstname": context.user_data["firstname"],
            "lastname": context.user_data["lastname"],
            "phone": context.user_data["phone"],
            "checkin": context.user_data["checkin"],
            "checkout": context.user_data["checkout"],
            "nights": context.user_data["nights"],
            "adults": context.user_data["adults"],
            "children": context.user_data["children"],
            "babies": context.user_data["babies"],
            "total": context.user_data["total"],
        }

        save_booking(booking_data)

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔔 حجز جديد!\n\n"
                 f"👤 {booking_data['firstname']} {booking_data['lastname']}\n"
                 f"📞 {booking_data['phone']}\n"
                 f"🏖️ منتجع الفردوس - بني حواء\n"
                 f"📅 {booking_data['checkin']} → {booking_data['checkout']}\n"
                 f"🌙 {booking_data['nights']} ليالي\n"
                 f"👨 كبار: {booking_data['adults']}\n"
                 f"👦 أطفال: {booking_data['children']}\n"
                 f"👶 رضع: {booking_data['babies']}\n"
                 f"💰 {booking_data['total']:,.0f} دج"
        )

        await update.message.reply_text(
            f"🎉 تم تسجيل حجزك بنجاح!\n\n"
            f"👤 {booking_data['firstname']} {booking_data['lastname']}\n"
            f"📞 {booking_data['phone']}\n"
            f"🏖️ منتجع الفردوس - بني حواء\n"
            f"📅 {booking_data['checkin']} → {booking_data['checkout']}\n"
            f"🌙 {booking_data['nights']} ليالي\n"
            f"💰 {booking_data['total']:,.0f} دج\n\n"
            f"📞 سنتواصل معك قريباً للتأكيد! 😊\n"
            f"اكتب /start للبداية من جديد"
        )

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot is running!")
app.run_polling()