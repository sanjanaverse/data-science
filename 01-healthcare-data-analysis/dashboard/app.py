"""
Interactive dashboard: Diabetes hospital readmissions.

Run from the repo root:
    .venv\\Scripts\\streamlit run 01-healthcare-data-analysis/dashboard/app.py
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# This file lives in dashboard/, so the project folder is one level up.
# Adding it to sys.path lets us import the shared code in src/.
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_DIR))

from src.features import (AGE_ORDER, INSULIN_NAMES, MEDICATION_ORDER,
                          PRIOR_INPATIENT_ORDER, add_analysis_columns, rate_table)

DATA_PATH = PROJECT_DIR / "data" / "processed" / "cleaned_data.csv"

# Same colours as the notebook charts
BLUE = "#2a78d6"
MUTED = "#898781"


# ---------------------------------------------------------------- page setup
st.set_page_config(page_title="Diabetes Readmissions Dashboard", page_icon="🏥", layout="wide")

# Streamlit colours selected filter options red by default, which looks like an error.
# This small CSS rule makes them blue to match the charts.
st.markdown(f"""<style>
    .stMultiSelect span[data-tag] {{ background-color: {BLUE} !important; }}
</style>""", unsafe_allow_html=True)



# ---------------------------------------------------------------- load data
@st.cache_data   # read the CSV once, not on every click
def load_data():
    df = pd.read_csv(DATA_PATH, low_memory=False)
    return add_analysis_columns(df)


if not DATA_PATH.exists():
    st.error(f"Cleaned data not found at {DATA_PATH}. Run notebooks/01_data_cleaning.ipynb first.")
    st.stop()

df = load_data()

st.title("Diabetes Hospital Readmissions")
st.caption(f"First hospital stays of {len(df):,} patients with diabetes at 130 US hospitals (1999–2008). "
           "Use the filters on the left to explore who is readmitted within 30 days.")


# ---------------------------------------------------------------- sidebar filters
st.sidebar.header("Filters")

age_choice = st.sidebar.multiselect("Age group", AGE_ORDER, default=AGE_ORDER)
gender_options = sorted(df["gender"].unique())
gender_choice = st.sidebar.multiselect("Gender", gender_options, default=gender_options)
admission_options = sorted(df["admission_type_label"].unique())
admission_choice = st.sidebar.multiselect("Admission type", admission_options, default=admission_options)

st.sidebar.caption("Tip: remove options to focus on a group. The coloured numbers under each "
                   "KPI compare the selection with all patients.")

# Keep only the rows that match every filter
filtered = df[
    df["age_group"].isin(age_choice)
    & df["gender"].isin(gender_choice)
    & df["admission_type_label"].isin(admission_choice)
]

if filtered.empty:
    st.warning("No patients match these filters. Select at least one option in each filter.")
    st.stop()


# ---------------------------------------------------------------- KPI cards
def kpis(data):
    """The four headline numbers for a set of patients."""
    return {
        "patients": len(data),
        "stay": data["length_of_stay"].mean(),
        "readmit": data["readmit_flag"].mean(),
        "meds": data["num_medications"].mean(),
    }


now, everyone = kpis(filtered), kpis(df)
is_filtered = len(filtered) < len(df)


def delta(value):
    """Show the difference from all patients only when a filter is active."""
    return value if is_filtered else None


col1, col2, col3, col4 = st.columns(4)
col1.metric("Total patients", f"{now['patients']:,}",
            delta=delta(f"{now['patients'] / everyone['patients']:.0%} of all"), delta_color="off")
col2.metric("Average length of stay", f"{now['stay']:.1f} days",
            delta=delta(f"{now['stay'] - everyone['stay']:+.1f} days vs all"), delta_color="inverse")
col3.metric("30-day readmission rate", f"{now['readmit']:.1%}",
            delta=delta(f"{(now['readmit'] - everyone['readmit']) * 100:+.1f} pts vs all"), delta_color="inverse")
col4.metric("Average medications", f"{now['meds']:.1f}",
            delta=delta(f"{now['meds'] - everyone['meds']:+.1f} vs all"), delta_color="off")
# delta_color="inverse": a rise shows red, because a longer stay or more readmissions is bad.

st.divider()


# ---------------------------------------------------------------- chart helpers
selection_rate = now["readmit"]


def style(fig, x_title, y_title, percent_axis=None):
    """Apply the same clean look to every chart."""
    fig.update_traces(marker_color=BLUE)
    fig.update_layout(
        xaxis_title=x_title,
        yaxis_title=y_title,
        margin=dict(l=10, r=10, t=10, b=10),
        height=360,
        bargap=0.3,
        showlegend=False,
    )
    if percent_axis == "y":
        fig.update_yaxes(tickformat=".0%")
    if percent_axis == "x":
        fig.update_xaxes(tickformat=".0%")
    return fig


def rate_chart(group_col, order, x_title):
    """Bar chart of readmission rate per group, with a line for the selection's average."""
    table = rate_table(filtered, group_col, order).dropna()
    fig = px.bar(
        table, x=group_col, y="readmission_rate",
        category_orders={group_col: order},
        custom_data=["patients"],
    )
    fig.update_traces(hovertemplate="%{x}<br>Readmission rate: %{y:.1%}"
                                    "<br>Patients: %{customdata[0]:,}<extra></extra>")
    # Treat x values as labels, not numbers. Without this, Plotly reads "0", "1", "2" as
    # numbers, makes a numeric axis, and silently drops the "5+" bar.
    fig.update_xaxes(type="category")
    fig.add_hline(y=selection_rate, line_color=MUTED, line_width=1.5,
                  annotation_text=f"average {selection_rate:.1%}",
                  annotation_position="top left", annotation_font_color=MUTED)
    return style(fig, x_title, "30-day readmission rate", percent_axis="y")


# ---------------------------------------------------------------- charts (2 per row)
left, right = st.columns(2)

with left:
    st.subheader("Readmission by age group")
    st.plotly_chart(rate_chart("age_group", AGE_ORDER, "Age group (years)"), width="stretch")

with right:
    st.subheader("Readmission by prior hospital stays")
    st.plotly_chart(rate_chart("prior_inpatient", PRIOR_INPATIENT_ORDER,
                               "Inpatient stays in the previous year"), width="stretch")

left, right = st.columns(2)

with left:
    st.subheader("Length of stay")
    stay_counts = filtered["length_of_stay"].value_counts().sort_index().reset_index()
    stay_counts.columns = ["days", "patients"]
    fig = px.bar(stay_counts, x="days", y="patients")
    fig.update_traces(hovertemplate="%{x} days<br>Patients: %{y:,}<extra></extra>")
    fig.update_xaxes(dtick=1)
    st.plotly_chart(style(fig, "Days in hospital", "Patients"), width="stretch")

with right:
    st.subheader("Readmission by number of medications")
    st.plotly_chart(rate_chart("medication_range", MEDICATION_ORDER,
                               "Medications during the stay"), width="stretch")

left, right = st.columns(2)

with left:
    st.subheader("Top 10 primary diagnoses")
    top = filtered["diagnosis_category"].value_counts().head(10).reset_index()
    top.columns = ["diagnosis", "patients"]
    top["share"] = top["patients"] / len(filtered)
    fig = px.bar(top, x="share", y="diagnosis", orientation="h", custom_data=["patients"])
    fig.update_traces(hovertemplate="%{y}<br>Share: %{x:.1%}"
                                    "<br>Patients: %{customdata[0]:,}<extra></extra>")
    fig.update_yaxes(autorange="reversed")   # biggest bar at the top
    st.plotly_chart(style(fig, "Share of patients", "", percent_axis="x"), width="stretch")

with right:
    st.subheader("Readmission by insulin dose")
    st.plotly_chart(rate_chart("insulin_status", list(INSULIN_NAMES.values()),
                               "Insulin during the stay"), width="stretch")


# ---------------------------------------------------------------- footer
st.caption("Bars show patterns, not causes. Groups with few patients (hover to see the count) "
           "can have rates that swing widely. Data: UCI Machine Learning Repository, "
           "Diabetes 130-US Hospitals for Years 1999–2008.")
