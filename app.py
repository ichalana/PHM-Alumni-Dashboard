import re
from pathlib import Path

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

st.set_page_config(page_title="ΨHM Alumni Dashboard", layout="wide")

st.title("ΨHM Alumni Dashboard")
st.caption("Visualizing alumni locations, jobs, and companies from `data.csv`.")

DATA_PATH = Path(__file__).parent / "data.csv"
if not DATA_PATH.exists():
    st.error(f"Could not find `{DATA_PATH.name}` in the app directory. Drop the CSV next to `app.py` and refresh.")
    st.stop()

df = pd.read_csv(DATA_PATH)
df.columns = [c.strip().lower() for c in df.columns]

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

left, right = st.columns(2)

with left:
    st.subheader(f"Top {top_n} Companies")
    data = top_counts(filtered["company"], top_n)
    fig = px.bar(data, x="count", y="value", orientation="h", labels={"value": "Company", "count": "Alumni"})
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader(f"Top {top_n} Locations")
    data = top_counts(filtered["location"], top_n)
    fig = px.bar(data, x="count", y="value", orientation="h", labels={"value": "Location", "count": "Alumni"})
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

st.subheader(f"Top {top_n} Job Categories")
data = top_counts(filtered["job_category"], top_n)
fig = px.bar(data, x="count", y="value", orientation="h", labels={"value": "Category", "count": "Alumni"})
fig.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig, use_container_width=True)

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
    wc = WordCloud(
        width=1600,
        height=800,
        background_color=None,
        mode="RGBA",
        colormap="Dark2",
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
        color_continuous_scale="Blues",
        labels={"count": "Alumni"},
        hover_data={"state": True, "count": True},
    )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), geo=dict(bgcolor="rgba(0,0,0,0)"))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
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
st.dataframe(table, use_container_width=True)

st.download_button(
    "Download filtered CSV",
    data=table.to_csv(index=False).encode("utf-8"),
    file_name="alumni_filtered.csv",
    mime="text/csv",
)
