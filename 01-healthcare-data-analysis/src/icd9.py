"""
Group ICD-9 diagnosis codes into broad, readable categories.

ICD-9 is the coding system US hospitals used for diagnoses in 1999-2008.
Codes are numbers like "428" (heart failure) or "250.83" (diabetes),
and the number range tells you which body system the disease belongs to.
Codes starting with "V" or "E" are not diseases: they record extra
information such as check-ups (V) or the cause of an injury (E).

The ranges below follow the official ICD-9-CM chapters, with diabetes
(code 250.xx) split out because it is the focus of this dataset.
"""

# Each entry: (first code, last code, category name).
# Codes are compared as numbers, so 250.83 falls inside 240-279.
ICD9_RANGES = [
    (1, 139, "Infectious"),
    (140, 239, "Neoplasms (cancer)"),
    (240, 279, "Endocrine & metabolic"),   # diabetes (250) is handled first
    (280, 289, "Blood"),
    (290, 319, "Mental health"),
    (320, 389, "Nervous system"),
    (390, 459, "Circulatory"),
    (460, 519, "Respiratory"),
    (520, 579, "Digestive"),
    (580, 629, "Genitourinary"),
    (630, 679, "Pregnancy"),
    (680, 709, "Skin"),
    (710, 739, "Musculoskeletal"),
    (740, 759, "Congenital"),
    (760, 779, "Perinatal"),
    (780, 799, "Symptoms & ill-defined"),
    (800, 999, "Injury & poisoning"),
]


def icd9_category(code):
    """Return the broad category name for one ICD-9 code (a string)."""
    code = str(code).strip()

    # Missing codes were labelled "Unknown" during cleaning
    if code in ("", "Unknown", "nan"):
        return "Unknown"

    # V and E codes are supplementary, not a disease category
    if code[0] in ("V", "E"):
        return "Supplementary (V/E codes)"

    number = float(code)

    # Diabetes codes are 250.00 to 250.99
    if 250 <= number < 251:
        return "Diabetes"

    for first, last, name in ICD9_RANGES:
        # "< last + 1" so that decimals like 459.9 still count as 459
        if first <= number < last + 1:
            return name

    return "Other"
