import re
from pathlib import Path

# Data Visualizing
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st
from wordcloud import WordCloud

JOB_CATEGORIES = [
    ("Cybersecurity", [r"cyber\s*security", r"\bcyber\b", r"\binfosec\b", r"information security", r"security (analyst|engineer|specialist|consultant|supervisor|architect)"]),
    ("Software Engineering", [r"software", r"\bswe\b", r"\bsde\b", r"developer", r"programmer", r"\bengineer\b(?! risk)", r"backend", r"front[- ]?end", r"full[- ]?stack", r"devops", r"site reliability", r"\bsre\b"]),
    ("Data Science & Analytics", [r"data scien", r"machine learning", r"\bml\b", r"\bai\b", r"data analyst", r"analytics", r"data engineer", r"quant"]),
    ("Product Management", [r"product manager", r"\bpm\b", r"product owner", r"product lead"]),
    ("Consulting", [r"consult", r"advisor", r"advisory"]),
    ("Finance & Banking", [r"investment", r"banking", r"\btrader\b", r"trading", r"portfolio", r"\bfinance\b", r"financial analyst", r"equity", r"hedge fund", r"private equity", r"venture"]),
    ("Accounting & Audit", [r"accountant", r"accounting", r"\baudit", r"\btax\b"]),
    ("Marketing & Sales", [r"marketing", r"\bsales\b", r"business development", r"account executive", r"account manager", r"growth"]),
    ("Design", [r"\bux\b", r"\bui\b", r"designer", r"\bdesign\b"]),
    ("Operations & Strategy", [r"operations", r"\bstrategy\b", r"strategic", r"chief of staff", r"\bcoo\b"]),
    ("Research", [r"research", r"\brnd\b", r"r&d"]),
    ("Legal", [r"lawyer", r"attorney", r"\blegal\b", r"paralegal", r"\bjd\b"]),
    ("Healthcare & Medicine", [r"\bdoctor\b", r"physician", r"nurse", r"medical", r"clinical", r"\bmd\b", r"healthcare"]),
    ("Education & Academia", [r"\bstudent\b", r"\bphd\b", r"masters", r"\bmba\b", r"\bmdes\b", r"\bms\b", r"\bm\.s\.?\b", r"university", r"professor", r"teacher", r"graduate", r"undergrad"]),
    ("Project & Program Management", [r"project manager", r"program manager", r"scrum"]),
    ("Human Resources", [r"\bhr\b", r"human resources", r"recruiter", r"talent"]),
    ("Risk & Compliance", [r"\brisk\b", r"compliance", r"governance"]),
    ("IT & Network", [r"\bit\b analyst", r"network", r"system admin", r"sysadmin", r"technician", r"help desk"]),
    ("General Analyst", [r"analyst", r"associate", r"specialist"]),
    ("General Management", [r"manager", r"rotational", r"chief"]),
]


def categorize_job(title: str) -> str:
    text = title.lower()
    for category, patterns in JOB_CATEGORIES:
        for pattern in patterns:
            if re.search(pattern, text):
                return category
    return "Other"

st.set_page_config(page_title="ΨHM Alumni Dashboard", layout="wide", initial_sidebar_state="collapsed")

NAVY = "#13294B"
DARK_NAVY = "#0a1628"
CARD_NAVY = "#0d1d35"
ACCENT = "#FFFFFF"
ACCENT_HOVER = "#E0E0E0"
WHITE = "#FFFFFF"
LIGHT_GRAY = "#CCCCCC"
SOFT_WHITE = "#F0F0F0"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="st-"], .stApp, button, input, textarea, select {{
        font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif !important;
    }}

    /* Don't override the Material Symbols font on icon elements — otherwise
       the ligature text (e.g. "keyboard_double_arrow_right") shows in place of the glyph. */
    span[class*="material-symbols"],
    span[class*="material-icons"],
    .material-icons,
    .material-symbols-rounded,
    .material-symbols-outlined,
    .material-symbols-sharp,
    [data-testid="stIconMaterial"] {{
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    }}

    .stApp {{
        background-color: {NAVY};
        color: {SOFT_WHITE};
    }}

    /* Remove default top/bottom padding so the hero sits flush with the top
       and the footer sits flush with the bottom. */
    .main .block-container,
    [data-testid="stMainBlockContainer"],
    section.main > div.block-container {{
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }}
    [data-testid="stAppViewContainer"] > .main {{
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }}

    /* Keep Streamlit header transparent but make sure its controls stay clickable above the hero */
    #MainMenu, header[data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
        z-index: 1000;
    }}
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {{
        z-index: 1001 !important;
        position: relative;
    }}
    footer {{ visibility: hidden; }}

    .phm-hero {{
        text-align: center;
        padding: 80px 24px 64px;
        background: linear-gradient(180deg, {DARK_NAVY} 0%, {NAVY} 100%);
        margin: 0 -3rem 2.5rem -3rem;
        border-bottom: 3px solid {ACCENT};
    }}
    .phm-hero h1 {{
        font-size: clamp(2.5rem, 6vw, 5rem);
        font-weight: 800;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: {WHITE};
        margin: 0 0 0.75rem 0;
        line-height: 1.05;
    }}
    .phm-hero .subtitle {{
        color: {LIGHT_GRAY};
        font-style: italic;
        font-weight: 300;
        font-size: 1.15rem;
        max-width: 680px;
        margin: 0 auto 0.5rem;
        line-height: 1.6;
    }}
    .phm-hero .announce {{
        color: {ACCENT};
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-size: 0.85rem;
        margin-top: 1rem;
    }}

    .stApp h2, .stApp h3 {{
        color: {WHITE};
        font-weight: 600;
        letter-spacing: 0.01em;
        position: relative;
        padding-bottom: 0.5rem;
        margin-top: 2.5rem;
    }}
    .stApp h2::after, .stApp h3::after {{
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 56px;
        height: 3px;
        background-color: {ACCENT};
    }}

    .stApp p, .stApp li, .stApp .stMarkdown {{
        color: {SOFT_WHITE};
        line-height: 1.8;
    }}

    [data-testid="stMetric"] {{
        background-color: {CARD_NAVY};
        padding: 18px 20px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.35);
        border: 1px solid rgba(255,255,255,0.15);
    }}
    [data-testid="stMetricLabel"] p {{
        color: {LIGHT_GRAY} !important;
        text-transform: uppercase;
        font-size: 0.7rem !important;
        letter-spacing: 0.1em;
        font-weight: 500;
    }}
    [data-testid="stMetricValue"] {{
        color: {WHITE} !important;
        font-weight: 700;
    }}

    .stButton > button {{
        background-color: {ACCENT};
        color: {NAVY} !important;
        border: none;
        border-radius: 4px;
        padding: 12px 28px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        transition: background 0.2s ease;
    }}
    .stButton > button:hover {{
        background-color: {ACCENT_HOVER};
        color: {NAVY} !important;
    }}

    .stDownloadButton > button {{
        background-color: {DARK_NAVY};
        color: {WHITE} !important;
        border: 1px solid rgba(255,255,255,0.25);
        border-radius: 4px;
        padding: 12px 28px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        transition: background 0.2s ease, border-color 0.2s ease;
    }}
    .stDownloadButton > button:hover {{
        background-color: {NAVY};
        color: {WHITE} !important;
        border-color: {WHITE};
    }}

    [data-testid="stSidebar"] {{
        background-color: {DARK_NAVY};
        border-right: 1px solid rgba(255,255,255,0.2);
    }}
    [data-testid="stSidebar"] h2 {{
        color: {WHITE} !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 1rem;
    }}
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {{
        color: {SOFT_WHITE} !important;
    }}

    /* Slider — force the accent (thumb + filled track + value bubble) to white,
       and the unfilled track to a soft translucent white. */
    [data-testid="stSlider"] [role="slider"] {{
        background-color: {WHITE} !important;
        border-color: {WHITE} !important;
        box-shadow: 0 0 0 2px {WHITE} !important;
    }}
    [data-testid="stSlider"] [data-baseweb="slider"] > div > div {{
        background: rgba(255,255,255,0.25) !important;
    }}
    [data-testid="stSlider"] [data-baseweb="slider"] > div > div > div {{
        background: {WHITE} !important;
    }}
    [data-testid="stSlider"] [data-testid="stThumbValue"],
    [data-testid="stSlider"] [data-testid="stTickBarMin"],
    [data-testid="stSlider"] [data-testid="stTickBarMax"],
    [data-testid="stSlider"] [role="slider"],
    [data-testid="stSlider"] [role="slider"] *,
    [data-testid="stSlider"] [data-baseweb="tooltip"],
    [data-testid="stSlider"] [data-baseweb="tooltip"] * {{
        color: {WHITE} !important;
    }}

    .stTextInput > div > div > input,
    .stMultiSelect [data-baseweb="select"] > div {{
        background-color: {CARD_NAVY} !important;
        color: {WHITE} !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }}

    .stAlert {{
        background-color: {CARD_NAVY};
        border-left: 4px solid {ACCENT};
        color: {SOFT_WHITE};
    }}
    .stAlert p {{ color: {SOFT_WHITE} !important; }}

    a {{ color: {ACCENT}; text-decoration: underline; text-underline-offset: 3px; }}
    a:hover {{ color: {LIGHT_GRAY}; }}

    .phm-footer {{
        margin: 4rem -3rem -3rem -3rem;
        padding: 48px 24px;
        background-color: #000000;
        text-align: center;
        border-top: 2px solid {ACCENT};
    }}
    .phm-footer .wordmark {{
        font-weight: 800;
        font-size: 1.4rem;
        letter-spacing: 0.15em;
        color: {WHITE};
        text-transform: uppercase;
    }}
    .phm-footer p {{
        color: {LIGHT_GRAY};
        font-size: 0.85rem;
        margin: 0.5rem 0 0;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="phm-hero">
        <h1>ΨHM Alumni Dashboard</h1>
        <p class="subtitle">Where Psi Eta Mu alumni live and work — a visual look at the brotherhood beyond Illinois.</p>
        <p class="announce">Spring 2026 Snapshot</p>
    </div>
    """,
    unsafe_allow_html=True,
)

#Manually opening data.csv locally -> Use PostgreSQL server and script to automatically update and pull new data
#DATA_PATH = Path(__file__).parent / "data.csv"
#if not DATA_PATH.exists():
#    st.error(f"Could not find `{DATA_PATH.name}` in the app directory. Drop the CSV next to `app.py` and refresh.")
#   st.stop()

#df = pd.read_csv(DATA_PATH)
#df.columns = [c.strip().lower() for c in df.columns]

try:
    conn = st.connection("postgresql", type="sql", url=st.secrets["DB_URI"])
    df = conn.query("SELECT * FROM alumni_records", ttl="10m")
except Exception as e:
    st.error("Database connection failed. Ensure secrets are configured correctly.")
    st.stop()

required = {"location", "job", "company"}
missing = required - set(df.columns)
if missing:
    st.error(f"CSV is missing required columns: {', '.join(sorted(missing))}")
    st.stop()

for col in ["location", "job", "company"]:
    df[col] = df[col].astype(str).str.strip()

unknown_mask = pd.Series(False, index=df.index)
for col in ["location", "job", "company"]:
    unknown_mask |= df[col].str.lower().isin(["", "nan", "none", "unknown"])

total_alumni = len(df)
jobs_not_shared = int(unknown_mask.sum())
df = df.loc[~unknown_mask].reset_index(drop=True)

if jobs_not_shared:
    st.info(
        f"ΨHM has {total_alumni} alumni in this dataset. "
        f"{jobs_not_shared} chose not to share their job information — "
        f"they're counted in the total below but excluded from the job, location, and company charts."
    )

df["job_category"] = df["job"].map(categorize_job)

with st.sidebar:
    st.header("Filters")
    locations = st.multiselect("Location", sorted(df["location"].unique()))
    companies = st.multiselect("Company", sorted(df["company"].unique()))
    categories = st.multiselect("Job Category", sorted(df["job_category"].unique()))
    top_n = st.slider("Top N to show in charts", 5, 30, 10)

filtered = df.copy()
if locations:
    filtered = filtered[filtered["location"].isin(locations)]
if companies:
    filtered = filtered[filtered["company"].isin(companies)]
if categories:
    filtered = filtered[filtered["job_category"].isin(categories)]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Alumni", f"{total_alumni:,}")
c2.metric("In Current View", f"{len(filtered):,}")
c3.metric("Unique Companies", f"{filtered['company'].nunique():,}")
c4.metric("Unique Locations", f"{filtered['location'].nunique():,}")
c5.metric("Job Categories", f"{filtered['job_category'].nunique():,}")

if filtered.empty:
    st.warning("No rows match the current filters.")
    st.stop()

def top_counts(series, n):
    return series.value_counts().head(n).rename_axis("value").reset_index(name="count")


def style_fig(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=SOFT_WHITE, family="Inter, Helvetica Neue, Arial, sans-serif"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.08)", color=LIGHT_GRAY, zerolinecolor="rgba(255,255,255,0.15)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)", color=LIGHT_GRAY, zerolinecolor="rgba(255,255,255,0.15)"),
        margin=dict(l=10, r=10, t=20, b=10),
        coloraxis_colorbar=dict(tickcolor=LIGHT_GRAY, tickfont=dict(color=LIGHT_GRAY)),
    )
    return fig


def orange_bar(data, label):
    fig = px.bar(
        data, x="count", y="value", orientation="h",
        labels={"value": label, "count": "Alumni"},
        color_discrete_sequence=[WHITE],
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return style_fig(fig)


left, right = st.columns(2)

with left:
    st.subheader(f"Top {top_n} Companies")
    st.plotly_chart(orange_bar(top_counts(filtered["company"], top_n), "Company"), use_container_width=True)

with right:
    st.subheader(f"Top {top_n} Locations")
    st.plotly_chart(orange_bar(top_counts(filtered["location"], top_n), "Location"), use_container_width=True)

st.subheader(f"Top {top_n} Job Categories")
st.plotly_chart(orange_bar(top_counts(filtered["job_category"], top_n), "Category"), use_container_width=True)

with st.expander("See raw job titles within each category"):
    st.dataframe(
        filtered.groupby("job_category")["job"]
        .apply(lambda s: ", ".join(sorted(s.unique())))
        .rename("titles")
        .reset_index()
        .sort_values("job_category"),
        use_container_width=True,
    )

st.subheader("Job Category Word Cloud")
cat_freq = filtered["job_category"].value_counts().to_dict()
if cat_freq:
    import random
    palette = ["#FFFFFF", "#F0F0F0", "#E0E0E0", "#CCCCCC", "#B8B8B8"]

    def phm_colors(*args, **kwargs):
        return random.choice(palette)

    wc = WordCloud(
        width=1600,
        height=800,
        background_color=None,
        mode="RGBA",
        color_func=phm_colors,
        prefer_horizontal=0.9,
        collocations=False,
    ).generate_from_frequencies(cat_freq)
    fig, ax = plt.subplots(figsize=(16, 8))
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig, use_container_width=True, transparent=True)
else:
    st.caption("No job categories to display.")

st.subheader("Alumni by US State")
state_pattern = re.compile(r",\s*([A-Z]{2})\s*$")
states = filtered["location"].str.extract(state_pattern, expand=False)
state_counts = states.dropna().value_counts().rename_axis("state").reset_index(name="count")
non_us = int(states.isna().sum())
if not state_counts.empty:
    fig = px.choropleth(
        state_counts,
        locations="state",
        locationmode="USA-states",
        color="count",
        scope="usa",
        color_continuous_scale=[[0, "#7a8aa5"], [0.5, "#c5d0e2"], [1, "#FFFFFF"]],
        labels={"count": "Alumni"},
        hover_data={"state": True, "count": True},
    )
    fig.update_traces(marker_line_color="#FFFFFF", marker_line_width=1.2)
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(
            bgcolor="rgba(0,0,0,0)",
            lakecolor=NAVY,
            landcolor="#4a5a78",
            showlakes=False,
            showsubunits=True,
            subunitcolor="#FFFFFF",
            subunitwidth=1.2,
            showcoastlines=True,
            coastlinecolor="#FFFFFF",
            coastlinewidth=1.2,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=SOFT_WHITE, family="Inter, sans-serif"),
        coloraxis_colorbar=dict(tickcolor=LIGHT_GRAY, tickfont=dict(color=LIGHT_GRAY)),
    )
    st.plotly_chart(fig, use_container_width=True)
    if non_us:
        st.caption(f"{non_us} alumni in non-US locations are not shown on the map.")
else:
    st.caption("No US-state locations to map.")

st.subheader("Alumni Records")
search = st.text_input("Search across all columns")
table = filtered
if search:
    mask = table.apply(lambda row: row.astype(str).str.contains(search, case=False, na=False).any(), axis=1)
    table = table[mask]
display_table = table.drop(columns=["latitude", "longitude"], errors="ignore")
st.dataframe(display_table, use_container_width=True)

st.download_button(
    "Download filtered CSV",
    data=table.to_csv(index=False).encode("utf-8"),
    file_name="alumni_filtered.csv",
    mime="text/csv",
)

st.markdown(
    """
    <div class="phm-footer">
        <div class="wordmark">ΨHM &middot; Psi Eta Mu</div>
        <p>University of Illinois Urbana-Champaign</p>
        <p><a href="mailto:contact@phmillinois.org">contact@phmillinois.org</a></p>
    </div>
    """,
    unsafe_allow_html=True,
)