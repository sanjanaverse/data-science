"""
Extra columns used for analysis and charts, built from the cleaned data.

Keeping them here (instead of copying code into each notebook) means the
notebooks and the dashboard all group the data in exactly the same way.
"""

import numpy as np
import pandas as pd

from src.icd9 import icd9_category

# Fixed orders, so charts always show groups in a sensible sequence
AGE_ORDER = ["0-9", "10-19", "20-29", "30-39", "40-49",
             "50-59", "60-69", "70-79", "80-89", "90-99"]
MEDICATION_ORDER = ["1-5", "6-10", "11-15", "16-20", "21-30", "31+"]
PRIOR_INPATIENT_ORDER = ["0", "1", "2", "3", "4", "5+"]
INSULIN_NAMES = {"No": "Not on insulin", "Steady": "Steady dose",
                 "Up": "Dose up", "Down": "Dose down"}


def add_analysis_columns(df):
    """Return a copy of df with the extra columns used in the analysis."""
    df = df.copy()

    # 1 = readmitted within 30 days, 0 = not. The mean of this column is the rate.
    df["readmit_flag"] = (df["readmitted_30days"] == "Yes").astype(int)

    # Number of medications grouped into ranges
    df["medication_range"] = pd.cut(
        df["num_medications"],
        bins=[0, 5, 10, 15, 20, 30, np.inf],
        labels=MEDICATION_ORDER,
    ).astype(str)

    # Hospital stays in the year before this visit: 0, 1, 2, 3, 4, 5+
    df["prior_inpatient"] = df["number_inpatient"].clip(upper=5).astype(str).replace("5", "5+")

    # Primary diagnosis code -> broad category (see src/icd9.py)
    df["diagnosis_category"] = df["diag_1"].map(icd9_category)

    # Readable insulin status
    df["insulin_status"] = df["insulin"].map(INSULIN_NAMES)

    return df


def rate_table(df, group_col, order=None):
    """Patient count and 30-day readmission rate for each group in group_col."""
    table = df.groupby(group_col).agg(
        patients=("readmit_flag", "size"),
        readmission_rate=("readmit_flag", "mean"),
    )
    if order is not None:
        table = table.reindex(order)
    return table.reset_index()
