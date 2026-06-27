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

GOLD = colors.HexColor('#C9A84C')
DARK_GOLD = colors.HexColor('#8B6914')
LIGHT_GOLD = colors.HexColor('#F5E6C8')
WHITE = colors.white
GRAY = colors.HexColor('#666666')

# تسجيل الخط العربي
pdfmetrics.registerFont(TTFont('Arabic', '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Arabic-Bold', '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf'))

def ar(text):
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)

def p(text, size=11, bold=False, color=colors.black, align=1):
    font = 'Arabic-Bold' if bold else 'Arabic'
    return Paragraph(
        ar(text),
        ParagraphStyle('', fontName=font, fontSize=size, textColor=color, alignment=align)
    )

def create_test():
    doc = SimpleDocTemplate(
        "test_invoice.pdf",
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    story = []

    # HEADER
    header = [[
        Paragraph("BE TOURIST TRAVEL",
            ParagraphStyle('', fontName='Helvetica-Bold', fontSize=22, textColor=GOLD, alignment=1)),
        p("وكالة السياحة والأسفار\nبليدة - بولفار 20 متر\n0549573865", 10, False, GRAY, 1),
    ]]
    t = Table(header, colWidths=[9*cm, 8*cm])
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    story.append(t)
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=3, color=GOLD))
    story.append(Spacer(1, 0.3*cm))

    # TITLE
    title = [[
        Paragraph("FACTURE",
            ParagraphStyle('', fontName='Helvetica-Bold', fontSize=16, textColor=WHITE, alignment=1)),
        Paragraph(f"N: BT-2026-0001 | {datetime.now().strftime('%d/%m/%Y')}",
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

    # CLIENT
    client = [
        [p("معلومات الزبون", 11, True, DARK_GOLD)],
        [p("الاسم: أحمد محمد", 11)],
        [p("الهاتف: 0549573865", 11)],
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

    # TRIP
    trip = [
        [p("تفاصيل الرحلة", 11, True, DARK_GOLD), ""],
        [p("الوجهة:", 11, False, GRAY), p("تونس", 11, True)],
        [p("تاريخ الذهاب:", 11, False, GRAY), p("23/07/2026", 11, True)],
        [p("تاريخ الإياب:", 11, False, GRAY), p("30/07/2026", 11, True)],
        [p("عدد الليالي:", 11, False, GRAY), p("7 ليالي", 11, True)],
        [p("الفندق:", 11, False, GRAY), p("فندق الجزيرة", 11, True)],
        [p("الإعاشة:", 11, False, GRAY), p("نصف داخلي", 11, True)],
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

    # PRICES
    price_rows = [
        [p("البيان", 10, True, WHITE), p("العدد", 10, True, WHITE),
         p("السعر", 10, True, WHITE), p("المجموع", 10, True, WHITE)],
        [p("كبار +12 سنة"), p("2"), p("50,000 دج"), p("100,000 دج")],
        [p("أطفال 6-12 سنة"), p("1"), p("35,000 دج"), p("35,000 دج")],
        [p("رضع 0-6 سنوات"), p("1"), p("مجانا"), p("0 دج")],
    ]
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

    # TOTALS
    totals = [
        [p("المجموع الكلي:", 12, True), p("135,000 دج", 12, True)],
        [p("المدفوع:", 12, True), p("50,000 دج", 12, True, colors.HexColor('#2E7D32'))],
        [p("المتبقي:", 12, True), p("85,000 دج", 12, True, colors.HexColor('#E65100'))],
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

    # PAYMENT
    payment = [[p("طريقة الدفع: نقدا", 10, False, DARK_GOLD)]]
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

    # FOOTER
    footer = [[p("شكرا لثقتكم في وكالة Be Tourist Travel", 12, True, DARK_GOLD, 1)]]
    t = Table(footer, colWidths=[17*cm])
    story.append(t)

    doc.build(story)
    print("test_invoice.pdf created!")

create_test()