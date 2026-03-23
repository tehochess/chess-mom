"""
Starbucks FY23 Annual Report -- Smart Word Cloud Generator
===========================================================
PURPOSE: Help a non-technical reader quickly identify the most
important terms, concepts, and financial vocabulary they need to
learn to fully understand the investor report.

Color legend in the word cloud:
  Dark green  = appears most frequently (top 10 terms)
  Medium green = top 30 terms
  Gold         = top 60 terms
  Grey-teal    = lower frequency but still meaningful
"""

import re
import sys
from collections import Counter

import matplotlib.pyplot as plt
import wordninja
from nltk.corpus import stopwords
from pdfminer.high_level import extract_text
from wordcloud import WordCloud

# ── 1. EXTRACT TEXT (pdfminer handles spacing much better than pdfplumber) ───
PDF_PATH = "C:/Users/hesam/project/fy23-annual-report.pdf"

print("Extracting text from PDF (this may take ~15 seconds)...")
full_text = extract_text(PDF_PATH)
print(f"  Extracted {len(full_text):,} characters.")


# ── 2. SPLIT RUN-TOGETHER WORDS, THEN TOKENIZE ───────────────────────────────
# Some PDF encodings merge words; wordninja splits them intelligently
print("Tokenizing and segmenting words...")

raw_tokens = re.findall(r"[a-zA-Z]{3,}", full_text.lower())

# For any "word" that looks like a run-together blob (>18 chars), segment it
final_tokens = []
for tok in raw_tokens:
    if len(tok) > 18:
        final_tokens.extend(wordninja.split(tok))
    else:
        final_tokens.append(tok)

# Keep only proper alphabetic tokens 4+ characters long
final_tokens = [t for t in final_tokens if re.match(r'^[a-z]{4,}$', t)]
print(f"  Total tokens after segmentation: {len(final_tokens):,}")


# ── 3. STOPWORD LAYERS ────────────────────────────────────────────────────────

# Layer 1: standard English
nltk_stops = set(stopwords.words("english"))

# Layer 2: SEC/legal boilerplate (sounds important but tells you nothing)
legal_boilerplate = {
    "pursuant","herein","thereof","hereby","whereby","whereas","therein",
    "therefor","thereto","hereof","hereto","hereunder","thereunder",
    "notwithstanding","aforesaid","aforementioned","shall","thereof",
    "include","included","includes","including","well","provide","provides",
    "provided","providing","related","result","results","resulted","resulting",
    "certain","various","generally","primarily","partially","further","upon",
    "within","without","whether","among","such","used","based","following",
    "fiscal","year","ended","noted","described","discussed","pursuant",
    "during","period","quarter","annual","report","form","item","note",
    "notes","refer","approximately","compared","comparison","increase",
    "increases","increased","increasing","decrease","decreases","decreased",
    "decreasing","respectively","total","billion","million","thousand",
    "percentage","percent","basis","points","applicable","associated",
    "addition","additional","impact","impacts","higher","lower","greater",
    "less","significant","significantly","continue","continued","continues",
    "continuing","current","currently","prior","previous","previously",
    "future","expected","expect","expects","ability","believe","believes",
    "believed","could","would","should","will","make","makes","made",
    "making","take","taken","takes","taking","give","given","gives","also",
    "become","becomes","became","allow","allows","allowed","allowing",
    "represent","represents","represented","representing","reflect",
    "reflects","reflected","reflecting","consider","considered","require",
    "requires","required","requiring","support","supports","supported",
    "supporting","manage","manages","managed","managing","drive","drives",
    "driven","driving","improve","improves","improved","improving",
    "maintain","maintains","maintained","maintaining","achieve","achieves",
    "achieved","achieving","address","addresses","addressed","addressing",
    "assess","assesses","assessed","assessing","establish","establishes",
    "established","establishing","implement","implements","implemented",
    "implementing","operate","operates","operated","operation","operations",
    "multiple","number","numbers","amount","amounts","level","levels",
    "portion","portions","range","ranges","type","types","manner","nature",
    "extent","degree","terms","conditions","factors","factor","values",
    "ways","times","dates","periods","begin","begins","began","beginning",
    "sets","setting","puts","held","hold","holds","holding","place","places",
    "placed","placing","orders","ordered","ordering","opens","opened",
    "opening","closes","closed","closing","transfer","transfers","transferred",
    "effective","effectively","efficient","efficiently","financial",
    "financially","operational","operationally","strategic","strategically",
    "overall","largely","mainly","particularly","especially","specifically",
    "typically","usually","often","sometimes","always","never","still",
    "already","come","comes","came","back","full","right","left","real",
    "true","able","like","know","think","look","want","need","works",
    "worked","working","apply","applies","applied","applying","adds",
    "added","adding","pays","paid","paying","sells","sold","selling",
    "buys","bought","buying","earns","earned","earning","returns",
    "returned","returning","grows","grew","grown","growing","expands",
    "expanded","expanding","item","items","value","ways","time","date",
    "open","order","close","transfer","activity","activities",
}

# Layer 3: too-generic business words (not specific enough to learn)
generic_biz = {
    "business","businesses","company","companies","organization",
    "organizations","management","manager","managers","executive",
    "executives","officer","officers","director","directors","president",
    "vice","senior","chief","global","world","worldwide","market",
    "markets","marketing","industry","industries","sector","sectors",
    "service","services","product","products","customer","customers",
    "consumer","consumers","partner","partners","investor","investors",
    "shareholder","shareholders","employee","employees","team","teams",
    "group","groups","segment","segments","region","regions","area",
    "areas","location","locations","store","stores","site","sites",
    "office","offices","initiative","initiatives","strategy","strategies",
    "plan","plans","program","programs","process","processes","system",
    "systems","platform","platforms","solution","solutions","model",
    "models","approach","approaches","method","methods","practice",
    "practices","policy","policies","standard","standards","objective",
    "objectives","goal","goals","target","targets","performance",
    "investment","investments","cost","costs","expense","expenses",
    "revenue","revenues","income","loss","losses","profit","profits",
    "margin","margins","rate","rates","price","prices","pricing",
    "ratio","ratios","index","indices","measure","measures","metric",
    "metrics","indicator","indicators","data","information","report",
    "reports","statement","statements","disclosure","disclosures",
    "accounting","audit","auditor","auditors","review","reviews",
    "assessment","assessments","evaluation","evaluations","analysis",
    "analyses","estimate","estimates","projection","projections",
    "forecast","forecasts","outlook","guidance","risk","risks",
    "opportunity","opportunities","challenge","challenges","issue",
    "issues","matter","matters","event","events","condition","conditions",
    "circumstance","circumstances","environment","environments",
    "situation","situations","development","developments","think",
    "know","look","want","need","work","sell","buy","earn","return",
    "grow","expand","need","make","take","give","come","become",
    "allow","support","manage","drive","improve","maintain","achieve",
    "address","assess","establish","implement","operate",
}

ALL_STOPS = nltk_stops | legal_boilerplate | generic_biz


# ── 4. LOAD ENGLISH DICTIONARY FOR CLEAN-WORD FILTER ─────────────────────────
import nltk
from nltk.corpus import words as nltk_words

english_vocab = set(w.lower() for w in nltk_words.words())

# Add domain-specific financial/business terms not in NLTK's word list
domain_terms = {
    "arabica","teavana","frappuccino","starbucks","nasdaq","sofr","ebitda",
    "amortization","depreciation","impairment","goodwill","intangible",
    "royalty","royalties","dividends","derivative","derivatives","hedging",
    "collateral","covenant","covenants","indenture","liquidity","solvency",
    "dilution","diluted","deferred","consolidated","consolidation",
    "refranchise","comparable","comps","throughput","licensees","licensee",
    "noncontrolling","revolving","unsecured","maturity","matures","issuance",
    "treasury","benchmark","restructuring","impairments","securities",
    "reinvention","channel","alliance","frappuccinos","sustainability",
    "cafepractices","roaster","roasting","sourcing","ethical","ethically",
    "inflation","inflationary","commodity","commodities","arabica",
    "espresso","beverage","beverages","barista","baristas","latte",
    "cappuccino","macchiato","americano","nitro","cold","brew",
    "unionization","workforce","headcount","retention","turnover",
    "omnichannel","ecommerce","digital","mobile","loyalty","rewards",
    "transaction","transactions","ticket","throughput","comparable",
    "capex","opex","ebit","gross","operating","fiscal","quarterly",
}
english_vocab.update(domain_terms)

# OCR artifact patterns to reject
OCR_PATTERNS = re.compile(
    r'(.)\1{2,}'                  # 3+ repeated chars: "rrr", "fff"
    r'|[hj][a-z]{1,2}$'          # short garbled prefixes
    r'|^(hthe|affeff|effeff|andd|lity|suppl|suppor|subju|offiff|availabla|liabia|starbuc|aabl|aaabl)$'
)

# ── 5. FILTER & COUNT ─────────────────────────────────────────────────────────
# Also add noise words explicitly to stopwords
extra_noise = {
    # OCR leftovers
    "hthe","effeff","affeff","andd","lity","suppl","availabla",
    "liabia","starbuc","suppor","subju","offiff","aabl",
    # boilerplate / dates / pure function words
    "october","november","march","january","february","april","june",
    "july","august","september","december",
    "corporation","exhibit","laws","using","long","changes","part",
    "common","general","north","third","recognized","reporting",
    "recorded","estimated","millions","flows","outstanding","obligations",
    "regulations","material","instruments","change","years","sale",
    "balance","shares","share","corporate","brand","gains","taxes",
    "food","purchase","america","starbucks","section","many","high",
    "fixed","international","growth","quality","experience","retail",
    "internal","potential","comprehensive","adversely","adverse",
    "compliance","administrative","determine","local","party","economic",
    "registrant","control","operating","term","fair",
}
ALL_STOPS.update(extra_noise)

meaningful = [
    t for t in final_tokens
    if t not in ALL_STOPS
    and t in english_vocab              # must be a real English/domain word
    and not OCR_PATTERNS.search(t)      # no OCR artifacts
    and len(t) >= 4
]

freq = Counter(meaningful)

# Keep only terms appearing 4+ times (removes OCR noise / hapax legomena)
freq = Counter({w: c for w, c in freq.items() if c >= 4})

top_terms = freq.most_common(120)
print(f"  Meaningful unique terms (freq >= 4): {len(freq):,}")


# ── 5. PRINT FREQUENCY TABLE WITH PLAIN-ENGLISH HINTS ────────────────────────
term_hints = {
    # Financial mechanics
    "diluted":        "EPS = earnings per share (all possible shares counted)",
    "comparable":     "same-store sales vs prior year (key growth signal)",
    "amortization":   "spreading intangible asset cost over time (e.g. brand value)",
    "depreciation":   "spreading physical asset cost over time (e.g. equipment)",
    "equity":         "ownership stake or net worth of the company",
    "royalty":        "fee paid to Starbucks for using its brand/trademark",
    "liquidity":      "ability to cover short-term obligations with cash",
    "hedging":        "locking in prices via contracts to reduce risk",
    "commodity":      "raw material priced by the market (coffee, dairy, etc.)",
    "impairment":     "writing down an asset's value when it declines",
    "capital":        "long-term money invested in the business",
    "lease":          "contract to use property/equipment for regular payments",
    "liability":      "debt or financial obligation owed by the company",
    "covenant":       "restriction or promise in a loan agreement",
    "dividend":       "cash paid to shareholders from profits",
    "dividends":      "cash payments distributed to shareholders",
    "repurchase":     "company buying back its own stock from the market",
    "deferred":       "delayed or postponed (e.g. deferred tax liability)",
    "intangible":     "non-physical asset: brand name, patents, goodwill",
    "goodwill":       "premium paid above fair value when acquiring a business",
    "derivative":     "financial contract whose value tracks another asset/price",
    "inflation":      "economy-wide price increases raising operating costs",
    "dilution":       "reduction in share value from issuing new shares",
    "collateral":     "asset pledged as security for a loan",
    "principal":      "original loan amount before interest",
    "maturity":       "date when a debt must be fully repaid",
    "unsecured":      "debt not backed by a specific pledged asset",
    "revolving":      "credit line you can borrow, repay, and borrow again",
    "commercial":     "commercial paper = short-term corporate borrowing tool",
    "noncontrolling": "minority ownership interest in a subsidiary",
    "refranchise":    "converting company-owned stores to licensed stores",
    "consolidate":    "combining financials of all subsidiaries into one",
    "recognition":    "when revenue/expense is officially recorded",
    "benchmark":      "reference interest rate (e.g. SOFR) for loan pricing",
    # Business model
    "arabica":        "high-quality coffee bean variety used by Starbucks",
    "licensed":       "stores run by third-party operators under Starbucks brand",
    "transaction":    "individual customer purchase count",
    "ticket":         "average dollar spend per customer visit",
    "throughput":     "how fast customers are served (key efficiency metric)",
    "reinvention":    "Starbucks' internal transformation plan (2022-2024)",
    "alliance":       "partnership -- here: Global Coffee Alliance with Nestle",
    "teavana":        "Starbucks tea brand (sold in stores)",
    "frappuccino":    "Starbucks signature blended cold coffee drink (trademark)",
    "loyalty":        "Starbucks Rewards -- points program driving repeat visits",
    "mobile":         "mobile app ordering -- huge driver of digital sales",
    "digital":        "app, online, and tech-driven customer experience",
    "supply":         "supply chain -- logistics of getting goods to stores",
    "venture":        "joint venture = shared business ownership with a partner",
    "channel":        "Channel Development = packaged goods / grocery sales",
    "roaster":        "Starbucks roasts its own coffee beans (key differentiator)",
    "ethically":      "coffee sourced via C.A.F.E. Practices (ethics/sustainability)",
    "tariff":         "government tax on imported goods (e.g. coffee beans)",
    "currency":       "foreign exchange rate exposure from global operations",
    "fiscal":         "fiscal year = Starbucks' Oct-to-Oct accounting calendar",
    "exchange":       "stock exchange or foreign currency exchange",
    "securities":     "financial instruments: stocks, bonds, notes",
    "issuance":       "new debt or stock being officially released/sold",
    "indenture":      "formal bond/debt contract outlining obligations",
    "covenant":       "contractual restriction in a debt agreement",
    "matures":        "when a debt instrument reaches its repayment date",
    "treasury":       "U.S. government bonds (safe investment) or stock buybacks",
    "sofr":           "Secured Overnight Financing Rate -- benchmark lending rate",
    "wacc":           "Weighted Average Cost of Capital (hurdle rate)",
    "ebitda":         "Earnings Before Interest, Tax, Depreciation, Amortization",
    "restructuring":  "costs of reorganizing / closing underperforming parts",
}

print(f"\n{'='*60}")
print(f"  TOP TERMS TO LEARN FROM THE STARBUCKS FY23 REPORT")
print(f"{'='*60}")
print(f"  {'RANK':<5} {'TERM':<26} {'COUNT':>6}   MEANING")
print(f"{'='*60}")

for rank, (word, count) in enumerate(top_terms[:80], 1):
    hint = term_hints.get(word, "")
    hint_display = f"= {hint}" if hint else ""
    print(f"  {rank:<5} {word:<26} {count:>5}x   {hint_display}")

print(f"\n{'='*60}\n")


# ── 6. GENERATE WORD CLOUD ────────────────────────────────────────────────────
print("Generating word cloud image...")

wc_freq = dict(freq.most_common(150))

# Starbucks brand palette
SBUX_DARK   = "#1E3932"   # deep forest green
SBUX_GREEN  = "#00704A"   # Starbucks green
SBUX_GOLD   = "#CBA258"   # warm gold
SBUX_GREY   = "#7A8C87"   # muted teal-grey
SBUX_CREAM  = "#F2F0EB"   # off-white background

sorted_counts = sorted(wc_freq.values(), reverse=True)
top10_threshold  = sorted_counts[min(9,  len(sorted_counts)-1)]
top30_threshold  = sorted_counts[min(29, len(sorted_counts)-1)]
top60_threshold  = sorted_counts[min(59, len(sorted_counts)-1)]

def starbucks_color(word, font_size, position, orientation,
                    random_state=None, **kwargs):
    count = wc_freq.get(word, 0)
    if count >= top10_threshold:
        return SBUX_DARK
    elif count >= top30_threshold:
        return SBUX_GREEN
    elif count >= top60_threshold:
        return SBUX_GOLD
    else:
        return SBUX_GREY

wc = WordCloud(
    width=1800,
    height=1000,
    background_color=SBUX_CREAM,
    max_words=150,
    color_func=starbucks_color,
    prefer_horizontal=0.72,
    min_font_size=11,
    max_font_size=180,
    collocations=False,
    relative_scaling=0.55,
    margin=10,
    random_state=42,
)
wc.generate_from_frequencies(wc_freq)

fig, ax = plt.subplots(figsize=(18, 10))
ax.imshow(wc, interpolation="bilinear")
ax.axis("off")
fig.patch.set_facecolor(SBUX_CREAM)

plt.suptitle(
    "Starbucks FY2023 Annual Report  --  Key Terms to Know",
    fontsize=16, fontweight="bold", color=SBUX_DARK, y=0.97,
)
plt.title(
    "Dark green = most frequent  |  Medium green = common  |  Gold = notable  |  Grey = lower frequency",
    fontsize=10, color=SBUX_GREEN, pad=4,
)

plt.tight_layout(rect=[0, 0, 1, 0.95])

output_path = "C:/Users/hesam/project/starbucks_wordcloud.png"
plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=SBUX_CREAM)
plt.close()

print(f"  Saved to: {output_path}")
print("\nDone! Open starbucks_wordcloud.png to see your learning map.")
