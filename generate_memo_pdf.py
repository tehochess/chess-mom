"""
Generates a clean, well-formatted PDF of the Samuel He / Starbucks strategic analysis.
Uses ReportLab for precise typographic control.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import FrameBreak
from reportlab.lib import colors

# ── BRAND PALETTE ─────────────────────────────────────────────────────────────
SBUX_DARK    = HexColor("#1E3932")   # deep forest green
SBUX_GREEN   = HexColor("#00704A")   # Starbucks green
SBUX_GOLD    = HexColor("#CBA258")   # warm gold
SBUX_CREAM   = HexColor("#F7F5F0")   # off-white page bg tone
SBUX_LIGHT   = HexColor("#D4EDDA")   # light mint for table headers
SLATE        = HexColor("#4A5568")   # body text
LIGHT_RULE   = HexColor("#CBD5E0")   # divider lines
HIGHLIGHT_BG = HexColor("#EBF4EE")   # soft green highlight boxes
GOLD_BG      = HexColor("#FDF6EC")   # soft gold for callout boxes
WHITE        = HexColor("#FFFFFF")


# ── DOCUMENT SETUP ────────────────────────────────────────────────────────────
OUTPUT_PATH = "C:/Users/hesam/project/Samuel_He_Starbucks_Strategy_Memo.pdf"

doc = SimpleDocTemplate(
    OUTPUT_PATH,
    pagesize=letter,
    leftMargin=0.85*inch,
    rightMargin=0.85*inch,
    topMargin=0.9*inch,
    bottomMargin=0.9*inch,
    title="Samuel He — Starbucks Value Creation Analysis",
    author="Talent Strategy Analysis",
)

# ── STYLE DEFINITIONS ─────────────────────────────────────────────────────────
styles = getSampleStyleSheet()
W = doc.width   # usable page width

def style(name, **kwargs):
    return ParagraphStyle(name, **kwargs)

# Cover / document header
cover_title = style("CoverTitle",
    fontName="Helvetica-Bold", fontSize=22, textColor=WHITE,
    leading=28, spaceAfter=6, alignment=TA_LEFT)

cover_sub = style("CoverSub",
    fontName="Helvetica", fontSize=11, textColor=HexColor("#D4EDDA"),
    leading=16, spaceAfter=4, alignment=TA_LEFT)

cover_meta = style("CoverMeta",
    fontName="Helvetica", fontSize=9, textColor=HexColor("#A8C5B5"),
    leading=14, alignment=TA_LEFT)

# Part header (PART I, PART II...)
part_header = style("PartHeader",
    fontName="Helvetica-Bold", fontSize=8, textColor=SBUX_GREEN,
    leading=12, spaceBefore=18, spaceAfter=2,
    letterSpacing=2, alignment=TA_LEFT)

# Section title
section_title = style("SectionTitle",
    fontName="Helvetica-Bold", fontSize=14, textColor=SBUX_DARK,
    leading=18, spaceBefore=4, spaceAfter=8, alignment=TA_LEFT)

# Sub-section heading
sub_heading = style("SubHeading",
    fontName="Helvetica-Bold", fontSize=10.5, textColor=SBUX_DARK,
    leading=14, spaceBefore=10, spaceAfter=4, alignment=TA_LEFT)

# Body text
body = style("Body",
    fontName="Helvetica", fontSize=9.5, textColor=SLATE,
    leading=15, spaceAfter=7, alignment=TA_JUSTIFY)

# Body bold inline
body_lead = style("BodyLead",
    fontName="Helvetica-Bold", fontSize=9.5, textColor=SLATE,
    leading=15, spaceAfter=7, alignment=TA_JUSTIFY)

# Bullet item
bullet_item = style("BulletItem",
    fontName="Helvetica", fontSize=9.5, textColor=SLATE,
    leading=14, spaceAfter=4, leftIndent=14, alignment=TA_LEFT)

# Numbered item
numbered = style("Numbered",
    fontName="Helvetica", fontSize=9.5, textColor=SLATE,
    leading=14, spaceAfter=4, leftIndent=14, alignment=TA_LEFT)

# Callout quote (green box text)
callout = style("Callout",
    fontName="Helvetica-Oblique", fontSize=9.5, textColor=SBUX_DARK,
    leading=15, spaceAfter=0, alignment=TA_LEFT)

# Caption / footnote
caption = style("Caption",
    fontName="Helvetica-Oblique", fontSize=8, textColor=HexColor("#718096"),
    leading=12, spaceAfter=4, alignment=TA_LEFT)

# Table cell styles
tbl_header = style("TblHeader",
    fontName="Helvetica-Bold", fontSize=8.5, textColor=WHITE,
    leading=12, alignment=TA_LEFT)

tbl_cell = style("TblCell",
    fontName="Helvetica", fontSize=8.5, textColor=SLATE,
    leading=13, alignment=TA_LEFT)

tbl_cell_bold = style("TblCellBold",
    fontName="Helvetica-Bold", fontSize=8.5, textColor=SBUX_DARK,
    leading=13, alignment=TA_LEFT)


# ── HELPER FUNCTIONS ──────────────────────────────────────────────────────────

def rule(color=LIGHT_RULE, thickness=0.5, space_before=4, space_after=8):
    return [
        Spacer(1, space_before),
        HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=space_after),
    ]

def green_rule():
    return [
        Spacer(1, 2),
        HRFlowable(width="100%", thickness=1.5, color=SBUX_GREEN, spaceAfter=6),
    ]

def part_label(text):
    return Paragraph(text, part_header)

def section(text):
    return Paragraph(text, section_title)

def sub(text):
    return Paragraph(text, sub_heading)

def p(text):
    return Paragraph(text, body)

def b(text):
    """Bullet point."""
    return Paragraph(f"<b>·</b>  {text}", bullet_item)

def callout_box(text, bg=HIGHLIGHT_BG, border=SBUX_GREEN):
    """Shaded callout block."""
    inner = Paragraph(text, callout)
    tbl = Table([[inner]], colWidths=[W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("LEFTPADDING",  (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING",   (0,0), (-1,-1), 10),
        ("BOTTOMPADDING",(0,0), (-1,-1), 10),
        ("LINECOLOR",    (0,0), (-1,-1), border),
        ("LINEBEFORE",   (0,0), (0,-1), 3, border),
        ("GRID",         (0,0), (-1,-1), 0, colors.white),
    ]))
    return tbl

def gold_box(text):
    return callout_box(text, bg=GOLD_BG, border=SBUX_GOLD)

def spacer(h=6):
    return Spacer(1, h)

def data_table(headers, rows, col_widths=None):
    if col_widths is None:
        col_widths = [W / len(headers)] * len(headers)
    header_row = [Paragraph(h, tbl_header) for h in headers]
    body_rows  = []
    for row in rows:
        body_rows.append([Paragraph(str(c), tbl_cell) for c in row])
    data = [header_row] + body_rows
    tbl = Table(data, colWidths=col_widths)
    tbl_style = [
        ("BACKGROUND",    (0,0), (-1,0),  SBUX_DARK),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, HIGHLIGHT_BG]),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("GRID",          (0,0), (-1,-1), 0.4, LIGHT_RULE),
        ("LINEABOVE",     (0,0), (-1,0),  1,   SBUX_DARK),
        ("LINEBELOW",     (0,-1),(-1,-1), 1,   LIGHT_RULE),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]
    tbl.setStyle(TableStyle(tbl_style))
    return tbl


# ── COVER BLOCK ───────────────────────────────────────────────────────────────

def make_cover():
    cover_data = [[
        Paragraph("TALENT STRATEGY MEMO", style("CS1",
            fontName="Helvetica-Bold", fontSize=7.5,
            textColor=HexColor("#A8C5B5"), leading=10,
            letterSpacing=2.5)),
        ""
    ], [
        Paragraph("Samuel He × Starbucks Corporation", style("CS2",
            fontName="Helvetica-Bold", fontSize=20,
            textColor=WHITE, leading=26)),
        ""
    ], [
        Paragraph("Value Creation &amp; Strategic Fit Analysis", style("CS3",
            fontName="Helvetica", fontSize=12,
            textColor=HexColor("#D4EDDA"), leading=18)),
        ""
    ], [
        Paragraph("Based on FY2023 Annual Report (10-K) &amp; Resume Review", style("CS4",
            fontName="Helvetica-Oblique", fontSize=9,
            textColor=HexColor("#A8C5B5"), leading=14)),
        Paragraph("March 2026", style("CS5",
            fontName="Helvetica", fontSize=9,
            textColor=HexColor("#A8C5B5"), leading=14,
            alignment=TA_LEFT)),
    ]]

    cover = Table(cover_data, colWidths=[W*0.75, W*0.25])
    cover.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), SBUX_DARK),
        ("LEFTPADDING",   (0,0), (-1,-1), 22),
        ("RIGHTPADDING",  (0,0), (-1,-1), 22),
        ("TOPPADDING",    (0,0), (0,0),   20),
        ("TOPPADDING",    (0,1), (-1,1),  6),
        ("TOPPADDING",    (0,2), (-1,2),  4),
        ("TOPPADDING",    (0,3), (-1,3),  14),
        ("BOTTOMPADDING", (0,3), (-1,3),  20),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    return cover


# ── ASSEMBLE CONTENT ──────────────────────────────────────────────────────────

story = []

# ── COVER ─────────────────────────────────────────────────────────────────────
story.append(make_cover())
story.append(spacer(18))

# ── MEMO HEADER TABLE ─────────────────────────────────────────────────────────
meta_style = style("Meta", fontName="Helvetica", fontSize=9, textColor=SLATE, leading=14)
meta_bold  = style("MetaBold", fontName="Helvetica-Bold", fontSize=9, textColor=SBUX_DARK, leading=14)

meta_data = [
    [Paragraph("TO",   meta_bold), Paragraph("Hiring Strategy / Talent Advisory", meta_style)],
    [Paragraph("FROM", meta_bold), Paragraph("Talent Strategy Analysis", meta_style)],
    [Paragraph("RE",   meta_bold), Paragraph("Samuel He — Value Creation Assessment for Starbucks Corporation", meta_style)],
    [Paragraph("DATE", meta_bold), Paragraph("March 11, 2026", meta_style)],
]
meta_tbl = Table(meta_data, colWidths=[0.7*inch, W - 0.7*inch])
meta_tbl.setStyle(TableStyle([
    ("LEFTPADDING",  (0,0), (-1,-1), 0),
    ("RIGHTPADDING", (0,0), (-1,-1), 0),
    ("TOPPADDING",   (0,0), (-1,-1), 3),
    ("BOTTOMPADDING",(0,0), (-1,-1), 3),
    ("VALIGN",       (0,0), (-1,-1), "TOP"),
]))
story.append(meta_tbl)
story += rule(LIGHT_RULE, 0.5, 8, 6)
story += green_rule()
story.append(spacer(4))

# ── EXECUTIVE SUMMARY ─────────────────────────────────────────────────────────
story.append(part_label("EXECUTIVE SUMMARY"))
story.append(section("Overview"))

story.append(callout_box(
    "Samuel He is a Redmond-based data analyst with approximately three years of post-graduate experience in "
    "loyalty analytics, customer churn modeling, and dashboard infrastructure — capabilities that map directly "
    "to Starbucks' most commercially significant analytical priorities. His strongest transferable asset is his "
    "Bass Pro Shops tenure, where he operated at meaningful scale (500K+ customer records, 170+ retail locations) "
    "on problems structurally identical to those Starbucks faces in its Starbucks Rewards program and comparable "
    "store sales optimization."
))
story.append(spacer(8))
story.append(p(
    "He is not a senior hire and carries real limitations in enterprise-scale data engineering and beverage/CPG "
    "domain knowledge, but his technical stack is well-matched to Starbucks' environment, and he is geographically "
    "co-located with Starbucks' technology teams in the Redmond area. The most compelling case for hiring Samuel "
    "is in <b>Customer Intelligence or Loyalty Analytics</b>, where his churn modeling and segmentation work "
    "provides day-one relevance to Starbucks' highest-priority digital platform. He represents a mid-tier "
    "analytical hire with above-average ceiling given his ML exposure."
))

story += rule()

# ── PART I ────────────────────────────────────────────────────────────────────
story.append(part_label("PART I"))
story.append(section("Starbucks Strategic Priorities and Business Context"))

story.append(sub("Six Core Strategic Priorities"))
story.append(p(
    "Starbucks' FY2023 10-K makes clear the company is executing a multi-year operational and digital "
    "transformation under its <b>Reinvention Plan</b>. Six priorities dominate."
))

priorities = [
    ["#", "Priority", "Key Metric / Signal"],
    ["1", "Starbucks Rewards & Mobile Order/Pay — primary engine of comp store sales growth",
         "NA comp sales +9%; transactions +3%"],
    ["2", "Global store expansion — China (+785 stores), disciplined U.S. growth",
         "38,038 total stores; +2,327 net FY23"],
    ["3", "Licensed store & Channel Development growth — highest-margin segment at 51.1% op. margin",
         "Licensed rev +23.4% YoY"],
    ["4", "Technology investment — $140M incremental FY23, capex rising to $3.0B in FY24",
         "Op margin +200 bps FY23"],
    ["5", "Margin management — offset wage (+250 bps headwind) and commodity inflation via pricing/efficiency",
         "Operating income: $5.87B (+27%)"],
    ["6", "Omni-channel / digital personalization — app, delivery, contactless pickup, Starbucks Now (China)",
         "Mobile Order & Pay share growing"],
]
story.append(data_table(
    priorities[0], priorities[1:],
    col_widths=[0.25*inch, W*0.62, W*0.27]
))
story.append(spacer(10))

story.append(sub("Key Financial Context for Analytical Talent"))
story.append(p(
    "Starbucks carries <b>$15.5B in principal debt obligations</b>, meaning capital discipline is serious. "
    "The company returned $3.4B to shareholders in FY23 while simultaneously investing heavily in technology "
    "and wages — a sign of tight resource allocation. Analysts who can demonstrate impact on comparable store "
    "sales, loyalty retention, or channel revenue mix will have organizational visibility. "
    "<b>Those who can only report on what happened will not.</b>"
))

story += rule()

# ── PART II ───────────────────────────────────────────────────────────────────
story.append(part_label("PART II"))
story.append(section("Samuel He: Capability Assessment"))

story.append(sub("Technical Strengths"))
story.append(p(
    "Samuel's technical stack is genuinely broad for his experience level. He is proficient in "
    "<b>SQL and Snowflake</b> — the standard analytical infrastructure layers at enterprise retail. "
    "His <b>Tableau and Domo</b> work is directly applicable. AWS certifications (Cloud Practitioner + "
    "Solutions Architect Associate) indicate comfort with cloud data environments beyond surface level — "
    "meaningful as Starbucks moves toward $3.0B in capex. His <b>Python proficiency</b> (Pandas, NumPy, "
    "scikit-learn) with demonstrated ML application — including a Customer Review Intelligence System "
    "using GPT-4o and RAG pipelines — places him above pure BI analysts. DBT, BigQuery, and Netezza "
    "exposure rounds out a functional modern data stack."
))

story.append(sub("Business and Analytical Strengths"))
story.append(p(
    "The most commercially significant item on Samuel's resume is the <b>churn forecasting work at "
    "Bass Pro Shops</b>: monthly models on 500K+ customer records, used operationally by loyalty and "
    "sales teams to target high-risk cohorts. This is not a research project — it was a production "
    "analytical workflow influencing weekly decisions. That is a material differentiator at his "
    "experience level. His competitive market analysis (visit frequency across competing markets "
    "for executive retention decisions) is directly analogous to how Starbucks thinks about comparable "
    "store sales defense. C-suite briefing experience at Bandwidth indicates comfort translating "
    "analytical findings into executive communication."
))

story.append(sub("Gaps and Limitations"))
for gap in [
    "<b>Scale gap:</b> Largest data environment was 500K records. Starbucks Rewards has tens of millions of active members.",
    "<b>Domain gap:</b> No food and beverage, CPG, or supply chain experience. Channel Development and commodity analytics are outside his range.",
    "<b>ML maturity gap:</b> ML work is prototype-level (Jupyter notebooks), not enterprise-deployed. The gap from modeling to production MLOps is real.",
    "<b>International gap:</b> No experience with multi-market data, foreign currency analytics, or cross-border licensed store economics.",
    "<b>Organizational scale gap:</b> Never navigated a matrixed, cross-functional organization at 381,000 employees.",
]:
    story.append(b(gap))
story.append(spacer(4))

story += rule()

# ── PART III ──────────────────────────────────────────────────────────────────
story.append(part_label("PART III"))
story.append(section("Mapping Samuel's Experience to Starbucks' Needs"))

mapping_rows = [
    ["Samuel's Capability", "Starbucks Business Need", "Confidence"],
    ["Churn forecasting on 500K+ loyalty records (Bass Pro)", "Starbucks Rewards member retention & reactivation modeling", "HIGH"],
    ["Store-level competitive market analysis", "Comp store sales analytics & market defense strategy", "HIGH"],
    ["15+ dashboards across 170+ retail locations", "Campaign/operations reporting across ~38K stores", "HIGH"],
    ["Customer segmentation: churn risk, purchase intent", "Rewards program personalization & targeted promotions", "HIGH"],
    ["Customer Review Intelligence System (1M+ reviews, GPT-4o + RAG)", "Customer feedback analytics, app review sentiment, personalization", "MEDIUM"],
    ["SQL/Snowflake/AWS/BigQuery data stack", "Enterprise data infrastructure alignment", "MEDIUM"],
    ["C-suite briefings at Bandwidth", "Executive-facing analytical communication", "MEDIUM"],
]
story.append(data_table(
    mapping_rows[0], mapping_rows[1:],
    col_widths=[W*0.36, W*0.42, W*0.14]
))
story.append(spacer(4))

story += rule()

# ── PART IV ───────────────────────────────────────────────────────────────────
story.append(PageBreak())
story.append(part_label("PART IV"))
story.append(section("Top 3 Role Paths and Contribution Areas"))

# ── PATH 1 ────────────────────────────────────────────────────────────────────
path1_header = Table([[
    Paragraph("PATH 1", style("P1L", fontName="Helvetica-Bold", fontSize=8,
              textColor=WHITE, leading=11, letterSpacing=1.5)),
    Paragraph("Customer Intelligence / Loyalty Analytics", style("P1T",
              fontName="Helvetica-Bold", fontSize=12,
              textColor=WHITE, leading=16)),
    Paragraph("HIGHEST CONFIDENCE", style("P1R", fontName="Helvetica-Bold",
              fontSize=7.5, textColor=SBUX_GOLD, leading=11, alignment=TA_LEFT)),
]], colWidths=[0.7*inch, W*0.6, W*0.28])
path1_header.setStyle(TableStyle([
    ("BACKGROUND",   (0,0), (-1,-1), SBUX_DARK),
    ("LEFTPADDING",  (0,0), (-1,-1), 12),
    ("RIGHTPADDING", (0,0), (-1,-1), 12),
    ("TOPPADDING",   (0,0), (-1,-1), 10),
    ("BOTTOMPADDING",(0,0), (-1,-1), 10),
    ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
]))
story.append(path1_header)
story.append(spacer(8))

story.append(p(
    "<b>Role:</b> Senior Analyst or Analyst II, Starbucks Rewards / Customer Intelligence"
))
story.append(p(
    "<b>Why it fits.</b> Samuel has run production churn forecasting on loyalty customer data at a "
    "multi-location retail company. Starbucks Rewards is the company's most strategically critical "
    "data asset and the primary driver of comparable store sales growth. The analytical problems are "
    "structurally identical: identify lapsing members, score purchase intent, segment by behavioral "
    "cohort, target reactivation campaigns."
))

path1_details = [
    ["DIMENSION", "DETAIL"],
    ["Business problems he solves",
     "Predictive churn modeling for Rewards members; cohort segmentation; reactivation campaign targeting; loyalty ROI measurement; Mobile Order & Pay behavioral analytics"],
    ["Collaboration", "Digital & Technology, Marketing, U.S. Store Operations, Rewards product team, Data Engineering"],
    ["Metrics he can move", "Rewards member 90-day retention rate · Reactivated lapsed member revenue · Frequency per active member · Transaction comp contribution from loyalty cohorts"],
    ["Short-term (0–12 mo)", "Rebuild/refine churn scoring models; build cohort dashboards for loyalty team; run A/B analysis on reactivation effectiveness"],
    ["Long-term (1–3 yr)", "Own the predictive modeling layer for member lifecycle management — directly informs marketing spend allocation and top-line transaction growth projections"],
]
story.append(data_table(path1_details[0], path1_details[1:], col_widths=[W*0.25, W*0.67]))
story.append(spacer(14))

# ── PATH 2 ────────────────────────────────────────────────────────────────────
path2_header = Table([[
    Paragraph("PATH 2", style("P2L", fontName="Helvetica-Bold", fontSize=8,
              textColor=WHITE, leading=11, letterSpacing=1.5)),
    Paragraph("Marketing Analytics / Campaign Performance", style("P2T",
              fontName="Helvetica-Bold", fontSize=12,
              textColor=WHITE, leading=16)),
    Paragraph("STRONG FIT", style("P2R", fontName="Helvetica-Bold",
              fontSize=7.5, textColor=SBUX_GOLD, leading=11, alignment=TA_LEFT)),
]], colWidths=[0.7*inch, W*0.6, W*0.28])
path2_header.setStyle(TableStyle([
    ("BACKGROUND",   (0,0), (-1,-1), SBUX_GREEN),
    ("LEFTPADDING",  (0,0), (-1,-1), 12),
    ("RIGHTPADDING", (0,0), (-1,-1), 12),
    ("TOPPADDING",   (0,0), (-1,-1), 10),
    ("BOTTOMPADDING",(0,0), (-1,-1), 10),
    ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
]))
story.append(path2_header)
story.append(spacer(8))

story.append(p("<b>Role:</b> Analyst, Marketing Analytics or Digital Marketing Performance"))
story.append(p(
    "<b>Why it fits.</b> Samuel's Bass Pro work included campaign performance measurement across "
    "170+ locations and 500K+ customers, with direct outputs to marketing and sales leadership. "
    "Starbucks runs highly sophisticated, data-driven promotional campaigns through Rewards, and "
    "measuring those campaigns — attribution, incrementality, ROI by promotion type — requires "
    "exactly his Tableau/Domo/SQL skill set."
))

path2_details = [
    ["DIMENSION", "DETAIL"],
    ["Business problems he solves",
     "Campaign lift measurement for Rewards promotions; spend optimization across digital and in-store channels; seasonal/LTO performance tracking; market-level comp sales attribution"],
    ["Collaboration", "Marketing, Digital Product, Loyalty Analytics, Finance (budget allocation inputs)"],
    ["Metrics he can move", "Incremental revenue per campaign dollar · Offer redemption rate by member segment · Mobile order attach rate for promoted items · Promotional margin contribution"],
    ["Short-term (0–12 mo)", "Build standardized campaign measurement dashboards; establish baseline attribution methodology for digital promotions"],
    ["Long-term (1–3 yr)", "Multi-touch attribution modeling and marketing mix optimization — an area where his ML foundations become directly relevant"],
]
story.append(data_table(path2_details[0], path2_details[1:], col_widths=[W*0.25, W*0.67]))
story.append(spacer(14))

# ── PATH 3 ────────────────────────────────────────────────────────────────────
path3_header = Table([[
    Paragraph("PATH 3", style("P3L", fontName="Helvetica-Bold", fontSize=8,
              textColor=SBUX_DARK, leading=11, letterSpacing=1.5)),
    Paragraph("Digital & Technology — Product Analytics", style("P3T",
              fontName="Helvetica-Bold", fontSize=12,
              textColor=SBUX_DARK, leading=16)),
    Paragraph("VIABLE / HIGH CEILING", style("P3R", fontName="Helvetica-Bold",
              fontSize=7.5, textColor=SBUX_GREEN, leading=11, alignment=TA_LEFT)),
]], colWidths=[0.7*inch, W*0.6, W*0.28])
path3_header.setStyle(TableStyle([
    ("BACKGROUND",   (0,0), (-1,-1), SBUX_GOLD),
    ("LEFTPADDING",  (0,0), (-1,-1), 12),
    ("RIGHTPADDING", (0,0), (-1,-1), 12),
    ("TOPPADDING",   (0,0), (-1,-1), 10),
    ("BOTTOMPADDING",(0,0), (-1,-1), 10),
    ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
]))
story.append(path3_header)
story.append(spacer(8))

story.append(p("<b>Role:</b> Product Analyst, Mobile / Digital Platform"))
story.append(p(
    "<b>Why it fits.</b> Starbucks' $140M+ technology investment in FY23 and rising capex signal "
    "serious internal digital product investment. Mobile Order &amp; Pay is a growing share of "
    "transactions. Samuel's Python, AWS, and LLM project experience put him at the boundary between "
    "pure analytics and technical product roles — unusual for his years of experience. DBT and BigQuery "
    "familiarity make him viable in a product analytics context. <b>This path has the highest long-term "
    "ceiling but the longest ramp.</b>"
))

path3_details = [
    ["DIMENSION", "DETAIL"],
    ["Business problems he solves",
     "Funnel analysis for Mobile Order & Pay conversion; feature adoption measurement across app updates; A/B test analysis; customer sentiment from app reviews (directly applicable from NLP projects)"],
    ["Collaboration", "Digital Product, Engineering, UX Research, Loyalty Analytics"],
    ["Metrics he can move", "Mobile Order & Pay attach rate · App engagement retention · Feature adoption rates · Mobile transaction frequency per active user"],
    ["Short-term (0–12 mo)", "Dashboard infrastructure for product KPIs; funnel analysis and drop-off identification; app review sentiment monitoring"],
    ["Long-term (1–3 yr)", "As Starbucks deepens digital investment, analysts with ML and cloud depth move into senior data science or analytics engineering — Samuel's ceiling here is higher than any other path"],
]
story.append(data_table(path3_details[0], path3_details[1:], col_widths=[W*0.25, W*0.67]))

story += rule()

# ── PART V ────────────────────────────────────────────────────────────────────
story.append(PageBreak())
story.append(part_label("PART V"))
story.append(section("Immediate Strengths vs. Development Areas"))

two_col_data = [[
    # Left column
    Table([[
        Paragraph("CAN DO ON DAY ONE", style("D1H",
            fontName="Helvetica-Bold", fontSize=8.5,
            textColor=SBUX_GREEN, leading=12, letterSpacing=1)),
    ]] + [[b(item)] for item in [
        "Build and maintain dashboard infrastructure (Tableau, Domo, similar) — production-validated at scale",
        "Write SQL against large customer datasets in Snowflake or BigQuery — no instruction required",
        "Run churn risk models on loyalty customer data using Python — methodology already established",
        "Produce executive-ready analytical summaries from complex datasets",
        "Customer segmentation and cohort analysis",
        "Contribute to reporting infrastructure from week 2",
    ]], colWidths=[(W/2)-8]),

    # Right column
    Table([[
        Paragraph("REQUIRES DEVELOPMENT", style("D2H",
            fontName="Helvetica-Bold", fontSize=8.5,
            textColor=HexColor("#C53030"), leading=12, letterSpacing=1)),
    ]] + [[b(item)] for item in [
        "Starbucks-specific data environment: Rewards schema, MOP data architecture, enterprise governance",
        "Food & beverage economics — contextualizing store-level margin drivers",
        "Production ML deployment (MLOps) — currently at prototype layer; needs data engineering partnership",
        "Organizational navigation in a 381K-person matrixed company",
        "International & channel analytics — Nestlé partnership, licensed store economics, FX",
    ]], colWidths=[(W/2)-8]),
]]
two_col = Table(two_col_data, colWidths=[(W/2)-4, (W/2)-4], hAlign="LEFT")
two_col.setStyle(TableStyle([
    ("LEFTPADDING",  (0,0), (-1,-1), 4),
    ("RIGHTPADDING", (0,0), (-1,-1), 4),
    ("VALIGN",       (0,0), (-1,-1), "TOP"),
]))
story.append(two_col)
story += rule()

# ── PART VI ───────────────────────────────────────────────────────────────────
story.append(part_label("PART VI"))
story.append(section("Most Compelling Value Proposition to Starbucks"))
story.append(gold_box(
    "Samuel He's most compelling value to Starbucks is narrow but genuinely differentiated: "
    "he is one of the few candidates at his experience level who has built and operated "
    "PRODUCTION churn forecasting models on loyalty customer data at multi-location retail scale, "
    "using the exact technical stack — SQL, Snowflake, Python, Tableau, AWS — that Starbucks' "
    "analytics infrastructure requires. In a competitive landscape where Starbucks Rewards is both "
    "the company's highest-priority digital asset and its primary lever for comparable store sales "
    "growth, the ability to reduce member lapse rates and improve reactivation ROI through predictive "
    "modeling is not a future capability to be developed — it is a current operational need. "
    "Samuel does not need to be trained on the problem type. He needs to be trained on Starbucks' "
    "data. That distinction matters when ramp time is a real cost."
))
story.append(spacer(8))
story += rule()

# ── PART VII ──────────────────────────────────────────────────────────────────
story.append(part_label("PART VII"))
story.append(section("Best Narrative for Interviews"))

story.append(callout_box(
    '"I build analytical systems that help loyalty and operations teams make faster, better decisions '
    'about customers — and I\'ve done it at scale in production."'
))
story.append(spacer(8))

story.append(p(
    "Samuel should <b>lead with the Bass Pro churn forecasting work</b> — not the technical details, "
    "but the business outcome: retention-focused teams using his models weekly to prioritize outreach, "
    "with measurable ROI improvement. He should frame his transition to Starbucks not as a change of "
    "industry but as a continuation of the same problem set in a more sophisticated environment."
))
story.append(p(
    "He should <b>proactively reference Starbucks Rewards and Mobile Order &amp; Pay</b> in the "
    "conversation — demonstrating business understanding before being asked. His NLP and LLM projects "
    "are useful supporting evidence of ceiling, but should not be the lead — they read more academic "
    "than operational to most hiring managers."
))
story.append(sub("What to Avoid"))
for item in [
    "Overstating ML experience as production-ready at enterprise scale",
    "Claiming fluency in supply chain, channel economics, or international markets",
    "Presenting as a senior hire — his story is strongest when honest about scope",
    "Leading with the chess master achievement unprompted (use it only if aptitude comes up)",
]:
    story.append(b(item))
story.append(spacer(4))
story += rule()

# ── PART VIII ─────────────────────────────────────────────────────────────────
story.append(PageBreak())
story.append(part_label("PART VIII"))
story.append(section("Potential Weaknesses or Objections — and How to Address Them"))

objections = [
    [
        '"You\'ve never worked in food & beverage. How will you understand the business fast enough?"',
        "The objection conflates domain knowledge with analytical transferability. Churn modeling and segmentation are domain-agnostic at the methodology level. Business context — menu engineering, beverage attach rates, daypart behavior — is learnable. The analytical framework he brings is already validated. Bass Pro's retail customer data environment is structurally more similar to Starbucks than it is different."
    ],
    [
        '"You\'ve worked at mid-sized companies. Starbucks operates at a completely different scale."',
        "The scale gap is real and should be acknowledged directly rather than deflected. Honest answer: he has demonstrated the right methodology at smaller scale and has the technical infrastructure knowledge (Snowflake, AWS, BigQuery) to operate at enterprise scale. His AWS certifications are concrete evidence of preparation. The modeling logic does not change at scale; the data environment does."
    ],
    [
        '"You\'ve been at multiple companies in a short time. What\'s the retention risk?"',
        "His timeline is coherent: Bandwidth (~1 year, early-career generalist BI role), Bass Pro (~2 years, more senior). Neither departure signals disengagement. His current Redmond location — in Starbucks' technology hub — is a meaningful stability signal and reflects deliberate positioning, not opportunistic drifting."
    ],
    [
        '"Your ML work appears project-based, not enterprise production. Can you actually deploy models at scale?"',
        "This is the strongest objection and should be addressed with calibration rather than defensiveness. Acknowledge that his ML experience is at the modeling and prototyping layer, not full MLOps deployment, and position as someone who builds models that data engineering teams operationalize. At Starbucks, loyalty analysts typically partner with data engineers for deployment — solo ML engineering is not the expectation at this level."
    ],
    [
        '"Our Rewards program is far more complex than anything you\'ve worked with. How long before you\'re actually productive?"',
        "Samuel's productivity floor is higher than a generalist's because his dashboard and SQL skills are immediately deployable. He can contribute to reporting and exploratory analysis from week two while ramping on the Rewards data model. Realistic timeline: 60–90 days to meaningful analytical contribution, 6 months to independent modeling work."
    ],
    [
        '"You\'ve worked across multiple geographies. Can you operate in our in-person collaboration environment?"',
        "Samuel is currently located in Redmond, WA — directly in the Starbucks technology team's geography. Geographic co-location is not a risk; it is an asset. His prior locations were job-dependent; his current location reflects deliberate positioning for this market."
    ],
]

for i, (obj, rebuttal) in enumerate(objections, 1):
    obj_block = Table([[
        Paragraph(f"OBJECTION {i}", style(f"ObjN{i}",
            fontName="Helvetica-Bold", fontSize=7.5,
            textColor=SBUX_GOLD, leading=10, letterSpacing=1.5)),
        Paragraph(obj, style(f"ObjT{i}",
            fontName="Helvetica-Oblique", fontSize=9,
            textColor=WHITE, leading=14)),
    ]], colWidths=[0.85*inch, W - 0.85*inch])
    obj_block.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), SBUX_DARK),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING",   (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
    ]))
    rebuttal_block = Table([[
        Paragraph("RESPONSE", style(f"RbL{i}",
            fontName="Helvetica-Bold", fontSize=7.5,
            textColor=SBUX_GREEN, leading=10, letterSpacing=1.5)),
        Paragraph(rebuttal, style(f"RbT{i}",
            fontName="Helvetica", fontSize=9,
            textColor=SLATE, leading=14)),
    ]], colWidths=[0.85*inch, W - 0.85*inch])
    rebuttal_block.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), HIGHLIGHT_BG),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING",   (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
    ]))
    story.append(KeepTogether([obj_block, rebuttal_block, spacer(10)]))

story += rule()

# ── PART IX ───────────────────────────────────────────────────────────────────
story.append(part_label("PART IX"))
story.append(section("Corporate Role Type Ranking — Best to Worst Fit"))

rank_data = [
    ["RANK", "ROLE TYPE", "FIT", "RATIONALE"],
    ["#1", "Customer Intelligence / Loyalty Analytics", "★★★★★",
     "Highest-confidence fit. Production churn modeling on loyalty data at multi-location retail is exactly what Starbucks Rewards needs. Day-one relevant capability with fastest ROI."],
    ["#2", "Marketing Analytics / Campaign Performance", "★★★★☆",
     "Strong fit grounded in Bass Pro campaign measurement. Primary limitation: sits slightly further from the core loyalty modeling layer where his differentiation is strongest. Fast ramp."],
    ["#3", "Digital & Technology (Product Analytics)", "★★★☆☆",
     "Viable with highest long-term ceiling. Python, AWS, LLM experience differentiates from pure BI analysts, but production product analytics at Starbucks' digital scale is a stretch from his current level. Recommended as internal move after 2–3 years."],
    ["#4", "Finance / FP&A Analytics", "★★☆☆☆",
     "Limited fit. Math+Finance degree provides numeracy, but his career has been entirely on the commercial analytics side, not P&L modeling or multi-segment financial planning. Requires more retraining than the value warrants."],
    ["#5", "Supply Chain & Operations Analytics", "★☆☆☆☆",
     "Weakest fit. No experience in demand forecasting, commodity management, or logistics optimization. Placing him here wastes his actual strengths and mismatches him against genuine domain expertise requirements."],
]
story.append(data_table(
    rank_data[0], rank_data[1:],
    col_widths=[0.42*inch, W*0.27, 0.65*inch, W*0.48]
))
story.append(spacer(16))

# ── FOOTER ────────────────────────────────────────────────────────────────────
story.append(HRFlowable(width="100%", thickness=1, color=SBUX_GREEN, spaceAfter=6))
story.append(Paragraph(
    "This memo is based solely on publicly reported FY2023 Starbucks financial data (10-K) "
    "and the resume information provided. Assessments reflect the analytical mapping of those "
    "data sources and do not incorporate primary research or interviews. "
    "Prepared March 2026.",
    style("Footer", fontName="Helvetica-Oblique", fontSize=7.5,
          textColor=HexColor("#718096"), leading=11, alignment=TA_CENTER)
))


# ── BUILD PDF ─────────────────────────────────────────────────────────────────
def on_page(canvas, doc):
    """Add page number footer on every page except the first."""
    page_num = doc.page
    if page_num > 1:
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(HexColor("#718096"))
        canvas.drawString(0.85*inch, 0.55*inch, "CONFIDENTIAL — TALENT STRATEGY MEMO")
        canvas.drawRightString(letter[0] - 0.85*inch, 0.55*inch, f"Page {page_num}")
        canvas.restoreState()

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF saved to: {OUTPUT_PATH}")
