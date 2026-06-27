from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime
import os

# ========== اعدادات ==========
TOKEN = "8863744686:AAGEh0R4pNjugsGPtAU46pGKMst36yPqxuY"
AUTHORIZED_USER = 1550117523  # ID صديقك

# ========== الوان ==========
GOLD = colors.HexColor('#C9A84C')
DARK_GOLD = colors.HexColor('#8B6914')
LIGHT_GOLD = colors.HexColor('#F5E6C8')
WHITE = colors.white
GRAY = colors.HexColor('#666666')

# ========== الخط العربي ==========
pdfmetrics.registerFont(TTFont('Arabic', '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Arabic-Bold', '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf'))

def ar(text):
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)

def p(text, size=11, bold=False, color=colors.black, align=1):
    font = 'Arabic-Bold' if bold else 'Arabic'
    return Paragraph(ar(text), ParagraphStyle('', fontName=font, fontSize=size, textColor=color, alignment=align))

def get_invoice_number():
    file = "invoice_counter.txt"
    if os.path.exists(file):
        with open(file, "r") as f:
            num = int(f.read()) + 1
    else:
        num = 1
    with open(file, "w") as f:
        f.write(str(num))
    return f"BT-2026-{num:04d}"

def create_invoice(data):
    os.makedirs("invoices", exist_ok=True)
    invoice_num = get_invoice_number()
    filename = f"invoices/invoice_{invoice_num}.pdf"

    doc = SimpleDocTemplate(filename, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm)

    story = []

    # ===== HEADER =====
    header = [[
        Paragraph("BE TOURIST TRAVEL",
            ParagraphStyle('', fontName='Helvetica-Bold', fontSize=20, textColor=GOLD, alignment=1)),
        Table([
            [p("وكالة السياحة والأسفار", 10, True, DARK_GOLD)],
            [p("بليدة - بولفار 20 متر", 9, False, GRAY)],
            [p("0549573865", 9, False, GRAY)],
            [p("betouristtravel@gmail.com", 9, False, GRAY)],
            [p("Be Tourist Travel", 9, False, GRAY)],
        ], colWidths=[8*cm]),
    ]]
    t = Table(header, colWidths=[9*cm, 8*cm])
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    story.append(t)
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=3, color=GOLD))
    story.append(Spacer(1, 0.3*cm))

    # ===== TITLE =====
    title = [[
        Paragraph("FACTURE / فاتورة",
            ParagraphStyle('', fontName='Helvetica-Bold', fontSize=16, textColor=WHITE, alignment=1)),
        Paragraph(f"N°: {data['invoice_num']}\nDate: {datetime.now().strftime('%d/%m/%Y')}",
            ParagraphStyle('', fontName='Helvetica-Bold', fontSize=11, textColor=WHITE, alignment=1)),
    ]]
    t = Table(title, colWidths=[10*cm, 7*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), DARK_GOLD),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),10),
        ('BOTTOMPADDING',(0,0),(-1,-1),10),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4*cm))

    # ===== CLIENT =====
    client = [
        [p("معلومات الزبون", 11, True, DARK_GOLD)],
        [p(f"الاسم واللقب: {data['firstname']} {data['lastname']}", 11)],
        [p(f"الهاتف: {data['phone']}", 11)],
    ]
    t = Table(client, colWidths=[17*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,0), LIGHT_GOLD),
        ('BOX',(0,0),(-1,-1),1,GOLD),
        ('TOPPADDING',(0,0),(-1,-1),8),
        ('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('LEFTPADDING',(0,0),(-1,-1),10),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4*cm))

    # ===== TRIP =====
    trip = [
        [p("تفاصيل الرحلة", 11, True, DARK_GOLD), ""],
        [p("الوجهة:", 11, False, GRAY), p(data['destination'], 11, True)],
        [p("تاريخ الذهاب:", 11, False, GRAY), p(data['depart'], 11, True)],
        [p("تاريخ الإياب:", 11, False, GRAY), p(data['retour'], 11, True)],
        [p("عدد الليالي:", 11, False, GRAY), p(f"{data['nights']} ليالي", 11, True)],
        [p("الفندق:", 11, False, GRAY), p(data['hotel'], 11, True)],
        [p("الإعاشة:", 11, False, GRAY), p(data['pension'], 11, True)],
    ]
    t = Table(trip, colWidths=[7*cm, 10*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0), LIGHT_GOLD),
        ('SPAN',(0,0),(-1,0)),
        ('BOX',(0,0),(-1,-1),1,GOLD),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE, colors.HexColor('#FAFAFA')]),
        ('TOPPADDING',(0,0),(-1,-1),7),
        ('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('LEFTPADDING',(0,0),(-1,-1),10),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4*cm))

    # ===== PRICES =====
    price_rows = [
        [p("البيان", 10, True, WHITE),
         p("العدد", 10, True, WHITE),
         p("السعر", 10, True, WHITE),
         p("المجموع", 10, True, WHITE)],
    ]

    if data['adults'] > 0:
        adult_total = data['adults'] * data['price_adult']
        price_rows.append([
            p("كبار +12 سنة"), p(str(data['adults'])),
            p(f"{data['price_adult']:,.0f} دج"),
            p(f"{adult_total:,.0f} دج")
        ])

    if data['children'] > 0:
        child_total = data['children'] * data['price_child']
        price_rows.append([
            p("أطفال 6-12 سنة"), p(str(data['children'])),
            p(f"{data['price_child']:,.0f} دج"),
            p(f"{child_total:,.0f} دج")
        ])

    if data['babies'] > 0:
        price_rows.append([
            p("رضع 0-6 سنوات"), p(str(data['babies'])),
            p("مجانا"), p("0 دج")
        ])

    t = Table(price_rows, colWidths=[7*cm, 3*cm, 4*cm, 3*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0), DARK_GOLD),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('BOX',(0,0),(-1,-1),1,GOLD),
        ('INNERGRID',(0,0),(-1,-1),0.5,GOLD),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE, LIGHT_GOLD]),
        ('TOPPADDING',(0,0),(-1,-1),8),
        ('BOTTOMPADDING',(0,0),(-1,-1),8),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    # ===== TOTALS =====
    totals = [
        [p("المجموع الكلي:", 12, True), p(f"{data['total']:,.0f} دج", 12, True)],
        [p("المدفوع:", 12, True), p(f"{data['paid']:,.0f} دج", 12, True, colors.HexColor('#2E7D32'))],
        [p("المتبقي:", 12, True), p(f"{data['remaining']:,.0f} دج", 12, True, colors.HexColor('#E65100'))],
    ]
    t = Table(totals, colWidths=[10*cm, 7*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0), LIGHT_GOLD),
        ('BACKGROUND',(0,1),(-1,1), colors.HexColor('#E8F5E9')),
        ('BACKGROUND',(0,2),(-1,2), colors.HexColor('#FFF3E0')),
        ('BOX',(0,0),(-1,-1),1.5,GOLD),
        ('TOPPADDING',(0,0),(-1,-1),10),
        ('BOTTOMPADDING',(0,0),(-1,-1),10),
        ('LEFTPADDING',(0,0),(-1,-1),15),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    # ===== PAYMENT =====
    payment = [[p(f"طريقة الدفع: {data['payment_method']}", 10, False, DARK_GOLD)]]
    t = Table(payment, colWidths=[17*cm])
    t.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),1,GOLD),
        ('BACKGROUND',(0,0),(-1,-1), LIGHT_GOLD),
        ('TOPPADDING',(0,0),(-1,-1),8),
        ('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('LEFTPADDING',(0,0),(-1,-1),10),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    story.append(Spacer(1, 0.2*cm))

    # ===== FOOTER =====
    footer = [[p("شكرا لثقتكم في وكالة Be Tourist Travel", 12, True, DARK_GOLD, 1)]]
    t = Table(footer, colWidths=[17*cm])
    story.append(t)

    doc.build(story)
    return filename, invoice_num

# ========== BOT ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != AUTHORIZED_USER:
        await update.message.reply_text("❌ غير مصرح لك باستخدام هذا البوت!")
        return
    context.user_data.clear()
    await update.message.reply_text(
        "🌍 Be Tourist Travel\n"
        "📄 بوت إنشاء الفواتير\n\n"
        "📝 أدخل اسم الزبون:"
    )
    context.user_data["waiting"] = "firstname"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != AUTHORIZED_USER:
        return

    text = update.message.text
    waiting = context.user_data.get("waiting")

    if waiting == "firstname":
        context.user_data["firstname"] = text
        context.user_data["waiting"] = "lastname"
        await update.message.reply_text("📝 أدخل لقب الزبون:")

    elif waiting == "lastname":
        context.user_data["lastname"] = text
        context.user_data["waiting"] = "phone"
        await update.message.reply_text("📞 أدخل رقم الهاتف:")

    elif waiting == "phone":
        context.user_data["phone"] = text
        context.user_data["waiting"] = "destination"
        await update.message.reply_text("🌍 أدخل الوجهة:")

    elif waiting == "destination":
        context.user_data["destination"] = text
        context.user_data["waiting"] = "depart"
        await update.message.reply_text("📅 تاريخ الذهاب (مثال: 23/07/2026):")

    elif waiting == "depart":
        context.user_data["depart"] = text
        context.user_data["waiting"] = "retour"
        await update.message.reply_text("📅 تاريخ الإياب:")

    elif waiting == "retour":
        context.user_data["retour"] = text
        context.user_data["waiting"] = "nights"
        await update.message.reply_text("🌙 عدد الليالي:")

    elif waiting == "nights":
        context.user_data["nights"] = text
        context.user_data["waiting"] = "hotel"
        await update.message.reply_text("🏨 اسم الفندق:")

    elif waiting == "hotel":
        context.user_data["hotel"] = text
        context.user_data["waiting"] = "pension"
        keyboard = [
            [InlineKeyboardButton("🍳 إفطار فقط", callback_data="pension_إفطار فقط")],
            [InlineKeyboardButton("🍽️ نصف داخلي", callback_data="pension_نصف داخلي")],
            [InlineKeyboardButton("🍱 داخلي كامل", callback_data="pension_داخلي كامل")],
            [InlineKeyboardButton("🌟 كل شيء شامل", callback_data="pension_كل شيء شامل")],
        ]
        await update.message.reply_text("🍽️ نوع الإعاشة:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif waiting == "adults":
        try:
            context.user_data["adults"] = int(text)
            context.user_data["waiting"] = "children"
            await update.message.reply_text("👦 عدد الأطفال 6-12 سنة:")
        except:
            await update.message.reply_text("❌ أدخل رقم صحيح!")

    elif waiting == "children":
        try:
            context.user_data["children"] = int(text)
            context.user_data["waiting"] = "babies"
            await update.message.reply_text("👶 عدد الرضع 0-6 سنوات (مجانا):")
        except:
            await update.message.reply_text("❌ أدخل رقم صحيح!")

    elif waiting == "babies":
        try:
            context.user_data["babies"] = int(text)
            context.user_data["waiting"] = "price_adult"
            await update.message.reply_text("💰 سعر الكبير (دج):")
        except:
            await update.message.reply_text("❌ أدخل رقم صحيح!")

    elif waiting == "price_adult":
        try:
            context.user_data["price_adult"] = float(text)
            if context.user_data["children"] > 0:
                context.user_data["waiting"] = "price_child"
                await update.message.reply_text("💰 سعر الطفل 6-12 (دج):")
            else:
                context.user_data["price_child"] = 0
                total = context.user_data["adults"] * context.user_data["price_adult"]
                context.user_data["total"] = total
                context.user_data["waiting"] = "paid"
                await update.message.reply_text(f"💰 المجموع: {total:,.0f} دج\n\n✅ كم دفع الزبون؟")
        except:
            await update.message.reply_text("❌ أدخل رقم صحيح!")

    elif waiting == "price_child":
        try:
            context.user_data["price_child"] = float(text)
            total = (context.user_data["adults"] * context.user_data["price_adult"]) + \
                    (context.user_data["children"] * context.user_data["price_child"])
            context.user_data["total"] = total
            context.user_data["waiting"] = "paid"
            await update.message.reply_text(f"💰 المجموع: {total:,.0f} دج\n\n✅ كم دفع الزبون؟")
        except:
            await update.message.reply_text("❌ أدخل رقم صحيح!")

    elif waiting == "paid":
        try:
            paid = float(text)
            context.user_data["paid"] = paid
            context.user_data["remaining"] = context.user_data["total"] - paid
            keyboard = [
                [InlineKeyboardButton("💵 نقدا", callback_data="pay_نقدا")],
                [InlineKeyboardButton("📱 CCP", callback_data="pay_CCP")],
                [InlineKeyboardButton("🏦 تحويل بنكي", callback_data="pay_تحويل بنكي")],
                [InlineKeyboardButton("💳 Baridimob", callback_data="pay_Baridimob")],
            ]
            await update.message.reply_text("💳 طريقة الدفع:", reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            await update.message.reply_text("❌ أدخل رقم صحيح!")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("pension_"):
        context.user_data["pension"] = data.replace("pension_", "")
        context.user_data["waiting"] = "adults"
        await query.edit_message_text("👨 عدد الكبار +12 سنة:")

    elif data.startswith("pay_"):
        context.user_data["payment_method"] = data.replace("pay_", "")

        summary = (
            f"📋 ملخص الفاتورة:\n\n"
            f"👤 {context.user_data['firstname']} {context.user_data['lastname']}\n"
            f"📞 {context.user_data['phone']}\n"
            f"🌍 {context.user_data['destination']}\n"
            f"📅 {context.user_data['depart']} → {context.user_data['retour']}\n"
            f"🌙 {context.user_data['nights']} ليالي\n"
            f"🏨 {context.user_data['hotel']}\n"
            f"🍽️ {context.user_data['pension']}\n"
            f"👨 كبار: {context.user_data['adults']}\n"
            f"👦 أطفال: {context.user_data['children']}\n"
            f"👶 رضع: {context.user_data['babies']}\n"
            f"💰 المجموع: {context.user_data['total']:,.0f} دج\n"
            f"✅ المدفوع: {context.user_data['paid']:,.0f} دج\n"
            f"⏳ المتبقي: {context.user_data['remaining']:,.0f} دج\n"
            f"💳 {context.user_data['payment_method']}\n\n"
            f"هل المعلومات صحيحة؟"
        )
        keyboard = [
            [InlineKeyboardButton("✅ إنشاء الفاتورة", callback_data="create")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel")],
        ]
        await query.edit_message_text(summary, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "create":
        await query.edit_message_text("⏳ جاري إنشاء الفاتورة...")
        try:
            context.user_data["invoice_num"] = get_invoice_number()
            filename, invoice_num = create_invoice(context.user_data)

            with open(filename, 'rb') as f:
                await context.bot.send_document(
                    chat_id=AUTHORIZED_USER,
                    document=f,
                    filename=f"فاتورة_{invoice_num}.pdf",
                    caption=f"✅ الفاتورة {invoice_num} جاهزة!\n"
                           f"👤 {context.user_data['firstname']} {context.user_data['lastname']}\n"
                           f"💰 {context.user_data['total']:,.0f} دج"
                )

            await query.edit_message_text(
                f"🎉 تم إنشاء الفاتورة!\n"
                f"رقم: {invoice_num}\n\n"
                f"اكتب /start لفاتورة جديدة"
            )
        except Exception as e:
            await query.edit_message_text(f"❌ خطأ: {e}")

    elif data == "cancel":
        context.user_data.clear()
        await query.edit_message_text("❌ تم الإلغاء!\n\nاكتب /start من جديد")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Invoice Bot is running!")
app.run_polling()