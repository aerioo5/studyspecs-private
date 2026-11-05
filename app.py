"""
Study Specs — Interactive Laptop Recommender (Streamlit app)

To run locally:
    pip install streamlit pandas
    streamlit run app.py
"""

import random

import streamlit as st
from recommend import (
    load_data,
    recommend_laptops,
    why_this_laptop,
    shopping_links,
    DOMAIN_TO_COLUMN,
    PERFORMANCE_TIERS,
    STORAGE_MAP,
)

st.set_page_config(page_title="Study Specs", page_icon="💻", layout="centered")

WAVE_FRONT = (
    "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 1120 60' preserveAspectRatio='none'%3E%3Cpath "
    "d='M0 30 C 140 0, 280 60, 420 30 C 560 0, 700 60, 840 30 "
    "C 980 0, 1000 30, 1120 20 L1120 60 L0 60 Z' fill='white'/%3E%3C/svg%3E\")"
)
# Softer second wave sitting slightly behind, for depth.
WAVE_BACK = (
    "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 1120 60' preserveAspectRatio='none'%3E%3Cpath "
    "d='M0 20 C 140 55, 280 0, 420 25 C 560 50, 700 0, 840 25 "
    "C 980 50, 1000 15, 1120 30 L1120 60 L0 60 Z' fill='white' fill-opacity='0.5'/%3E%3C/svg%3E\")"
)

STYLE = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{--paper:#F5F7FB;--paper-2:#FFFFFF;--ink:#171B2E;--ink-soft:#5B6478;--blue:#2F6FED;--blue-dark:#1F4FBE;--blue-light:#8FB4FF;--amber:#FFB020;--amber-dark:#B87400;--mint:#12B886;--line:rgba(23,27,46,0.10);--line-strong:rgba(23,27,46,0.22);}
.stApp{background:linear-gradient(180deg,#0C1229 0%,#131D45 55%,#1B2C66 100%) !important;background-attachment:fixed !important;font-family:'Inter',sans-serif;color:#fff;}
[data-testid="stHeader"]{background:transparent !important;}
.stApp::after{content:"";position:fixed;left:0;right:0;bottom:0;height:110px;background-image:__WAVE_FRONT__,__WAVE_BACK__;background-size:100% 80px,100% 100px;background-position:bottom,bottom;background-repeat:no-repeat;pointer-events:none;z-index:0;}
.block-container{position:relative;z-index:1;padding-bottom:150px !important;}
h1,h2,h3{font-family:'Space Grotesk',sans-serif !important;color:#fff !important;}
.stApp [data-testid="stMarkdownContainer"] p,.stApp [data-testid="stCaptionContainer"]{color:rgba(255,255,255,0.82);}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:rgba(255,255,255,0.20) !important;}
.starfield{position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:-1;pointer-events:none;overflow:hidden;}
[data-testid="stElementContainer"]:has(.starfield),.element-container:has(.starfield){position:absolute;height:0;margin:0;padding:0;}
.star{position:absolute;background:#fff;border-radius:50%;box-shadow:0 0 6px 1px rgba(255,255,255,0.55);pointer-events:auto;cursor:default;}
.star::before{content:"";position:absolute;top:-10px;left:-10px;right:-10px;bottom:-10px;}
.star.s1{width:2px;height:2px;}
.star.s2{width:3px;height:3px;}
.star.s3{width:4px;height:4px;}
.star:hover{animation:starblink 0.8s ease-in-out infinite;}
@keyframes starblink{0%,100%{opacity:1;transform:scale(2.4);box-shadow:0 0 14px 4px rgba(255,255,255,0.95);}50%{opacity:0.15;transform:scale(0.7);box-shadow:none;}}
.question-progress{color:var(--blue-light);font-size:13px;font-weight:700;margin:8px 0 8px;}
.question-card{background:var(--paper-2);border:1px solid var(--line);border-radius:16px;padding:32px 34px 28px;margin:18px 0 22px;box-shadow:0 8px 24px rgba(0,0,0,0.25);}
.question-number{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:9px;background:var(--blue);color:#fff;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:14px;margin-bottom:16px;}
.question-title{font-family:'Space Grotesk',sans-serif;font-size:27px;line-height:1.25;font-weight:600;color:var(--ink);margin-bottom:8px;}
.question-help{color:var(--ink-soft);font-size:14px;line-height:1.6;margin-bottom:0;}
div[role="radiogroup"]{gap:10px !important;background:transparent !important;border:none !important;padding:0 !important;box-shadow:none !important;}
div[role="radiogroup"] label{background:rgba(255,255,255,0.12) !important;border:1px solid rgba(255,255,255,0.40) !important;border-radius:10px !important;padding:13px 16px !important;margin:0 !important;}
[data-testid="stElementContainer"]:has([data-testid="stRadio"]),.element-container:has([data-testid="stRadio"]),div[data-testid="stRadio"],div[data-testid="stRadio"] > div{width:100% !important;}
div[role="radiogroup"]{width:100% !important;align-items:stretch !important;}
div[role="radiogroup"] label{width:100% !important;box-sizing:border-box !important;}
div[role="radiogroup"] label,div[role="radiogroup"] label *{color:#fff !important;}
div[role="radiogroup"] label:hover{border-color:var(--blue-light) !important;background:rgba(255,255,255,0.20) !important;}
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div{background:rgba(255,255,255,0.14) !important;border:1px solid rgba(255,255,255,0.40) !important;border-radius:12px !important;box-shadow:none !important;}
div[data-testid="stSelectbox"] div[data-baseweb="select"] *,div[data-testid="stMultiSelect"] div[data-baseweb="select"] *{color:#fff !important;}
div[data-testid="stSelectbox"] svg,div[data-testid="stMultiSelect"] svg{fill:#fff !important;}
div[data-testid="stSelectbox"] input::placeholder,div[data-testid="stMultiSelect"] input::placeholder{color:rgba(255,255,255,0.65) !important;}
span[data-baseweb="tag"]{background:var(--blue) !important;}
div[data-testid="stSlider"]{background:rgba(255,255,255,0.12) !important;border:1px solid rgba(255,255,255,0.40);border-radius:14px;padding:16px 18px 10px;box-shadow:none;margin-bottom:18px;}
div[data-testid="stSlider"] *{color:#fff !important;}
[data-testid="stExpander"]{background:rgba(255,255,255,0.12);border-radius:12px;border:1px solid rgba(255,255,255,0.40);}
[data-testid="stExpander"] *{color:#fff !important;}
.stButton > button,.stLinkButton > a,[data-testid="stBaseButton-secondary"],[data-testid="stBaseButton-primary"],[data-testid="stBaseLinkButton-secondary"],[data-testid="stBaseLinkButton-primary"]{background:var(--blue) !important;color:#fff !important;border:1px solid var(--blue-dark) !important;border-radius:10px !important;font-weight:600 !important;text-decoration:none !important;box-shadow:0 4px 14px rgba(47,111,237,0.35);}
.stButton > button *,.stLinkButton > a *,[data-testid="stBaseButton-secondary"] *,[data-testid="stBaseButton-primary"] *,[data-testid="stBaseLinkButton-secondary"] *,[data-testid="stBaseLinkButton-primary"] *{color:#fff !important;}
.stButton > button:hover,.stLinkButton > a:hover,[data-testid="stBaseButton-secondary"]:hover,[data-testid="stBaseButton-primary"]:hover,[data-testid="stBaseLinkButton-secondary"]:hover,[data-testid="stBaseLinkButton-primary"]:hover{background:var(--blue-dark) !important;border-color:var(--blue-light) !important;}
.results-header{margin:28px 0 24px;}
.results-eyebrow{font-family:'Space Grotesk',sans-serif;font-size:13px;font-weight:700;color:var(--blue-light);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;}
.results-title{font-family:'Space Grotesk',sans-serif;font-size:32px;line-height:1.2;font-weight:700;color:#fff;margin-bottom:8px;}
.results-subtitle{color:rgba(255,255,255,0.72);font-size:14px;line-height:1.6;}
.laptop-card{background:#FFFFFF;border:1px solid rgba(23,27,46,0.10);border-radius:18px;padding:24px;margin:14px 0;box-shadow:0 8px 25px rgba(0,0,0,0.28);}
.laptop-card:hover{border-color:rgba(47,111,237,0.55);}
.laptop-top{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:8px;}
.laptop-rank{font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;color:var(--ink-soft);text-transform:uppercase;letter-spacing:0.06em;}
.laptop-name{font-family:'Space Grotesk',sans-serif;font-size:21px;font-weight:700;color:var(--ink);margin:5px 0 4px;}
.laptop-price{font-family:'Space Grotesk',sans-serif;font-size:18px;font-weight:700;color:var(--blue);}
.match-pill{display:inline-block;padding:6px 11px;border-radius:999px;font-size:12px;font-weight:700;}
.pill-high{background:rgba(18,184,134,0.12);color:#087F5B;}
.pill-mid{background:rgba(47,111,237,0.12);color:#1F4FBE;}
.pill-low{background:rgba(255,176,32,0.16);color:#9A6700;}
.spec-grid{margin-top:18px;display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px;}
.spec-label{font-size:11px;color:var(--ink-soft);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:2px;}
.spec-value{font-size:14px;font-weight:600;color:var(--ink);}
.gpu-line{margin-top:14px;padding-top:14px;border-top:1px solid rgba(23,27,46,0.08);font-size:13px;color:var(--ink-soft);}
.gpu-line strong{color:var(--ink);}
.results-count{color:rgba(255,255,255,0.72);font-size:13px;margin-bottom:18px;}
.results-actions{margin-top:28px;padding-top:20px;border-top:1px solid rgba(255,255,255,0.15);}
.ss-footer{text-align:center;color:rgba(255,255,255,0.6);font-size:12px;margin-top:32px;}
[data-testid="stElementContainer"]:has(.spec-cube-wrap),.element-container:has(.spec-cube-wrap){position:absolute;height:0;margin:0;padding:0;}
.spec-cube-wrap{position:fixed;right:4vw;top:50%;transform:translateY(-50%);width:150px;height:150px;perspective:700px;z-index:2;pointer-events:none;}
.spec-cube{position:relative;width:100%;height:100%;transform-style:preserve-3d;animation:cubeSpin 18s linear infinite;}
.spec-face{position:absolute;inset:0;box-sizing:border-box;padding:12px;border-radius:14px;border:1px solid #8FB4FF;background:rgba(23,27,46,0.82);box-shadow:0 0 18px rgba(47,111,237,0.35);display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;}
.spec-face.f1{transform:rotateY(0deg) translateZ(75px);}
.spec-face.f2{transform:rotateY(90deg) translateZ(75px);}
.spec-face.f3{transform:rotateY(180deg) translateZ(75px);}
.spec-face.f4{transform:rotateY(270deg) translateZ(75px);}
.spec-label{font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#8FB4FF;margin-bottom:6px;}
.spec-value{font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:600;line-height:1.3;color:#FFFFFF;}
@keyframes cubeSpin{from{transform:rotateX(-14deg) rotateY(0deg);}to{transform:rotateX(-14deg) rotateY(360deg);}}
@media (max-width:1200px){.spec-cube-wrap{display:none;}}
</style>"""

STYLE = STYLE.replace("__WAVE_FRONT__", WAVE_FRONT).replace("__WAVE_BACK__", WAVE_BACK)
st.markdown(STYLE, unsafe_allow_html=True)


# ------------------------------------------------------------
# Starfield — tiny stars sit behind the content. Hover one and it blinks.
# The layer is z-index:-1 so it can never block clicks on the app itself.
# ------------------------------------------------------------
def build_starfield(count=80, seed=11):
    rng = random.Random(seed)  # fixed seed = same sky on every rerun
    stars = []
    for _ in range(count):
        size = rng.choice(["s1", "s1", "s2", "s2", "s3"])
        stars.append(
            f'<span class="star {size}" style="left:{rng.uniform(1, 99):.1f}%;'
            f'top:{rng.uniform(1, 92):.1f}%;opacity:{rng.uniform(0.35, 0.9):.2f}"></span>'
        )
    return '<div class="starfield">' + "".join(stars) + "</div>"


st.markdown(build_starfield(), unsafe_allow_html=True)


def spec_cube():
    ans = st.session_state.get("answers", {})
    budget = f"₹{ans['budget']:,.0f}" if "budget" in ans else None
    workload = ans.get("performance", "").split(" (")[0] or None
    storage = ans.get("storage", "").split(" (")[0] or None
    faces = [
        ("Field", ans.get("domain")),
        ("Budget", budget),
        ("Workload", workload),
        ("Storage", storage),
    ]
    faces_html = "".join(
        f'<div class="spec-face f{i}"><div class="spec-label">{label}</div>'
        f'<div class="spec-value">{value or "Not set"}</div></div>'
        for i, (label, value) in enumerate(faces, start=1)
    )
    return f'<div class="spec-cube-wrap"><div class="spec-cube">{faces_html}</div></div>'


cube_slot = st.empty()


# ------------------------------------------------------------
# HTML helpers — each returns ONE contiguous string (no blank lines)
# ------------------------------------------------------------
def question_card(number, title, help_text):
    st.markdown(
        '<div class="question-card">'
        f'<div class="question-number">{number}</div>'
        f'<div class="question-title">{title}</div>'
        f'<div class="question-help">{help_text}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def hint_line(text_html):
    st.markdown(
        f'<div style="margin-top:-5px;margin-bottom:20px;color:rgba(255,255,255,0.72);font-size:13px;">{text_html}</div>',
        unsafe_allow_html=True,
    )


def spec(label, value):
    return (
        '<div>'
        f'<div class="spec-label">{label}</div>'
        f'<div class="spec-value">{value}</div>'
        '</div>'
    )


def laptop_card(i, row, cls):
    return (
        '<div class="laptop-card">'
        '<div class="laptop-top">'
        f'<div class="laptop-rank">Recommendation {i}</div>'
        f'<div class="match-pill pill-{cls}">{row.match_percent}% match</div>'
        '</div>'
        f'<div class="laptop-name">{row.brand_name} — {row.model}</div>'
        f'<div class="laptop-price">₹{row.price:,.0f}</div>'
        '<div class="spec-grid">'
        + spec("Processor", row.processor)
        + spec("RAM", row.ram)
        + spec("Storage", f"{row.memory_size}GB {row.memory_type}")
        + spec("Rating", f"⭐ {row.rating}")
        + '</div>'
        f'<div class="gpu-line"><strong>Graphics:</strong> {row.gpu_brand} {row.gpu_type}</div>'
        '</div>'
    )


def footer():
    st.markdown(
        '<div class="ss-footer">Study Specs — a domain-matched laptop recommender · '
        'college mini-project</div>',
        unsafe_allow_html=True,
    )


# ---- Load data once ----
@st.cache_data
def get_data():
    return load_data("study_specs_laptops_upgraded.csv")


df = get_data()
ALL_COMPANIES = sorted(df["brand_name"].unique().tolist())

# ---- Track answers across the flow ----
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.answers = {}


def next_step():
    st.session_state.step += 1


def restart():
    st.session_state.step = 0
    st.session_state.answers = {}


# Steps: 0-8 are the questionnaire (9 questions), 9 = results, 10 = buy page
STEPS_TOTAL = 9

if st.session_state.step <= STEPS_TOTAL:
    step_label = (
        f"Question {st.session_state.step + 1} of {STEPS_TOTAL}"
        if st.session_state.step < STEPS_TOTAL
        else "Your matches"
    )
    st.markdown(f'<div class="question-progress">{step_label}</div>', unsafe_allow_html=True)

st.progress(min(st.session_state.step / STEPS_TOTAL, 1.0))


def match_class(pct):
    """Returns the CSS class suffix for a given match percentage."""
    if pct >= 55:
        return "high"
    elif pct >= 40:
        return "mid"
    return "low"



# QUESTIONNAIRE — Q1 TO Q9


# Q1 — Academic Domain
if st.session_state.step == 0:
    question_card("01", "What are you studying?",
                  "We'll match laptops against real coursework needs for your field.")

    domain = st.selectbox(
        "Pick your academic domain",
        list(DOMAIN_TO_COLUMN.keys()),
        label_visibility="collapsed",
    )

    if st.button("Continue »", use_container_width=True):
        st.session_state.answers["domain"] = domain
        next_step()
        st.rerun()

# Q2 — Budget
elif st.session_state.step == 1:
    question_card("02", "What's your budget?",
                  "Set the maximum amount you're comfortable spending on your laptop.")

    budget = st.slider(
        "Maximum price",
        min_value=10000,
        max_value=300000,
        value=70000,
        step=5000,
        format="₹%d",
        label_visibility="collapsed",
    )

    st.markdown(
        f'<div style="text-align:center;margin:8px 0 20px;font-family:\'Space Grotesk\',sans-serif;'
        f'font-size:22px;font-weight:700;color:#8FB4FF;">₹{budget:,.0f}</div>',
        unsafe_allow_html=True,
    )

    if st.button("Continue »", use_container_width=True):
        st.session_state.answers["budget"] = budget
        next_step()
        st.rerun()

# Q3 — Performance
elif st.session_state.step == 2:
    question_card("03", "How heavy is your day-to-day workload?",
                  "Not sure what specs mean? Just pick what you'll actually be doing.")

    performance = st.radio(
        "Typical use",
        list(PERFORMANCE_TIERS.keys()),
        label_visibility="collapsed",
    )

    if st.button("Continue »", use_container_width=True):
        st.session_state.answers["performance"] = performance
        next_step()
        st.rerun()

# Q4 — Dedicated Graphics
elif st.session_state.step == 3:
    question_card("04", "Do you need dedicated graphics?",
                  "Dedicated graphics help with gaming, video editing, 3D modeling, or ML work. "
                  "If you're mostly writing, browsing, or coding, you likely don't need it.")

    gpu_choice = st.radio(
        "Graphics need",
        [
            "No — integrated graphics is fine",
            "Yes — I need dedicated graphics",
            "Not sure / no preference",
        ],
        label_visibility="collapsed",
    )

    if st.button("Continue »", use_container_width=True):
        st.session_state.answers["needs_gpu"] = gpu_choice
        next_step()
        st.rerun()

# Q5 — Processor Brand
elif st.session_state.step == 4:
    question_card("05", "Any processor brand preference?",
                  "Choose a processor brand if you already have one in mind. "
                  "Otherwise, we'll keep your options open.")

    proc_brand = st.radio(
        "Processor brand",
        ["Intel", "AMD", "Apple", "No preference"],
        label_visibility="collapsed",
    )

    if st.button("Continue »", use_container_width=True):
        st.session_state.answers["processor_brand"] = proc_brand
        next_step()
        st.rerun()

# Q6 — Storage
elif st.session_state.step == 5:
    question_card("06", "Any storage preference?",
                  "Choose based on how you want your laptop to handle files, "
                  "applications, and everyday storage.")

    storage = st.radio(
        "Storage type",
        [
            "No preference",
            "SSD (faster)",
            "Hard Disk (cheaper, more space)",
            "eMMC (budget/light use)",
        ],
        label_visibility="collapsed",
    )

    if st.button("Continue »", use_container_width=True):
        st.session_state.answers["storage"] = storage
        next_step()
        st.rerun()

# Q7 — Laptop Brand
elif st.session_state.step == 6:
    question_card("07", "Any preferred laptop brands?",
                  "Pick one or more brands, or leave this open if you don't have a preference.")

    companies = st.multiselect(
        "Brands",
        ALL_COMPANIES,
        label_visibility="collapsed",
        placeholder="Select your preferred brands...",
    )

    if st.button("Continue »", use_container_width=True):
        st.session_state.answers["companies"] = companies
        next_step()
        st.rerun()

# Q8 — Data Security
elif st.session_state.step == 7:
    question_card("08", "How important is data security to you?",
                  "We'll add a few practical tips alongside your recommendations "
                  "if this matters to you.")

    security = st.radio(
        "Priority",
        ["Low", "Medium", "High"],
        index=1,
        label_visibility="collapsed",
    )

    if st.button("Continue »", use_container_width=True):
        st.session_state.answers["security"] = security
        next_step()
        st.rerun()

# Q9 — Rating + Number of Results
elif st.session_state.step == 8:
    question_card("09", "Last one — set your quality bar.",
                  "Choose the minimum rating you'd consider and how many "
                  "laptop matches you'd like to see.")

    min_rating = st.slider(
        "Minimum star rating",
        min_value=1.0,
        max_value=5.0,
        value=1.0,
        step=0.05,
    )
    hint_line(f"Showing laptops rated <strong>⭐ {min_rating:.2f}</strong> or higher")

    top_n = st.slider("Number of laptops to show", 1, 10, 5)
    hint_line(f"You'll receive <strong>{top_n}</strong> recommendations.")

    if st.button("Show my recommendations »", use_container_width=True):
        st.session_state.answers["min_rating"] = min_rating
        st.session_state.answers["top_n"] = top_n
        next_step()
        st.rerun()


# RESULTS

elif st.session_state.step == 9:
    ans = st.session_state.answers

    st.markdown(
        '<div class="results-header">'
        '<div class="results-eyebrow">Study Specs · Your Results</div>'
        '<div class="results-title">Specs that match your needs</div>'
        '<div class="results-subtitle">We\'ve compared laptops against your field of study, '
        'budget and preferences.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    recs = recommend_laptops(
        df,
        domain=ans["domain"],
        budget=ans["budget"],
        min_rating=ans["min_rating"],
        top_n=ans["top_n"],
        storage=STORAGE_MAP.get(ans["storage"]),
        performance=ans["performance"],
        needs_dedicated_gpu=(ans["needs_gpu"] == "Yes — I need dedicated graphics"),
        processor_brand=ans["processor_brand"],
        companies=ans["companies"] if ans["companies"] else None,
    )

    if recs.empty:
        st.warning(
            "No laptops matched all your filters. "
            "Try loosening your budget, brand, or graphics preference."
        )
        if st.button("← Back to questions"):
            st.session_state.step = 0
            st.rerun()
    else:
        st.session_state.results = recs

        noun = "match" if len(recs) == 1 else "matches"
        st.markdown(
            f'<div class="results-count">Showing <strong>{len(recs)}</strong> laptop {noun}.</div>',
            unsafe_allow_html=True,
        )

        for i, row in enumerate(recs.itertuples(index=False), start=1):
            st.markdown(laptop_card(i, row, match_class(row.match_percent)), unsafe_allow_html=True)

            with st.expander("💬 Why this matches you"):
                for reason in why_this_laptop(row, ans["domain"], security_priority=ans["security"]):
                    st.markdown(f"- {reason}")

        st.markdown('<div class="results-actions"></div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✦ Compare prices & buy ", use_container_width=True):
                next_step()
                st.rerun()
        with col2:
            if st.button("✦ Start over", use_container_width=True):
                restart()
                st.rerun()

    footer()


# BUY / PRICE COMPARISON PAGE

else:
    st.subheader("🛒💨 Compare prices & buy")
    st.caption("These open a search for the exact model on each site, so you can compare "
               "real-time prices yourself before buying.")

    recs = st.session_state.get("results")
    if recs is None or recs.empty:
        st.info("No recommendations to show — start over to get your matches.")
    else:
        for row in recs.itertuples(index=False):
            with st.container(border=True):
                st.markdown(f"**{row.brand_name} — {row.model}**")
                links = shopping_links(row.brand_name, row.model)
                cols = st.columns(len(links))
                for col, (site, url) in zip(cols, links.items()):
                    col.link_button(site, url)

    st.divider()
    if st.button("✦ Start over"):
        restart()
        st.rerun()

    footer()


cube_slot.markdown(spec_cube(), unsafe_allow_html=True)