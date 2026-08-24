import pandas as pd

CSV_PATH = "data/ml/next_semester_gpa_dataset_clean.csv"

df = pd.read_csv(CSV_PATH)

print("=" * 50)
print("NEXT_SGPA DISTRIBUTION VALIDATION")
print("=" * 50)

print("\nRows:", len(df))

print("\n--- Columns ---")
print(df.columns.tolist())

print("\n--- Next_SGPA Statistics ---")
print(df["Next_SGPA"].describe())

print("\n--- Invalid GPA Values ---")
invalid = df[
    (df["Next_SGPA"] < 0) |
    (df["Next_SGPA"] > 4)
]

print("Invalid rows:", len(invalid))

if len(invalid) > 0:
    print(invalid[["Student_ID", "Next_SGPA"]].head(20))

print("\n--- Missing Values ---")
print("Missing Next_SGPA:", df["Next_SGPA"].isna().sum())

print("\n--- Next_SGPA Distribution ---")

distribution = pd.cut(
    df["Next_SGPA"],
    bins=[0, 1, 2, 2.5, 3, 3.5, 4],
    include_lowest=True
).value_counts().sort_index()

print(distribution)

print("\n--- Percentage Distribution ---")
print((distribution / len(df) * 100).round(2))

print("\n--- Same as Current_SGPA ---")

same_current = (
    df["Next_SGPA"] == df["Current_SGPA"]
).mean()

print(f"{same_current:.2%}")

print("\n--- Same as Previous_SGPA ---")

same_previous = (
    df["Next_SGPA"] == df["Previous_SGPA"]
).mean()

print(f"{same_previous:.2%}")

print("\n--- GPA Correlations ---")

print(
    df[
        ["Previous_SGPA", "Current_SGPA", "Next_SGPA"]
    ].corr()
)

print("\n" + "=" * 50)
print("VALIDATION COMPLETE")
print("=" * 50)