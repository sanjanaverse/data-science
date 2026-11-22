# Rebuilding this dashboard in Power BI

These steps rebuild `app.py` in Power BI Desktop (free, Windows) using `data/processed/cleaned_data.csv`.

## 1. Load the data

1. **Home → Get data → Text/CSV** and pick `cleaned_data.csv`.
2. Click **Transform Data** (not Load) to open Power Query.
3. Check the column types: `length_of_stay`, `num_medications` and `number_inpatient` should be **Whole Number**. `age_group`, `gender` and the `*_label` columns should be **Text**.
4. **Close & Apply**.

## 2. Add the helper columns

These match `src/features.py`. In **Table view**, choose **New column** and enter each formula:

```dax
Readmit Flag = IF('cleaned_data'[readmitted_30days] = "Yes", 1, 0)

Medication Range =
SWITCH(TRUE(),
    'cleaned_data'[num_medications] <= 5,  "1-5",
    'cleaned_data'[num_medications] <= 10, "6-10",
    'cleaned_data'[num_medications] <= 15, "11-15",
    'cleaned_data'[num_medications] <= 20, "16-20",
    'cleaned_data'[num_medications] <= 30, "21-30",
    "31+")

Prior Inpatient = IF('cleaned_data'[number_inpatient] >= 5, "5+", FORMAT('cleaned_data'[number_inpatient], "0"))
```

**Sort order:** text columns sort alphabetically, so "11-15" would come before "6-10". For each range column:
1. Add a number column with the right order, for example `Medication Order = SWITCH('cleaned_data'[Medication Range], "1-5",1, "6-10",2, "11-15",3, "16-20",4, "21-30",5, 6)`.
2. Select the range column and use **Column tools → Sort by column → Medication Order**.

Do the same for `age_group` and `Prior Inpatient`.

**Diagnosis category:** the ICD-9 grouping is easiest to bring in from Python. Add `df["diagnosis_category"] = df["diag_1"].map(icd9_category)` before saving the CSV in `01_data_cleaning.ipynb`. You can also build the same ranges with a `SWITCH` like the one above.

## 3. Create the KPI measures

A **measure** is a calculation that updates with the filters. Choose **Home → New measure** for each:

```dax
Total Patients = COUNTROWS('cleaned_data')
Avg Length of Stay = AVERAGE('cleaned_data'[length_of_stay])
Readmission Rate = AVERAGE('cleaned_data'[Readmit Flag])
Avg Medications = AVERAGE('cleaned_data'[num_medications])
```

Set **Readmission Rate** to **Percentage** with 1 decimal place (Measure tools → Format), and the two averages to 1 decimal place.

## 4. Build the page

| Streamlit part | Power BI visual | Fields |
|---|---|---|
| Title and description | **Text box** | Type the same title and one-line description |
| 4 KPI cards | **Card** ×4 in a row | One measure each |
| Sidebar filters | **Slicer** ×3 down the left side, style *Dropdown* or *List* | `age_group`, `gender`, `admission_type_label` |
| Readmission by age | **Clustered column chart** | X: `age_group`, Y: `Readmission Rate` |
| Readmission by prior stays | **Clustered column chart** | X: `Prior Inpatient`, Y: `Readmission Rate` |
| Length of stay | **Clustered column chart** | X: `length_of_stay`, Y: `Total Patients` |
| Readmission by medications | **Clustered column chart** | X: `Medication Range`, Y: `Readmission Rate` |
| Top 10 diagnoses | **Clustered bar chart** | Y: `diagnosis_category`, X: `Total Patients`. Filter pane: **Top N = 10** by `Total Patients` |
| Readmission by insulin | **Clustered column chart** | X: `insulin`, Y: `Readmission Rate` |

**Average line:** select a rate chart, open **Analytics pane (magnifying glass) → Average line**, and set the colour to grey. This works like the grey "average" line in the Streamlit charts.

**Hover details:** drag `Total Patients` into **Tooltips** on each rate chart. Hovering then shows how many patients are behind each bar, just like the Streamlit tooltips.

## 5. Style it the same way

- **Format → Columns → Colour:** `#2a78d6` (the same blue) on every chart.
- Turn off data labels except where one number matters, and keep gridlines light.
- **View → Themes** lets you save these settings and reuse them on other pages.

## 6. Check it

Clear all slicers. The cards should show **69,970 patients**, **4.3 days**, **9.0%** and **15.7 medications**, the same as the Streamlit dashboard. If they don't match, check the column types from step 1.

## Streamlit vs Power BI

| | Streamlit (`app.py`) | Power BI |
|---|---|---|
| Built with | Python code | Drag and drop, plus DAX formulas |
| Version control | Plain text, works well in Git | `.pbix` is a binary file, so Git can't show what changed |
| Sharing | Streamlit Community Cloud (free) | Power BI Service (needs a work account) |
| Common in | Data science and tech teams | Business and NHS/healthcare analytics teams |

Building both shows you can work in either environment.
