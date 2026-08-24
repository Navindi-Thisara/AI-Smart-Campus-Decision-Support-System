import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_PATH = PROJECT_ROOT / "data" / "ml" / "next_semester_gpa_dataset.csv"

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "ml"
    / "next_semester_gpa_dataset_clean.csv"
)

REPORT_PATH = (
    PROJECT_ROOT
    / "data"
    / "ml"
    / "next_sgpa_cleaning_report.csv"
)

MIN_GPA = 0.0
MAX_GPA = 4.0

# LOAD DATA
print("=" * 70)
print("NEXT_SGPA VALIDATION AND CLEANING")
print("=" * 70)

print("\nInput file:")
print(INPUT_PATH)

if not INPUT_PATH.exists():
    raise FileNotFoundError(
        f"\nERROR: Input file was not found:\n{INPUT_PATH}"
    )

df = pd.read_csv(INPUT_PATH)

print(f"\nOriginal rows: {len(df)}")

required_columns = [
    "Student_ID",
    "Degree_ID",
    "Intake",
    "Gender",
    "Current_Year",
    "Current_Semester",
    "Previous_SGPA",
    "Current_SGPA",
    "Repeated_Courses",
    "Next_SGPA"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        "\nERROR: Required columns are missing:\n"
        + "\n".join(missing_columns)
    )

print("\nRequired columns: OK")

# CHECK MISSING VALUES
print("\n" + "=" * 70)
print("MISSING VALUE CHECK")
print("=" * 70)

missing_next = df["Next_SGPA"].isna()

print(
    f"Missing Next_SGPA: {missing_next.sum()}"
)

# CHECK INVALID GPA VALUES
print("\n" + "=" * 70)
print("NEXT_SGPA RANGE CHECK")
print("=" * 70)

# Convert to numeric safely
df["Next_SGPA"] = pd.to_numeric(
    df["Next_SGPA"],
    errors="coerce"
)

invalid_missing = df["Next_SGPA"].isna()

invalid_below = (
    df["Next_SGPA"] < MIN_GPA
)

invalid_above = (
    df["Next_SGPA"] > MAX_GPA
)

invalid_zero = (
    df["Next_SGPA"] == 0
)

invalid_mask = (
    invalid_missing
    | invalid_below
    | invalid_above
)

print(
    f"Below {MIN_GPA}: "
    f"{invalid_below.sum()}"
)

print(
    f"Above {MAX_GPA}: "
    f"{invalid_above.sum()}"
)

print(
    f"Missing/non-numeric: "
    f"{invalid_missing.sum()}"
)

print(
    f"Next_SGPA = 0: "
    f"{invalid_zero.sum()}"
)


# DISPLAY ZERO-GPA RECORDS
print("\n" + "=" * 70)
print("ZERO Next_SGPA RECORDS")
print("=" * 70)

zero_records = df[
    df["Next_SGPA"] == 0
].copy()

if len(zero_records) > 0:

    print(
        zero_records[
            [
                "Student_ID",
                "Current_Year",
                "Current_Semester",
                "Current_SGPA",
                "Repeated_Courses",
                "Next_SGPA"
            ]
        ].to_string(index=False)
    )

else:

    print("No zero Next_SGPA records found.")


print("\n" + "=" * 70)
print("CLEANING DATA")
print("=" * 70)

invalid_target_mask = (
    df["Next_SGPA"].isna()
    | (df["Next_SGPA"] <= MIN_GPA)
    | (df["Next_SGPA"] > MAX_GPA)
)

removed_rows = df[invalid_target_mask].copy()

clean_df = df[
    ~invalid_target_mask
].copy()

print(
    f"\nRows removed: {len(removed_rows)}"
)

if len(removed_rows) > 0:

    print("\nRemoved records:")

    print(
        removed_rows[
            [
                "Student_ID",
                "Current_Year",
                "Current_Semester",
                "Current_SGPA",
                "Repeated_Courses",
                "Next_SGPA"
            ]
        ].to_string(index=False)
    )

else:

    print("No records needed to be removed.")


print("\n" + "=" * 70)
print("DUPLICATE CHECK")
print("=" * 70)

duplicate_columns = [
    "Student_ID",
    "Current_Year",
    "Current_Semester"
]

duplicates = clean_df.duplicated(
    subset=duplicate_columns,
    keep=False
)

duplicate_count = duplicates.sum()

print(
    f"Duplicate Student + Semester rows: "
    f"{duplicate_count}"
)

# CHECK GPA RANGE AFTER CLEANING
print("\n" + "=" * 70)
print("POST-CLEANING VALIDATION")
print("=" * 70)

print(
    f"\nClean dataset rows: "
    f"{len(clean_df)}"
)

print(
    f"Removed rows: "
    f"{len(df) - len(clean_df)}"
)

print(
    f"Final minimum Next_SGPA: "
    f"{clean_df['Next_SGPA'].min():.4f}"
)

print(
    f"Final maximum Next_SGPA: "
    f"{clean_df['Next_SGPA'].max():.4f}"
)

print(
    f"Final mean Next_SGPA: "
    f"{clean_df['Next_SGPA'].mean():.4f}"
)

print(
    f"Final median Next_SGPA: "
    f"{clean_df['Next_SGPA'].median():.4f}"
)

print(
    f"Final missing Next_SGPA: "
    f"{clean_df['Next_SGPA'].isna().sum()}"
)

print(
    f"Final zero Next_SGPA: "
    f"{(clean_df['Next_SGPA'] == 0).sum()}"
)

# SAVE CLEAN DATASET
clean_df.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\n" + "=" * 70)
print("CLEAN DATASET SAVED")
print("=" * 70)

print(
    f"\nSaved to:\n{OUTPUT_PATH}"
)

# CREATE CLEANING REPORT
if len(removed_rows) > 0:

    report = removed_rows[
        [
            "Student_ID",
            "Degree_ID",
            "Intake",
            "Gender",
            "Current_Year",
            "Current_Semester",
            "Previous_SGPA",
            "Current_SGPA",
            "Repeated_Courses",
            "Next_SGPA"
        ]
    ].copy()

    report["Removal_Reason"] = report["Next_SGPA"].apply(
        lambda x:
            "Missing Next_SGPA"
            if pd.isna(x)
            else "Next_SGPA <= 0"
            if x <= 0
            else "Next_SGPA > 4"
    )

else:

    report = pd.DataFrame(
        columns=[
            "Student_ID",
            "Degree_ID",
            "Intake",
            "Gender",
            "Current_Year",
            "Current_Semester",
            "Previous_SGPA",
            "Current_SGPA",
            "Repeated_Courses",
            "Next_SGPA",
            "Removal_Reason"
        ]
    )

report.to_csv(
    REPORT_PATH,
    index=False
)

print(
    f"\nCleaning report saved to:\n{REPORT_PATH}"
)

print("\n" + "=" * 70)
print("FINAL Next_SGPA DISTRIBUTION")
print("=" * 70)

distribution = pd.cut(
    clean_df["Next_SGPA"],
    bins=[
        0,
        1,
        2,
        2.5,
        3,
        3.5,
        4
    ],
    include_lowest=True
).value_counts().sort_index()

print(distribution)

print("\nPercentage distribution:")

percentage = (
    distribution / len(clean_df) * 100
).round(2)

print(percentage)

print("\n" + "=" * 70)
print("CLEANING COMPLETE")
print("=" * 70)