import pandas as pd

ML_PATH = "data/ml/next_semester_gpa_dataset_clean.csv"
STUDENTS_PATH = "scripts/generated_dataset/students.csv"

print("=" * 70)
print("NEXT_SGPA SOURCE VALIDATION")
print("=" * 70)

# Load datasets
ml = pd.read_csv(ML_PATH)
students = pd.read_csv(STUDENTS_PATH)

print(f"\nML dataset rows: {len(ml)}")
print(f"Students dataset rows: {len(students)}")

# Create lookup table for the next semester
next_semester = students[
    [
        "Student_ID",
        "Current_Year",
        "Current_Semester",
        "Current_SGPA"
    ]
].copy()

# Rename fields so they represent the target semester
next_semester = next_semester.rename(
    columns={
        "Current_Year": "Next_Year",
        "Current_Semester": "Next_Semester",
        "Current_SGPA": "Expected_Next_SGPA"
    }
)

# For each ML row, calculate the expected next semester
def get_next_year_semester(row):

    year = row["Current_Year"]
    semester = row["Current_Semester"]

    if semester in [2, 4, 6]:
        return year + 1, semester + 1

    return year, semester + 1


ml[["Next_Year", "Next_Semester"]] = ml.apply(
    get_next_year_semester,
    axis=1,
    result_type="expand"
)

# Merge ML dataset with expected next semester GPA
merged = ml.merge(
    next_semester,
    on=["Student_ID", "Next_Year", "Next_Semester"],
    how="left"
)

# Calculate difference
merged["Difference"] = (
    merged["Next_SGPA"] -
    merged["Expected_Next_SGPA"]
).abs()

# Allow small floating-point differences
TOLERANCE = 0.0001

merged["Status"] = "MATCH"

merged.loc[
    merged["Expected_Next_SGPA"].isna(),
    "Status"
] = "NO_NEXT_SEMESTER"

merged.loc[
    (
        merged["Expected_Next_SGPA"].notna()
        & (merged["Difference"] > TOLERANCE)
    ),
    "Status"
] = "MISMATCH"


# Results
total = len(merged)

matches = (merged["Status"] == "MATCH").sum()
mismatches = (merged["Status"] == "MISMATCH").sum()
missing = (merged["Status"] == "NO_NEXT_SEMESTER").sum()

print("\n" + "=" * 70)
print("VALIDATION RESULTS")
print("=" * 70)

print(f"\nTotal ML records:       {total}")
print(f"Correct Next_SGPA:      {matches}")
print(f"Mismatched Next_SGPA:   {mismatches}")
print(f"No next semester:       {missing}")

print("\nPercentages:")

print(
    f"Correct:    {matches / total * 100:.2f}%"
)

print(
    f"Mismatched: {mismatches / total * 100:.2f}%"
)

print(
    f"Missing:    {missing / total * 100:.2f}%"
)


# Show mismatches
mismatch_df = merged[
    merged["Status"] == "MISMATCH"
].copy()

print("\n" + "=" * 70)
print("MISMATCH EXAMPLES")
print("=" * 70)

if len(mismatch_df) > 0:

    print(
        mismatch_df[
            [
                "Student_ID",
                "Current_Year",
                "Current_Semester",
                "Current_SGPA",
                "Next_SGPA",
                "Expected_Next_SGPA",
                "Difference"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

else:
    print("\nNo mismatches found.")


# Show missing next semester
missing_df = merged[
    merged["Status"] == "NO_NEXT_SEMESTER"
].copy()

print("\n" + "=" * 70)
print("MISSING NEXT SEMESTER EXAMPLES")
print("=" * 70)

if len(missing_df) > 0:

    print(
        missing_df[
            [
                "Student_ID",
                "Current_Year",
                "Current_Semester",
                "Current_SGPA",
                "Next_SGPA"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

else:
    print("\nNo missing next semesters.")


# Specifically check S1793
print("\n" + "=" * 70)
print("S1793 CHECK")
print("=" * 70)

s1793 = merged[
    merged["Student_ID"] == "S1793"
]

if len(s1793) > 0:

    print(
        s1793[
            [
                "Student_ID",
                "Current_Year",
                "Current_Semester",
                "Current_SGPA",
                "Next_SGPA",
                "Expected_Next_SGPA",
                "Difference",
                "Status"
            ]
        ].to_string(index=False)
    )
else:
    print("S1793 not found.")

print("\n" + "=" * 70)
print("VALIDATION COMPLETE")
print("=" * 70)