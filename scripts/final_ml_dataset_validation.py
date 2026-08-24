import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "ml"
    / "next_semester_gpa_dataset_clean.csv"
)

REPORT_PATH = (
    PROJECT_ROOT
    / "data"
    / "ml"
    / "final_ml_validation_report.txt"
)

MIN_GPA = 0.0
MAX_GPA = 4.0

EXPECTED_COLUMNS = [
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

# HELPER FUNCTIONS

report_lines = []


def report(text=""):
    """Print to terminal and store in report."""
    print(text)
    report_lines.append(str(text))


def section(title):
    report("\n" + "=" * 70)
    report(title)
    report("=" * 70)


def percentage(value, total):
    if total == 0:
        return 0.0
    return value / total * 100


# START

report("=" * 70)
report("FINAL ML DATASET VALIDATION")
report("=" * 70)

report(f"\nDataset:")
report(str(DATASET_PATH))


# CHECK FILE
if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"\nERROR: Dataset not found:\n{DATASET_PATH}"
    )


# LOAD DATASET
df = pd.read_csv(DATASET_PATH)

original_rows = len(df)

report(f"\nRows: {original_rows}")
report(f"Columns: {len(df.columns)}")

section("1. COLUMN VALIDATION")

actual_columns = list(df.columns)

report("\nActual columns:")
report(str(actual_columns))

missing_columns = [
    column
    for column in EXPECTED_COLUMNS
    if column not in df.columns
]

unexpected_columns = [
    column
    for column in df.columns
    if column not in EXPECTED_COLUMNS
]

if missing_columns:
    report("\nMISSING REQUIRED COLUMNS:")
    for column in missing_columns:
        report(f"  - {column}")
else:
    report("\nMissing required columns: 0")

if unexpected_columns:
    report("\nUNEXPECTED COLUMNS:")
    for column in unexpected_columns:
        report(f"  - {column}")
else:
    report("\nUnexpected columns: 0")


section("2. DATA TYPE VALIDATION")

report("\nData types:")

for column in df.columns:
    report(
        f"{column:20s} {str(df[column].dtype)}"
    )


section("3. MISSING VALUE VALIDATION")

missing_counts = df.isna().sum()

total_missing = missing_counts.sum()

report(f"\nTotal missing cells: {total_missing}")

if total_missing > 0:

    report("\nMissing values by column:")

    for column, count in missing_counts.items():

        if count > 0:
            report(
                f"{column:20s} "
                f"{count:6d} "
                f"({percentage(count, original_rows):.2f}%)"
            )

else:

    report("\nNo missing values found: PASS")


section("4. GPA RANGE VALIDATION")

gpa_columns = [
    "Previous_SGPA",
    "Current_SGPA",
    "Next_SGPA"
]

for column in gpa_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    invalid = (
        df[column].isna()
        | (df[column] < MIN_GPA)
        | (df[column] > MAX_GPA)
    )

    invalid_count = invalid.sum()

    report(
        f"{column:20s} "
        f"Invalid: {invalid_count}"
    )

    if invalid_count > 0:

        report(
            f"\nInvalid {column} records:"
        )

        report(
            df.loc[
                invalid,
                [
                    "Student_ID",
                    "Current_Year",
                    "Current_Semester",
                    column
                ]
            ].head(20).to_string(index=False)
        )


section("5. ZERO Next_SGPA VALIDATION")

zero_next = (
    df["Next_SGPA"] == 0
)

zero_count = zero_next.sum()

report(
    f"\nNext_SGPA = 0 records: {zero_count}"
)

if zero_count > 0:

    report("\nWARNING: Zero target records found:")

    report(
        df.loc[
            zero_next,
            [
                "Student_ID",
                "Current_Year",
                "Current_Semester",
                "Current_SGPA",
                "Next_SGPA"
            ]
        ].to_string(index=False)
    )

else:

    report(
        "\nZero Next_SGPA records: PASS"
    )


section("6. PREVIOUS_SGPA → CURRENT_SGPA CONSISTENCY")

consistency_results = []

for student_id, group in df.groupby("Student_ID"):

    group = group.sort_values(
        ["Current_Year", "Current_Semester"]
    )

    rows = group.to_dict("records")

    for i in range(1, len(rows)):

        previous_row = rows[i - 1]
        current_row = rows[i]

        previous_semester = previous_row[
            "Current_Semester"
        ]

        current_semester = current_row[
            "Current_Semester"
        ]

        # Only compare consecutive semesters
        if current_semester == previous_semester + 1:

            expected_previous = previous_row[
                "Current_SGPA"
            ]

            actual_previous = current_row[
                "Previous_SGPA"
            ]

            difference = abs(
                expected_previous - actual_previous
            )

            consistency_results.append({
                "Student_ID": student_id,
                "Previous_Semester": previous_semester,
                "Current_Semester": current_semester,
                "Expected_Previous_SGPA": expected_previous,
                "Actual_Previous_SGPA": actual_previous,
                "Difference": difference
            })


consistency_df = pd.DataFrame(
    consistency_results
)

if len(consistency_df) == 0:

    report(
        "\nNo consecutive semester pairs found."
    )

else:

    tolerance = 0.0001

    inconsistent = (
        consistency_df["Difference"]
        > tolerance
    )

    inconsistent_count = inconsistent.sum()

    report(
        f"\nConsecutive semester transitions checked: "
        f"{len(consistency_df)}"
    )

    report(
        f"Inconsistent Previous_SGPA values: "
        f"{inconsistent_count}"
    )

    if inconsistent_count > 0:

        report(
            "\nFirst inconsistencies:"
        )

        report(
            consistency_df.loc[
                inconsistent
            ].head(20).to_string(index=False)
        )

    else:

        report(
            "\nPrevious_SGPA consistency: PASS"
        )


section("7. CURRENT_SGPA → NEXT_SGPA CONSISTENCY")

next_results = []

for student_id, group in df.groupby("Student_ID"):

    group = group.sort_values(
        ["Current_Year", "Current_Semester"]
    )

    rows = group.to_dict("records")

    for i in range(len(rows) - 1):

        current_row = rows[i]
        next_row = rows[i + 1]

        current_semester = current_row[
            "Current_Semester"
        ]

        next_semester = next_row[
            "Current_Semester"
        ]

        if next_semester == current_semester + 1:

            expected_next = next_row[
                "Current_SGPA"
            ]

            actual_next = current_row[
                "Next_SGPA"
            ]

            difference = abs(
                expected_next - actual_next
            )

            next_results.append({
                "Student_ID": student_id,
                "Current_Semester": current_semester,
                "Next_Semester": next_semester,
                "Current_SGPA": current_row[
                    "Current_SGPA"
                ],
                "Next_SGPA": actual_next,
                "Expected_Next_SGPA": expected_next,
                "Difference": difference
            })


next_df = pd.DataFrame(next_results)

if len(next_df) == 0:

    report(
        "\nNo consecutive semester transitions found."
    )

else:

    tolerance = 0.0001

    mismatched = (
        next_df["Difference"]
        > tolerance
    )

    mismatch_count = mismatched.sum()

    report(
        f"\nConsecutive transitions checked: "
        f"{len(next_df)}"
    )

    report(
        f"Next_SGPA mismatches: "
        f"{mismatch_count}"
    )

    if mismatch_count > 0:

        report(
            "\nFirst mismatches:"
        )

        report(
            next_df.loc[
                mismatched
            ].head(20).to_string(index=False)
        )

    else:

        report(
            "\nCurrent_SGPA → Next_SGPA consistency: PASS"
        )


section("8. DUPLICATE STUDENT-SEMESTER CHECK")

duplicate_columns = [
    "Student_ID",
    "Current_Year",
    "Current_Semester"
]

duplicates = df.duplicated(
    subset=duplicate_columns,
    keep=False
)

duplicate_count = duplicates.sum()

duplicate_groups = (
    df.loc[
        duplicates,
        duplicate_columns
    ]
    .drop_duplicates()
)

report(
    f"\nDuplicate rows: {duplicate_count}"
)

report(
    f"Duplicate student-semester groups: "
    f"{len(duplicate_groups)}"
)

if len(duplicate_groups) > 0:

    report("\nDuplicate groups:")

    report(
        duplicate_groups
        .head(20)
        .to_string(index=False)
    )

else:

    report(
        "\nDuplicate Student + Semester: PASS"
    )


section("9. SEMESTER RANGE VALIDATION")

invalid_semester = (
    df["Current_Semester"] < 1
) | (
    df["Current_Semester"] > 8
)

invalid_year = (
    df["Current_Year"] < 1
) | (
    df["Current_Year"] > 4
)

report(
    f"\nInvalid semester values: "
    f"{invalid_semester.sum()}"
)

report(
    f"Invalid year values: "
    f"{invalid_year.sum()}"
)

if invalid_semester.sum() > 0:

    report(
        df.loc[
            invalid_semester
        ].head(20).to_string(index=False)
    )

if invalid_year.sum() > 0:

    report(
        df.loc[
            invalid_year
        ].head(20).to_string(index=False)
    )


section("10. YEAR / SEMESTER LOGIC")

expected_semesters = {
    1: {1, 2},
    2: {3, 4},
    3: {5, 6},
    4: {7, 8}
}

invalid_year_semester = []

for index, row in df.iterrows():

    year = int(row["Current_Year"])
    semester = int(row["Current_Semester"])

    valid = (
        year in expected_semesters
        and semester in expected_semesters[year]
    )

    if not valid:

        invalid_year_semester.append({
            "Student_ID": row["Student_ID"],
            "Current_Year": year,
            "Current_Semester": semester
        })

report(
    f"\nInvalid Year/Semester combinations: "
    f"{len(invalid_year_semester)}"
)

if invalid_year_semester:

    report(
        pd.DataFrame(
            invalid_year_semester
        ).head(20).to_string(index=False)
    )

else:

    report(
        "\nYear/Semester logic: PASS"
    )


section("11. STUDENT SEMESTER COVERAGE")

student_counts = (
    df.groupby("Student_ID")
    .size()
)

report(
    f"\nUnique students: "
    f"{student_counts.size}"
)

report(
    f"Minimum records per student: "
    f"{student_counts.min()}"
)

report(
    f"Maximum records per student: "
    f"{student_counts.max()}"
)

report(
    f"Average records per student: "
    f"{student_counts.mean():.2f}"
)

report("\nRecords per student distribution:")

report(
    student_counts.value_counts()
    .sort_index()
    .to_string()
)

section("12. REPEATED_COURSES VALIDATION")

df["Repeated_Courses"] = pd.to_numeric(
    df["Repeated_Courses"],
    errors="coerce"
)

invalid_repeated = (
    df["Repeated_Courses"].isna()
    | (df["Repeated_Courses"] < 0)
)

report(
    f"\nInvalid Repeated_Courses values: "
    f"{invalid_repeated.sum()}"
)

if invalid_repeated.sum() > 0:

    report(
        df.loc[
            invalid_repeated,
            [
                "Student_ID",
                "Current_Semester",
                "Repeated_Courses"
            ]
        ].head(20).to_string(index=False)
    )

else:

    report(
        "\nRepeated_Courses range: PASS"
    )

report(
    f"\nMaximum Repeated_Courses: "
    f"{df['Repeated_Courses'].max()}"
)

section("13. CATEGORICAL VALUE VALIDATION")

categorical_columns = [
    "Gender"
]

for column in categorical_columns:

    report(
        f"\n{column} unique values:"
    )

    report(
        df[column]
        .value_counts(dropna=False)
        .to_string()
    )


section("14. INTAKE VALIDATION")

report(
    "\nUnique Intake values:"
)

report(
    df["Intake"]
    .value_counts()
    .sort_index()
    .to_string()
)

section("15. DEGREE VALIDATION")

report(
    "\nUnique Degree_ID values:"
)

report(
    df["Degree_ID"]
    .value_counts()
    .sort_index()
    .to_string()
)

section("16. Next_SGPA TARGET DISTRIBUTION")

target = df["Next_SGPA"]

report("\nDescriptive statistics:")

report(
    target.describe().to_string()
)

bins = [
    0,
    1,
    2,
    2.5,
    3,
    3.5,
    4
]

distribution = pd.cut(
    target,
    bins=bins,
    include_lowest=True
).value_counts().sort_index()

report("\nDistribution:")

report(
    distribution.to_string()
)

target_percentage = (
    distribution / len(df) * 100
).round(2)

report("\nPercentage distribution:")

report(
    target_percentage.to_string()
)

section("17. NUMERIC FEATURE STATISTICS")

numeric_columns = [
    "Previous_SGPA",
    "Current_SGPA",
    "Repeated_Courses",
    "Next_SGPA"
]

report(
    df[numeric_columns]
    .describe()
    .round(4)
    .to_string()
)

section("18. CORRELATION ANALYSIS")

correlation_columns = [
    "Previous_SGPA",
    "Current_SGPA",
    "Repeated_Courses",
    "Next_SGPA"
]

correlation_matrix = (
    df[correlation_columns]
    .corr()
    .round(4)
)

report(
    correlation_matrix.to_string()
)

section("19. CORRELATION WITH Next_SGPA")

target_correlations = (
    correlation_matrix["Next_SGPA"]
    .drop("Next_SGPA")
    .sort_values(
        ascending=False
    )
)

report(
    target_correlations.to_string()
)

section("20. TARGET LEAKAGE CHECK")

leakage_columns = []

for column in df.columns:

    if column == "Next_SGPA":
        continue

    if pd.api.types.is_numeric_dtype(
        df[column]
    ):

        valid = (
            df[column].notna()
            & df["Next_SGPA"].notna()
        )

        if valid.sum() > 0:

            difference = (
                df.loc[valid, column]
                - df.loc[valid, "Next_SGPA"]
            ).abs()

            identical_count = (
                difference <= 0.0001
            ).sum()

            identical_percentage = (
                identical_count
                / valid.sum()
                * 100
            )

            if identical_percentage >= 95:

                leakage_columns.append(
                    (
                        column,
                        identical_percentage
                    )
                )

            report(
                f"{column:20s} "
                f"Identical to target: "
                f"{identical_percentage:.2f}%"
            )

if leakage_columns:

    report(
        "\nPOTENTIAL LEAKAGE DETECTED:"
    )

    for column, value in leakage_columns:

        report(
            f"  {column}: "
            f"{value:.2f}% identical to Next_SGPA"
        )

else:

    report(
        "\nNo obvious numeric target leakage detected."
    )


section("21. CURRENT_SGPA = NEXT_SGPA CHECK")

same_current_next = (
    np.isclose(
        df["Current_SGPA"],
        df["Next_SGPA"],
        atol=0.0001
    )
)

same_count = same_current_next.sum()

report(
    f"\nSame Current_SGPA and Next_SGPA: "
    f"{same_count}"
)

report(
    f"Percentage: "
    f"{percentage(same_count, len(df)):.2f}%"
)

section("22. PREVIOUS_SGPA = CURRENT_SGPA CHECK")

same_previous_current = (
    np.isclose(
        df["Previous_SGPA"],
        df["Current_SGPA"],
        atol=0.0001
    )
)

same_count = same_previous_current.sum()

report(
    f"\nSame Previous_SGPA and Current_SGPA: "
    f"{same_count}"
)

report(
    f"Percentage: "
    f"{percentage(same_count, len(df)):.2f}%"
)

section("23. OUTLIER CHECK")

for column in [
    "Previous_SGPA",
    "Current_SGPA",
    "Next_SGPA"
]:

    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)

    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outliers = (
        (df[column] < lower)
        | (df[column] > upper)
    )

    report(
        f"\n{column}:"
    )

    report(
        f"  Q1: {q1:.4f}"
    )

    report(
        f"  Q3: {q3:.4f}"
    )

    report(
        f"  IQR: {iqr:.4f}"
    )

    report(
        f"  Lower bound: {lower:.4f}"
    )

    report(
        f"  Upper bound: {upper:.4f}"
    )

    report(
        f"  Outliers: {outliers.sum()}"
    )


section("24. FINAL VALIDATION SUMMARY")

checks = {}

checks["Required columns"] = (
    len(missing_columns) == 0
)

checks["No missing values"] = (
    total_missing == 0
)

checks["GPA values valid"] = (
    all(
        (
            df[column].notna()
            & (df[column] >= MIN_GPA)
            & (df[column] <= MAX_GPA)
        ).all()
        for column in gpa_columns
    )
)

checks["No zero Next_SGPA"] = (
    zero_count == 0
)

checks["No duplicate Student + Semester"] = (
    duplicate_count == 0
)

checks["Valid year/semester"] = (
    invalid_semester.sum() == 0
    and invalid_year.sum() == 0
)

checks["Valid year/semester combination"] = (
    len(invalid_year_semester) == 0
)

checks["Previous_SGPA consistency"] = (
    len(consistency_df) == 0
    or inconsistent_count == 0
)

checks["Next_SGPA consistency"] = (
    len(next_df) == 0
    or mismatch_count == 0
)

checks["Repeated_Courses valid"] = (
    invalid_repeated.sum() == 0
)

report("\nValidation checks:")

for name, passed in checks.items():

    status = "PASS" if passed else "CHECK"

    report(
        f"{name:45s} [{status}]"
    )


passed_count = sum(
    checks.values()
)

total_checks = len(checks)

report(
    f"\nPassed: "
    f"{passed_count}/{total_checks}"
)

report("\n" + "=" * 70)
report("INTERPRETATION")
report("=" * 70)

report(
    """
This validation checks structural and logical quality of the next-semester GPA prediction dataset.

A CHECK result does not automatically mean that the dataset is wrong. Some checks, especially GPA correlations, identical GPA values, and IQR outliers, require interpretation rather than automatic deletion of records.

The dataset should NOT be artificially balanced based only on the target distribution.

Next_SGPA is the prediction target and must NOT be included as an input feature during model training.
"""
)

with open(
    REPORT_PATH,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "\n".join(report_lines)
    )

report("\n" + "=" * 70)
report("VALIDATION COMPLETE")
report("=" * 70)

report(
    f"\nReport saved to:\n{REPORT_PATH}"
)