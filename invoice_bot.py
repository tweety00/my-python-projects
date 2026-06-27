from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime
import os

# ========== اعدادات ==========
TOKEN = "8863744686:AAGEh0R4pNjugsGPtAU46pGKMst36yPqxuY"
AUTHORIZED_USER = 1550117523

# ========== الألوان ==========
GOLD = colors.HexColor('#C9A84C')
DARK_GOLD = colors.HexColor('#8B6914')
LIGHT_GOLD = colors.HexColor('#F5E6C8')
WHITE = colors.white
GRAY = colors.HexColor('#666666')
BLACK = colors.black

# ========== الخطوط ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pdfmetrics.registerFont(TTFont('Arabic', '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Arabic-Bold', '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf'))

def ar(text):
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)

def p(text, size=10, bold=False, color=BLACK, align=1):
    font = 'Arabic-Bold' if bold else 'Arabic'
    return Paragraph(ar(text), ParagraphStyle('', fontName=font, fontSize=size, textColor=color, alignment=align))

def pen(text, size=10, bold=False, color=BLACK, align=0):
    font = 'Helvetica-Bold' if bold else 'Helvetica'
    return Paragraph(str(text), ParagraphStyle('', fontName=font, fontSize=size, textColor=color, alignment=align))

def get_invoice_number():
    file = os.path.join(BASE_DIR, "invoice_counter.txt")
    if os.path.exists(file):
        with open(file, "r") as f:
            num = int(f.read()) + 1
    else:
        num = 1
    with open(file, "w") as f:
        f.write(str(num))
    return f"BT-2026-{num:04d}"

def create_invoice(data):
    os.makedirs(os.path.join(BASE_DIR, "invoices"), exist_ok=True)
    invoice_num = data.get("invoice_num", get_invoice_number())
    filename = os.path.join(BASE_DIR, f"invoices/invoice_{invoice_num}.pdf")

    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1*cm, bottomMargin=1*cm
    )

    story = []

    # ===== HEADER =====
    logo_path = os.path.join(BASE_DIR, "logo.jpeg")
    logo = Image(logo_path, width=4*cm, height=4*cm) if os.path.exists(logo_path) else pen("BT", 14, True, GOLD, 1)

    company_info = Table([
        [pen("BE TOURIST TRAVEL", 18, True, GOLD, 1)],
        [p("وكالة السياحة والأسفار", 12, True, DARK_GOLD, 1)],
        [pen("Tourism & Travel Agency", 9, False, GRAY, 1)],
        [pen("0549573865 | betouristtravel@gmail.com", 9, False, GRAY, 1)],
        [pen("Be Tourist Travel", 9, False, GRAY, 1)],
    ], colWidths=[9*cm])
    company_info.setStyle(TableStyle([
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),2),
        ('BOTTOMPADDING',(0,0),(-1,-1),2),
    ]))

    invoice_box = Table([
        [pen("FACTURE / ", 13, True, WHITE, 1), p("فاتورة", 13, True, WHITE, 1)],
        [pen(f"N: {invoice_num}", 10, True, WHITE, 1), ""],
        [pen(f"Date: {datetime.now().strftime('%d/%m/%Y')}", 10, False, WHITE, 1), ""],
    ], colWidths=[3*cm, 3*cm])
    invoice_box.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), DARK_GOLD),
        ('SPAN',(0,1),(-1,1)),
        ('SPAN',(0,2),(-1,2)),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),8),
        ('BOTTOMPADDING',(0,0),(-1,-1),8),
    ]))

    header = Table([[logo, company_info, invoice_box]], colWidths=[4*cm, 9*cm, 6*cm])
    header.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    story.append(header)
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    story.append(Spacer(1, 0.3*cm))

    # ===== CLIENT =====
    story.append(Table([[
        p("معلومات الزبون / Client", 11, True, DARK_GOLD, 1),
    ]], colWidths=[17*cm]))
    story[-1].setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), LIGHT_GOLD),
        ('BOX',(0,0),(-1,-1),1,GOLD),
        ('TOPPADDING',(0,0),(-1,-1),7),
        ('BOTTOMPADDING',(0,0),(-1,-1),7),
    ]))
    story.append(Spacer(1, 0.1*cm))

    client_rows = [
        [pen("Nom / Prénom:", 10, False, GRAY),
         pen(f"{data['firstname']} {data['lastname']}", 10, True),
         p(f"الاسم واللقب: {data['firstname']} {data['lastname']}", 10, True)],
        [pen("Téléphone:", 10, False, GRAY),
         pen(f"{data['phone']}", 10, True),
         p(f"الهاتف: {data['phone']}", 10, True)],
    ]
    if data.get('passport'):
        client_rows.append([
            pen("Passeport:", 10, False, GRAY),
            pen(f"{data['passport']}", 10, True),
            p(f"جواز السفر: {data['passport']}", 10, True)
        ])

    client_table = Table(client_rows, colWidths=[4*cm, 6.5*cm, 6.5*cm])
    client_table.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),1,GOLD),
        ('INNERGRID',(0,0),(-1,-1),0.3,GOLD),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[WHITE, colors.HexColor('#FAFAFA')]),
        ('TOPPADDING',(0,0),(-1,-1),7),
        ('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('LEFTPADDING',(0,0),(-1,-1),10),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 0.3*cm))

    # ===== TRIP =====
    story.append(Table([[
        p("تفاصيل الرحلة / Détails du Voyage", 11, True, DARK_GOLD, 1),
    ]], colWidths=[17*cm]))
    story[-1].setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), LIGHT_GOLD),
        ('BOX',(0,0),(-1,-1),1,GOLD),
        ('TOPPADDING',(0,0),(-1,-1),7),
        ('BOTTOMPADDING',(0,0),(-1,-1),7),
    ]))
    story.append(Spacer(1, 0.1*cm))

    trip_rows = [
        ["Destination:", data['destination'], f"الوجهة: {data['destination']}"],
        ["Départ:", data['depart'], f"تاريخ الذهاب: {data['depart']}"],
        ["Retour:", data['retour'], f"تاريخ الإياب: {data['retour']}"],
        ["Nuits:", f"{data['nights']} Nuits", f"عدد الليالي: {data['nights']} ليالي"],
        ["Hôtel:", data['hotel'], f"الفندق: {data['hotel']}"],
        ["Pension:", data['pension'], f"الإعاشة: {data['pension']}"],
    ]

    trip_table = Table([
        [pen(r[0], 10, False, GRAY), pen(r[1], 10, True), p(r[2], 10, True)]
        for r in trip_rows
    ], colWidths=[4*cm, 6.5*cm, 6.5*cm])
    trip_table.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),1,GOLD),
        ('INNERGRID',(0,0),(-1,-1),0.3,GOLD),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[WHITE, colors.HexColor('#FAFAFA')]),
        ('TOPPADDING',(0,0),(-1,-1),6),
        ('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),10),
    ]))
    story.append(trip_table)
    story.append(Spacer(1, 0.3*cm))

    # ===== PRICES =====
    story.append(Table([[
        p("الأسعار / PRIX", 11, True, WHITE, 1),
    ]], colWidths=[17*cm]))
    story[-1].setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), DARK_GOLD),
        ('TOPPADDING',(0,0),(-1,-1),7),
        ('BOTTOMPADDING',(0,0),(-1,-1),7),
    ]))

    price_header = Table([[
        pen("Item", 10, True, WHITE, 1),
        p("البيان", 10, True, WHITE, 1),
        pen("Qté", 10, True, WHITE, 1),
        pen("Prix unit.", 10, True, WHITE, 1),
        p("السعر", 10, True, WHITE, 1),
        pen("Total", 10, True, WHITE, 1),
        p("المجموع", 10, True, WHITE, 1),
    ]], colWidths=[3*cm, 4*cm, 2*cm, 3*cm, 2*cm, 2*cm, 2*cm])
    price_header.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), DARK_GOLD),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),6),
        ('BOTTOMPADDING',(0,0),(-1,-1),6),
    ]))
    story.append(price_header)

    price_rows = []

    if data['adults'] > 0:
        adult_total = data['adults'] * data['price_adult']
        price_rows.append([
            pen("Adultes +12 ans", 9, False, BLACK, 1),
            p("كبار +12 سنة", 9, False, BLACK, 1),
            pen(str(data['adults']), 10, True, BLACK, 1),
            pen(f"{data['price_adult']:,.0f} DZD", 9, False, BLACK, 1),
            p(f"{data['price_adult']:,.0f} دج", 9, False, BLACK, 1),
            pen(f"{adult_total:,.0f} DZD", 10, True, BLACK, 1),
            p(f"{adult_total:,.0f} دج", 10, True, BLACK, 1),
        ])

    if data['children'] > 0:
        child_total = data['children'] * data['price_child']
        price_rows.append([
            pen("Enfants 6-12 ans", 9, False, BLACK, 1),
            p("أطفال 6-12 سنة", 9, False, BLACK, 1),
            pen(str(data['children']), 10, True, BLACK, 1),
            pen(f"{data['price_child']:,.0f} DZD", 9, False, BLACK, 1),
            p(f"{data['price_child']:,.0f} دج", 9, False, BLACK, 1),
            pen(f"{child_total:,.0f} DZD", 10, True, BLACK, 1),
            p(f"{child_total:,.0f} دج", 10, True, BLACK, 1),
        ])

    if data['babies'] > 0:
        price_rows.append([
            pen("Bébés 0-6 ans", 9, False, BLACK, 1),
            p("رضع 0-6 سنوات", 9, False, BLACK, 1),
            pen(str(data['babies']), 10, True, BLACK, 1),
            pen("Gratuit", 9, False, BLACK, 1),
            p("مجانا", 9, False, BLACK, 1),
            pen("0 DZD", 10, True, BLACK, 1),
            p("0 دج", 10, True, BLACK, 1),
        ])

    price_table = Table(price_rows, colWidths=[3*cm, 4*cm, 2*cm, 3*cm, 2*cm, 2*cm, 2*cm])
    price_table.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),1,GOLD),
        ('INNERGRID',(0,0),(-1,-1),0.3,GOLD),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[WHITE, LIGHT_GOLD]),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),6),
        ('BOTTOMPADDING',(0,0),(-1,-1),6),
    ]))
    story.append(price_table)
    story.append(Spacer(1, 0.2*cm))

    # ===== TOTALS =====
    totals = Table([
        [pen("Total / ", 11, True, DARK_GOLD, 1),
         p("المجموع الكلي", 11, True, DARK_GOLD, 1),
         pen(f"{data['total']:,.0f} DZD", 12, True, BLACK, 1),
         p(f"{data['total']:,.0f} دج", 12, True, BLACK, 1)],
        [pen("Versé / ", 11, True, colors.HexColor('#2E7D32'), 1),
         p("المدفوع", 11, True, colors.HexColor('#2E7D32'), 1),
         pen(f"{data['paid']:,.0f} DZD", 12, True, colors.HexColor('#2E7D32'), 1),
         p(f"{data['paid']:,.0f} دج", 12, True, colors.HexColor('#2E7D32'), 1)],
        [pen("Reste / ", 11, True, colors.HexColor('#E65100'), 1),
         p("المتبقي", 11, True, colors.HexColor('#E65100'), 1),
         pen(f"{data['remaining']:,.0f} DZD", 12, True, colors.HexColor('#E65100'), 1),
         p(f"{data['remaining']:,.0f} دج", 12, True, colors.HexColor('#E65100'), 1)],
    ], colWidths=[3*cm, 5*cm, 4.5*cm, 4.5*cm])
    totals.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),1.5,GOLD),
        ('LINEBELOW',(0,0),(-1,1),0.5,GOLD),
        ('BACKGROUND',(0,0),(-1,0), LIGHT_GOLD),
        ('BACKGROUND',(0,1),(-1,1), colors.HexColor('#E8F5E9')),
        ('BACKGROUND',(0,2),(-1,2), colors.HexColor('#FFF3E0')),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),8),
        ('BOTTOMPADDING',(0,0),(-1,-1),8),
    ]))
    story.append(totals)
    story.append(Spacer(1, 0.2*cm))

    # ===== PAYMENT =====
    payment = Table([[
        pen(f"Mode de paiement: {data['payment_method']}", 10, False, DARK_GOLD, 0),
        p(f"طريقة الدفع: {data['payment_method']}", 10, False, DARK_GOLD, 1),
    ]], colWidths=[8.5*cm, 8.5*cm])
    payment.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),1,GOLD),
        ('BACKGROUND',(0,0),(-1,-1), LIGHT_GOLD),
        ('TOPPADDING',(0,0),(-1,-1),7),
        ('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('LEFTPADDING',(0,0),(-1,-1),10),
    ]))
    story.append(payment)
    story.append(Spacer(1, 0.4*cm))

    # ===== SIGNATURE =====
    signature = Table([[
        Table([
            [pen("Cachet et Signature:", 10, True, DARK_GOLD, 1)],
            [p("الختم والإمضاء:", 10, True, DARK_GOLD, 1)],
            [Spacer(1, 1.5*cm)],
            [HRFlowable(width="100%", thickness=1, color=GOLD)],
        ], colWidths=[8*cm]),
        Table([
            [pen("Client Signature:", 10, True, DARK_GOLD, 1)],
            [p("إمضاء الزبون:", 10, True, DARK_GOLD, 1)],
            [Spacer(1, 1.5*cm)],
            [HRFlowable(width="100%", thickness=1, color=GOLD)],
        ], colWidths=[8*cm]),
    ]], colWidths=[8.5*cm, 8.5*cm])
    signature.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),1,GOLD),
        ('LINEAFTER',(0,0),(0,-1),1,GOLD),
        ('TOPPADDING',(0,0),(-1,-1),10),
        ('BOTTOMPADDING',(0,0),(-1,-1),10),
        ('LEFTPADDING',(0,0),(-1,-1),10),
        ('RIGHTPADDING',(0,0),(-1,-1),10),
    ]))
    story.append(signature)
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    story.append(Spacer(1, 0.2*cm))

    # ===== FOOTER =====
    footer = Table([[
        p("شكراً لثقتكم في وكالة Be Tourist Travel", 11, True, DARK_GOLD, 1),
        pen("Merci de votre confiance - Be Tourist Travel", 10, True, DARK_GOLD, 1),
    ]], colWidths=[8.5*cm, 8.5*cm])
    story.append(footer)

    doc.build(story)
    return filename, invoice_num


# ========== BOT ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != AUTHORIZED_USER:
        await update.message.reply_text("❌ غير مصرح!")
        return
    context.user_data.clear()
    await update.message.reply_text(
        "🌍 Be Tourist Travel\n"
        "📄 بوت إنشاء الفواتير\n\n"
        "📝 أدخل اسم الزبون / Prénom du client:"
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
        await update.message.reply_text("📝 اللقب / Nom de famille:")

    elif waiting == "lastname":
        context.user_data["lastname"] = text
        context.user_data["waiting"] = "phone"
        await update.message.reply_text("📞 رقم الهاتف / Téléphone:")

    elif waiting == "phone":
        context.user_data["phone"] = text
        context.user_data["waiting"] = "passport"
        keyboard = [
            [InlineKeyboardButton("✅ نعم / Oui", callback_data="passport_yes")],
            [InlineKeyboardButton("❌ لا / Non", callback_data="passport_no")],
        ]
        await update.message.reply_text(
            "🛂 هل تريد إضافة رقم جواز السفر؟\nAjouter le numéro de passeport?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif waiting == "passport_num":
        context.user_data["passport"] = text
        context.user_data["waiting"] = "destination"
        await update.message.reply_text("🌍 الوجهة / Destination:")

    elif waiting == "destination":
        context.user_data["destination"] = text
        context.user_data["waiting"] = "depart"
        await update.message.reply_text("📅 تاريخ الذهاب / Date de départ (ex: 23/07/2026):")

    elif waiting == "depart":
        context.user_data["depart"] = text
        context.user_data["waiting"] = "retour"
        await update.message.reply_text("📅 تاريخ الإياب / Date de retour:")

    elif waiting == "retour":
        context.user_data["retour"] = text
        context.user_data["waiting"] = "nights"
        await update.message.reply_text("🌙 عدد الليالي / Nombre de nuits:")

    elif waiting == "nights":
        context.user_data["nights"] = text
        context.user_data["waiting"] = "hotel"
        await update.message.reply_text("🏨 اسم الفندق / Hôtel:")

    elif waiting == "hotel":
        context.user_data["hotel"] = text
        keyboard = [
            [InlineKeyboardButton("🍳 Petit déjeuner / إفطار", callback_data="pension_Petit déjeuner / إفطار")],
            [InlineKeyboardButton("🍽️ Demi-pension / نصف داخلي", callback_data="pension_Demi-pension / نصف داخلي")],
            [InlineKeyboardButton("🍱 Pension complète / داخلي كامل", callback_data="pension_Pension complète / داخلي كامل")],
            [InlineKeyboardButton("🌟 All inclusive / كل شيء شامل", callback_data="pension_All inclusive / كل شيء شامل")],
        ]
        await update.message.reply_text("🍽️ الإعاشة / Pension:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif waiting == "adults":
        try:
            context.user_data["adults"] = int(text)
            context.user_data["waiting"] = "children"
            await update.message.reply_text("👦 عدد الأطفال 6-12 / Enfants 6-12 ans:")
        except:
            await update.message.reply_text("❌ رقم غير صحيح!")

    elif waiting == "children":
        try:
            context.user_data["children"] = int(text)
            context.user_data["waiting"] = "babies"
            await update.message.reply_text("👶 عدد الرضع 0-6 / Bébés 0-6 ans (مجانا/Gratuit):")
        except:
            await update.message.reply_text("❌ رقم غير صحيح!")

    elif waiting == "babies":
        try:
            context.user_data["babies"] = int(text)
            context.user_data["waiting"] = "price_adult"
            await update.message.reply_text("💰 سعر الكبير / Prix adulte (DZD):")
        except:
            await update.message.reply_text("❌ رقم غير صحيح!")

    elif waiting == "price_adult":
        try:
            context.user_data["price_adult"] = float(text)
            if context.user_data["children"] > 0:
                context.user_data["waiting"] = "price_child"
                await update.message.reply_text("💰 سعر الطفل / Prix enfant (DZD):")
            else:
                context.user_data["price_child"] = 0
                total = context.user_data["adults"] * context.user_data["price_adult"]
                context.user_data["total"] = total
                context.user_data["waiting"] = "paid"
                await update.message.reply_text(f"💰 المجموع / Total: {total:,.0f} DZD\n\n✅ المدفوع / Versé (DZD):")
        except:
            await update.message.reply_text("❌ رقم غير صحيح!")

    elif waiting == "price_child":
        try:
            context.user_data["price_child"] = float(text)
            total = (context.user_data["adults"] * context.user_data["price_adult"]) + \
                    (context.user_data["children"] * context.user_data["price_child"])
            context.user_data["total"] = total
            context.user_data["waiting"] = "paid"
            await update.message.reply_text(f"💰 المجموع / Total: {total:,.0f} DZD\n\n✅ المدفوع / Versé (DZD):")
        except:
            await update.message.reply_text("❌ رقم غير صحيح!")

    elif waiting == "paid":
        try:
            paid = float(text)
            context.user_data["paid"] = paid
            context.user_data["remaining"] = context.user_data["total"] - paid
            keyboard = [
                [InlineKeyboardButton("💵 Espèces / نقدا", callback_data="pay_Espèces / نقدا")],
                [InlineKeyboardButton("📱 CCP", callback_data="pay_CCP")],
                [InlineKeyboardButton("🏦 Virement / تحويل بنكي", callback_data="pay_Virement / تحويل بنكي")],
                [InlineKeyboardButton("💳 Baridimob", callback_data="pay_Baridimob")],
            ]
            await update.message.reply_text(
                "💳 طريقة الدفع / Mode de paiement:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            await update.message.reply_text("❌ رقم غير صحيح!")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "passport_yes":
        context.user_data["waiting"] = "passport_num"
        await query.edit_message_text("🛂 أدخل رقم جواز السفر / Numéro de passeport:")

    elif data == "passport_no":
        context.user_data["passport"] = None
        context.user_data["waiting"] = "destination"
        await query.edit_message_text("🌍 الوجهة / Destination:")

    elif data.startswith("pension_"):
        context.user_data["pension"] = data.replace("pension_", "")
        context.user_data["waiting"] = "adults"
        await query.edit_message_text("👨 عدد الكبار / Adultes (+12 ans):")

    elif data.startswith("pay_"):
        context.user_data["payment_method"] = data.replace("pay_", "")

        summary = (
            f"📋 ملخص / Récapitulatif:\n\n"
            f"👤 {context.user_data['firstname']} {context.user_data['lastname']}\n"
            f"📞 {context.user_data['phone']}\n"
        )
        if context.user_data.get('passport'):
            summary += f"🛂 {context.user_data['passport']}\n"
        summary += (
            f"🌍 {context.user_data['destination']}\n"
            f"📅 {context.user_data['depart']} → {context.user_data['retour']}\n"
            f"🌙 {context.user_data['nights']} ليالي\n"
            f"🏨 {context.user_data['hotel']}\n"
            f"🍽️ {context.user_data['pension']}\n"
            f"👨 كبار: {context.user_data['adults']}\n"
            f"👦 أطفال: {context.user_data['children']}\n"
            f"👶 رضع: {context.user_data['babies']}\n"
            f"💰 المجموع: {context.user_data['total']:,.0f} DZD\n"
            f"✅ المدفوع: {context.user_data['paid']:,.0f} DZD\n"
            f"⏳ المتبقي: {context.user_data['remaining']:,.0f} DZD\n"
            f"💳 {context.user_data['payment_method']}\n\n"
            f"هل المعلومات صحيحة؟"
        )
        keyboard = [
            [InlineKeyboardButton("✅ إنشاء الفاتورة / Créer", callback_data="create")],
            [InlineKeyboardButton("❌ إلغاء / Annuler", callback_data="cancel")],
        ]
        await query.edit_message_text(summary, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "create":
        await query.edit_message_text("⏳ جاري إنشاء الفاتورة / Création en cours...")
        try:
            context.user_data["invoice_num"] = get_invoice_number()
            filename, invoice_num = create_invoice(context.user_data)

            with open(filename, 'rb') as f:
                await context.bot.send_document(
                    chat_id=AUTHORIZED_USER,
                    document=f,
                    filename=f"Facture_{invoice_num}.pdf",
                    caption=f"✅ Facture {invoice_num}\n"
                           f"👤 {context.user_data['firstname']} {context.user_data['lastname']}\n"
                           f"💰 {context.user_data['total']:,.0f} DZD"
                )

            await query.edit_message_text(
                f"🎉 تم إنشاء الفاتورة!\n"
                f"N°: {invoice_num}\n\n"
                f"اكتب /start لفاتورة جديدة"
            )
        except Exception as e:
            await query.edit_message_text(f"❌ خطأ: {e}")

    elif data == "cancel":
        context.user_data.clear()
        await query.edit_message_text("❌ ملغى / Annulé\n\nاكتب /start من جديد")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Invoice Bot is running!")
app.run_polling()