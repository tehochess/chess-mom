"""
Starbucks Drink Matcher
=======================
Run with:  streamlit run starbucks_matcher_app.py
"""

import csv
import os
import streamlit as st

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Starbucks Drink Matcher",
    page_icon="☕",
    layout="centered",
)

# ── STYLING ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── global ── */
html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }

/* ── header ── */
.main-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #1E3932;
    margin-bottom: 0;
}
.sub-title {
    font-size: 1rem;
    color: #00704A;
    margin-top: 0.2rem;
    margin-bottom: 1.4rem;
}

/* ── attribute block ── */
.attr-label {
    font-weight: 700;
    font-size: 0.95rem;
    color: #1E3932;
    margin-bottom: 0.15rem;
}
.attr-hint {
    font-size: 0.78rem;
    color: #6b7280;
    margin-bottom: 0.5rem;
}

/* ── result card ── */
.result-card {
    background: #f7f5f0;
    border-left: 5px solid #00704A;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1.2rem;
}
.result-card.silver {
    border-left-color: #CBA258;
}
.drink-name {
    font-size: 1.3rem;
    font-weight: 800;
    color: #1E3932;
    margin-bottom: 0.2rem;
}
.drink-desc {
    font-size: 0.88rem;
    color: #4a5568;
    margin-bottom: 0.8rem;
    font-style: italic;
}
.match-pct {
    font-size: 2rem;
    font-weight: 900;
    color: #00704A;
}
.match-pct.silver { color: #CBA258; }
.match-label {
    font-size: 0.75rem;
    color: #9ca3af;
    margin-top: 0.15rem;
}
.profile-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-top: 0.8rem;
}
.attr-chip {
    background: #e8f5ee;
    border-radius: 20px;
    padding: 0.25rem 0.65rem;
    font-size: 0.78rem;
    color: #1E3932;
    font-weight: 600;
}
.divider { border-top: 1px solid #e5e7eb; margin: 1.5rem 0; }
.section-header {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1E3932;
    margin-bottom: 0.6rem;
}
</style>
""", unsafe_allow_html=True)

# ── DATA LOADING ──────────────────────────────────────────────────────────────
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "starbucks_drinks_10_attribute_profiles.csv")

ATTRIBUTES = [
    ("Sweetness",         "How sweet do you want it? (1 = barely sweet, 5 = very sweet)"),
    ("Caffeine",          "How much of a caffeine kick? (1 = none, 5 = strong)"),
    ("Hotness",           "Do you want it hot? (1 = not at all, 5 = piping hot)"),
    ("Creaminess",        "How creamy and milky? (1 = light, 5 = rich and creamy)"),
    ("Coffee Intensity",  "How bold should the coffee flavor be? (1 = mild, 5 = intense)"),
    ("Chocolate Flavor",  "Do you want a chocolatey taste? (1 = none, 5 = strong)"),
    ("Fruit Flavor",      "Any fruity notes? (1 = none, 5 = very fruity)"),
    ("Spice / Floral",    "Spice or floral flavors like lavender/cinnamon? (1 = none, 5 = strong)"),
    ("Coldness",          "How cold and iced do you want it? (1 = not at all, 5 = very cold/icy)"),
    ("Dessert Richness",  "Should it feel like a dessert? (1 = light, 5 = very indulgent)"),
]

@st.cache_data
def load_drinks(path):
    drinks = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                profile = [
                    int(row["Sweetness (1-5)"]),
                    int(row["Caffeine (1-5)"]),
                    int(row["Hotness (1-5)"]),
                    int(row["Creaminess (1-5)"]),
                    int(row["Coffee Intensity (1-5)"]),
                    int(row["Chocolate Flavor (1-5)"]),
                    int(row["Fruit Flavor (1-5)"]),
                    int(row["Spice / Floral (1-5)"]),
                    int(row["Coldness (1-5)"]),
                    int(row["Dessert Richness (1-5)"]),
                ]
                drinks.append({
                    "name":        row["Drink Name"].strip(),
                    "description": row["Basic Description"].strip(),
                    "category":    row["Category"].strip(),
                    "profile":     profile,
                })
            except (ValueError, KeyError):
                continue
    return drinks

drinks = load_drinks(CSV_PATH)

# ── MATCHING LOGIC ────────────────────────────────────────────────────────────
def match_drinks(user_ratings, drinks):
    """
    Distance = sum of absolute differences across all 10 attributes.
    Max possible distance = 10 attributes × 4 (scale 1–5) = 40.
    Match % = (1 - distance / 40) × 100, clipped to [0, 100].
    """
    MAX_DIST = 40.0
    results = []
    for drink in drinks:
        dist = sum(abs(u - d) for u, d in zip(user_ratings, drink["profile"]))
        pct  = max(0.0, (1 - dist / MAX_DIST) * 100)
        results.append({**drink, "distance": dist, "match_pct": pct})
    results.sort(key=lambda x: x["distance"])
    return results

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">☕ Starbucks Drink Matcher</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">Rate what you\'re in the mood for — we\'ll find your best match '
    'from 88 Starbucks drinks.</p>',
    unsafe_allow_html=True,
)

st.info(
    "**How it works:** Rate each flavor dimension from **1** (not important / none) "
    "to **5** (very important / a lot). Hit **Find My Drink** when you're done.",
    icon="ℹ️",
)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── ATTRIBUTE SLIDERS ─────────────────────────────────────────────────────────
st.markdown('<p class="section-header">Your Flavor Profile</p>', unsafe_allow_html=True)

EMOJIS = ["🍬", "⚡", "🌡️", "🥛", "☕", "🍫", "🍓", "🌸", "🧊", "🍰"]

user_ratings = []

# 2-column layout for the 10 sliders
col_pairs = [st.columns(2) for _ in range(5)]

for i, ((attr, hint), emoji) in enumerate(zip(ATTRIBUTES, EMOJIS)):
    col = col_pairs[i // 2][i % 2]
    with col:
        st.markdown(f'<p class="attr-label">{emoji} {attr}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="attr-hint">{hint}</p>', unsafe_allow_html=True)
        val = st.select_slider(
            label=attr,
            options=[1, 2, 3, 4, 5],
            value=3,
            label_visibility="collapsed",
            key=f"slider_{i}",
        )
        user_ratings.append(val)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── LIVE PREVIEW BAR ──────────────────────────────────────────────────────────
with st.expander("👁️ See your current profile", expanded=False):
    profile_cols = st.columns(10)
    for i, (col, (attr, _), val) in enumerate(zip(profile_cols, ATTRIBUTES, user_ratings)):
        short = attr.split()[0]
        col.metric(short, val)

st.markdown("")

# ── SUBMIT ────────────────────────────────────────────────────────────────────
submitted = st.button("🔍  Find My Drink", type="primary", use_container_width=True)

# ── RESULTS ───────────────────────────────────────────────────────────────────
if submitted:
    ranked = match_drinks(user_ratings, drinks)
    top2   = ranked[:2]

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="section-header">Your Top Matches</p>', unsafe_allow_html=True)

    badges = [("🥇", "result-card", "match-pct"), ("🥈", "result-card silver", "match-pct silver")]

    for (badge, card_class, pct_class), drink in zip(badges, top2):
        pct       = drink["match_pct"]
        dist      = drink["distance"]
        profile   = drink["profile"]

        # Build attribute chip HTML
        chips = "".join(
            f'<span class="attr-chip">{EMOJIS[j]} {ATTRIBUTES[j][0].split("/")[0].strip()}: {profile[j]}</span>'
            for j in range(10)
        )

        st.markdown(f"""
        <div class="{card_class}">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div style="flex:1;">
                    <div class="drink-name">{badge} {drink['name']}</div>
                    <div class="drink-desc">{drink['description']}</div>
                    <div style="font-size:0.78rem; color:#6b7280; margin-bottom:0.4rem;">
                        Category: <b>{drink['category']}</b>
                    </div>
                    <div class="profile-row">{chips}</div>
                </div>
                <div style="text-align:center; padding-left:1.5rem; min-width:90px;">
                    <div class="{pct_class}">{pct:.0f}%</div>
                    <div class="match-label">match</div>
                    <div style="font-size:0.72rem; color:#9ca3af; margin-top:0.4rem;">
                        distance: {dist}/40
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── YOUR PROFILE vs MATCHES ───────────────────────────────────────────────
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="section-header">Profile Comparison</p>', unsafe_allow_html=True)

    import pandas as pd

    short_names = [a.split()[0].split("/")[0].strip() for a, _ in ATTRIBUTES]
    comparison  = pd.DataFrame(
        {
            "Attribute":   short_names,
            "You":         user_ratings,
            top2[0]["name"][:22]: top2[0]["profile"],
            top2[1]["name"][:22]: top2[1]["profile"],
        }
    ).set_index("Attribute")

    st.dataframe(
        comparison.style
            .background_gradient(cmap="Greens", vmin=1, vmax=5)
            .format("{:.0f}"),
        use_container_width=True,
    )

    # ── FULL RANKING EXPANDER ─────────────────────────────────────────────────
    with st.expander("📋 See all 88 drinks ranked", expanded=False):
        all_df = pd.DataFrame([
            {
                "Rank":        i + 1,
                "Drink":       d["name"],
                "Category":    d["category"],
                "Match %":     f"{d['match_pct']:.0f}%",
                "Distance":    d["distance"],
            }
            for i, d in enumerate(ranked)
        ])
        st.dataframe(all_df, use_container_width=True, hide_index=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; font-size:0.75rem; color:#9ca3af;'>"
    "88 drinks · 10 attributes · distance-based matching · "
    "100% = perfect match &nbsp;|&nbsp; scores based on FY23 Starbucks menu</p>",
    unsafe_allow_html=True,
)
