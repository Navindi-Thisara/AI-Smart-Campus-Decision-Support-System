import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "scripts" / "generated_dataset"

STUDENTS_FILE = DATA_DIR / "students.csv"
RESULTS_FILE = DATA_DIR / "student_results.csv"
DEGREES_FILE = DATA_DIR / "degrees.csv"
MODULES_FILE = DATA_DIR / "course_modules.csv"
DEGREE_MODULES_FILE = DATA_DIR / "degree_modules.csv"

EXPECTED_STUDENT_COUNT = 3000
EXPECTED_FIRST_ID = "S0001"
EXPECTED_LAST_ID = "S3000"

EXPECTED_INTAKE_BY_YEAR = {
    1: 42,
    2: 41,
    3: 40,
    4: 39
}

SEMESTERS_BY_YEAR = {
    1: [1, 2],
    2: [3, 4],
    3: [5, 6],
    4: [7, 8]
}

VALID_GENDERS = {
    "Male",
    "Female"
}

VALID_YEARS = {
    1,
    2,
    3,
    4
}

VALID_SEMESTERS = {
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8
}

VALID_FEE_STATUS = {
    "Yes",
    "No"
}

VALID_ATTENDANCE_APPROVAL = {
    "Yes",
    "No"
}

VALID_ELIGIBILITY = {
    "Eligible",
    "Not Eligible"
}

VALID_RESULT_STATUS = {
    "Pass",
    "Fail"
}

VALID_RISK = {
    "Low Risk",
    "Medium Risk",
    "High Risk"
}

REQUIRED_STUDENT_COLUMNS = [
    "Student_ID",
    "Registration_No",
    "Name",
    "Gender",
    "Intake",
    "Degree_ID",
    "Current_Year",
    "Current_Semester",
    "Current_SGPA",
    "Previous_SGPA",
    "FGPA",
    "Attendance_Percentage",
    "Attendance_Approved",
    "Fee_Paid",
    "Exam_Eligibility",
    "Repeated_Courses",
    "Student_Status",
    "Academic_Risk"
]

REQUIRED_RESULT_COLUMNS = [
    "Result_ID",
    "Student_ID",
    "Course_Code",
    "Academic_Year",
    "Semester",
    "Attempt",
    "Marks",
    "Grade",
    "Grade_Point",
    "Result_Status"
]

PASS_COUNT = 0
WARNING_COUNT = 0
ERROR_COUNT = 0

def passed(message):
    global PASS_COUNT
    PASS_COUNT += 1
    print(f"[PASS] {message}")


def warning(message):
    global WARNING_COUNT
    WARNING_COUNT += 1
    print(f"[WARNING] {message}")


def error(message):
    global ERROR_COUNT
    ERROR_COUNT += 1
    print(f"[ERROR] {message}")


def section(title):
    print()
    print("=" * 75)
    print(title)
    print("=" * 75)


section("1. FILE EXISTENCE CHECK")

required_files = [
    STUDENTS_FILE,
    RESULTS_FILE,
    DEGREES_FILE,
    MODULES_FILE,
    DEGREE_MODULES_FILE
]

for file in required_files:
    if file.exists():
        passed(f"File exists: {file.name}")

    else:
        error(f"Missing file: {file}")

        print()
        print("Dataset quality check cannot continue.")
        raise SystemExit(1)



section("2. LOADING DATASET")

try:
    students = pd.read_csv(
        STUDENTS_FILE
    )

    results = pd.read_csv(
        RESULTS_FILE
    )

    degrees = pd.read_csv(
        DEGREES_FILE
    )

    modules = pd.read_csv(
        MODULES_FILE
    )

    degree_modules = pd.read_csv(
        DEGREE_MODULES_FILE
    )

    passed("All CSV files loaded successfully.")

except Exception as exc:
    error(f"Could not load CSV files: {exc}")
    raise SystemExit(1)


section("3. DATASET SIZE")

print(
    f"Students       : {len(students):,}"
)

print(
    f"Results        : {len(results):,}"
)

print(
    f"Degrees        : {len(degrees):,}"
)

print(
    f"Modules        : {len(modules):,}"
)

print(
    f"Degree Modules : {len(degree_modules):,}"
)


if len(students) == EXPECTED_STUDENT_COUNT:
    passed(
        f"Exactly {EXPECTED_STUDENT_COUNT:,} students found."
    )

else:
    error(
        f"Expected {EXPECTED_STUDENT_COUNT:,} students "
        f"but found {len(students):,}."
    )


section("4. REQUIRED COLUMN CHECK")

def check_columns(
    dataframe,
    required_columns,
    filename
):
    missing = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]
    if missing:
        error(
            f"{filename} missing columns: {missing}"
        )

    else:
        passed(
            f"{filename} contains all required columns."
        )


check_columns(
    students,
    REQUIRED_STUDENT_COLUMNS,
    "students.csv"
)

check_columns(
    results,
    REQUIRED_RESULT_COLUMNS,
    "student_results.csv"
)

student_numeric_columns = [
    "Intake",
    "Current_Year",
    "Current_Semester",
    "Current_SGPA",
    "Previous_SGPA",
    "FGPA",
    "Attendance_Percentage",
    "Repeated_Courses"
]

result_numeric_columns = [
    "Academic_Year",
    "Semester",
    "Attempt",
    "Marks",
    "Grade_Point"
]

for column in student_numeric_columns:
    if column in students.columns:
        students[column] = pd.to_numeric(
            students[column],
            errors="coerce"
        )


for column in result_numeric_columns:
    if column in results.columns:
        results[column] = pd.to_numeric(
            results[column],
            errors="coerce"
        )


section("5. MISSING VALUE CHECK")

student_missing = students.isna().sum()

student_missing = student_missing[
    student_missing > 0
]

if student_missing.empty:
    passed(
        "students.csv contains no missing values."
    )

else:
    error(
        "Missing values found in students.csv:"
    )
    print(student_missing)


result_missing = results.isna().sum()

result_missing = result_missing[
    result_missing > 0
]

if result_missing.empty:
    passed(
        "student_results.csv contains no missing values."
    )

else:
    error(
        "Missing values found in student_results.csv:"
    )

    print(result_missing)


section("6. STUDENT ID CHECK")

student_ids = students[
    "Student_ID"
].astype(str)

if student_ids.is_unique:
    passed(
        "All Student_ID values are unique."
    )

else:
    duplicate_ids = (
        student_ids[
            student_ids.duplicated(keep=False)
        ]
        .unique()
        .tolist()
    )

    error(
        f"Duplicate Student_ID values found: "
        f"{duplicate_ids[:20]}"
    )


expected_ids = {
    f"S{i:04d}"
    for i in range(
        1,
        EXPECTED_STUDENT_COUNT + 1
    )
}

actual_ids = set(student_ids)

missing_ids = expected_ids - actual_ids
extra_ids = actual_ids - expected_ids

if not missing_ids and not extra_ids:
    passed(
        "Student IDs contain exactly S0001-S3000."
    )

else:
    if missing_ids:
        error(
            f"Missing Student IDs: "
            f"{sorted(missing_ids)[:20]}"
        )

    if extra_ids:
        error(
            f"Unexpected Student IDs: "
            f"{sorted(extra_ids)[:20]}"
        )


section("7. RESULT ID CHECK")

result_ids = results[
    "Result_ID"
].astype(str)

if result_ids.is_unique:
    passed(
        "All Result_ID values are unique."
    )

else:
    duplicate_result_ids = (
        result_ids[
            result_ids.duplicated(keep=False)
        ]
        .unique()
        .tolist()
    )

    error(
        f"Duplicate Result_ID values found: "
        f"{duplicate_result_ids[:20]}"
    )


section("8. STUDENT-RESULT RELATIONSHIP CHECK")

student_id_set = set(
    students["Student_ID"].astype(str)
)

result_student_ids = set(
    results["Student_ID"].astype(str)
)

unknown_result_students = (
    result_student_ids
    -
    student_id_set
)

if not unknown_result_students:
    passed(
        "Every result belongs to an existing student."
    )

else:
    error(
        "Results exist for students who are not in "
        "students.csv:"
    )

    print(
        sorted(
            unknown_result_students
        )[:50]
    )


section("9. EVERY STUDENT HAS RESULTS CHECK")

result_counts = (
    results
    .groupby("Student_ID")
    .size()
)

students_without_results = (
    students[
        ~students["Student_ID"].isin(
            result_counts.index
        )
    ]
)

if students_without_results.empty:
    passed(
        "Every student has at least one result."
    )

else:
    warning(
        f"{len(students_without_results)} students "
        "have no result records."
    )

    print(
        students_without_results[
            [
                "Student_ID",
                "Current_Year",
                "Current_Semester",
                "Degree_ID"
            ]
        ].head(20).to_string(index=False)
    )


section("10. DEGREE RELATIONSHIP CHECK")

valid_degree_ids = set(
    degrees["Degree_ID"].astype(str)
)

student_degree_ids = set(
    students["Degree_ID"].astype(str)
)

unknown_student_degrees = (
    student_degree_ids
    -
    valid_degree_ids
)

if not unknown_student_degrees:
    passed(
        "Every student has a valid Degree_ID."
    )

else:
    error(
        f"Unknown student Degree_ID values: "
        f"{unknown_student_degrees}"
    )


section("11. COURSE RELATIONSHIP CHECK")

valid_course_codes = set(
    modules["Course_Code"].astype(str)
)

result_course_codes = set(
    results["Course_Code"].astype(str)
)

unknown_courses = (
    result_course_codes
    -
    valid_course_codes
)

if not unknown_courses:
    passed(
        "Every result references an existing course."
    )

else:
    error(
        f"Unknown Course_Code values: "
        f"{sorted(unknown_courses)[:30]}"
    )


section("12. DEGREE-COURSE RELATIONSHIP CHECK")

valid_degree_course_pairs = set(
    zip(
        degree_modules[
            "Degree_ID"
        ].astype(str),

        degree_modules[
            "Course_Code"
        ].astype(str)
    )
)

results_degree = (
    results[
        [
            "Student_ID",
            "Course_Code"
        ]
    ]

    .merge(
        students[
            [
                "Student_ID",
                "Degree_ID"
            ]
        ],

        on="Student_ID",
        how="left"
    )
)

results_degree["pair"] = list(
    zip(
        results_degree[
            "Degree_ID"
        ].astype(str),

        results_degree[
            "Course_Code"
        ].astype(str)
    )
)

invalid_degree_courses = (
    results_degree[
        ~results_degree[
            "pair"
        ].isin(
            valid_degree_course_pairs
        )
    ]
)

if invalid_degree_courses.empty:
    passed(
        "All student results use courses belonging "
        "to the student's degree."
    )

else:
    error(
        f"{len(invalid_degree_courses)} result records "
        "have invalid Degree/Course combinations."
    )

    print(
        invalid_degree_courses.head(20).to_string(
            index=False
        )
    )


# INTAKE-YEAR CHECK
section("13. INTAKE-YEAR CONSISTENCY CHECK")

intake_errors = []

for _, row in students.iterrows():
    year = row["Current_Year"]
    intake = row["Intake"]

    expected_intake = (
        EXPECTED_INTAKE_BY_YEAR.get(
            year
        )
    )

    if expected_intake is None:
        continue

    if intake != expected_intake:

        intake_errors.append(
            (
                row["Student_ID"],
                year,
                intake,
                expected_intake
            )
        )

if not intake_errors:
    passed(
        "All students follow the required "
        "Year → Intake mapping."
    )

else:
    error(
        f"{len(intake_errors)} students have "
        "incorrect Intake/Year combinations."
    )

    print(
        "Examples:"
    )

    for item in intake_errors[:20]:

        print(
            f"Student={item[0]}, "
            f"Year={item[1]}, "
            f"Intake={item[2]}, "
            f"Expected={item[3]}"
        )


# YEAR-SEMESTER CHECK
section("14. YEAR-SEMESTER CONSISTENCY CHECK")

semester_errors = []

for _, row in students.iterrows():
    year = int(
        row["Current_Year"]
    )

    semester = int(
        row["Current_Semester"]
    )

    valid_semesters = (
        SEMESTERS_BY_YEAR.get(
            year,
            []
        )
    )

    if semester not in valid_semesters:
        semester_errors.append(
            (
                row["Student_ID"],
                year,
                semester,
                valid_semesters
            )
        )


if not semester_errors:
    passed(
        "All students have valid "
        "Year/Semester combinations."
    )

else:
    error(
        f"{len(semester_errors)} students have "
        "invalid Year/Semester combinations."
    )

    for item in semester_errors[:20]:
        print(
            f"Student={item[0]}, "
            f"Year={item[1]}, "
            f"Semester={item[2]}, "
            f"Allowed={item[3]}"
        )


# RESULT SEMESTER RANGE
section("15. RESULT SEMESTER RANGE CHECK")

invalid_result_semesters = results[
    ~results["Semester"].isin(
        VALID_SEMESTERS
    )
]

if invalid_result_semesters.empty:
    passed(
        "All result semesters are between 1 and 8."
    )

else:
    error(
        f"{len(invalid_result_semesters)} results "
        "have invalid semester values."
    )


# RESULT ACADEMIC YEAR RANGE
section("16. RESULT ACADEMIC YEAR CHECK")

invalid_result_years = results[
    ~results["Academic_Year"].isin(
        VALID_YEARS
    )
]

if invalid_result_years.empty:
    passed(
        "All result Academic_Year values are valid."
    )

else:
    error(
        f"{len(invalid_result_years)} results "
        "have invalid Academic_Year values."
    )

# RESULT SEMESTER VS ACADEMIC YEAR
section("17. RESULT YEAR-SEMESTER CONSISTENCY")

result_semester_errors = []

for _, row in results.iterrows():
    year = int(
        row["Academic_Year"]
    )

    semester = int(
        row["Semester"]
    )


    valid_semesters = (
        SEMESTERS_BY_YEAR.get(
            year,
            []
        )
    )


    if semester not in valid_semesters:
        result_semester_errors.append(
            (
                row["Result_ID"],
                row["Academic_Year"],
                row["Semester"]
            )
        )


if not result_semester_errors:
    passed(
        "All result Year/Semester combinations are valid."
    )

else:
    error(
        f"{len(result_semester_errors)} result records "
        "have invalid Year/Semester combinations."
    )

    print(
        result_semester_errors[:20]
    )


# RESULTS MUST NOT EXCEED CURRENT SEMESTER
section("18. RESULT HISTORY CONSISTENCY")

result_history = (
    results[
        [
            "Student_ID",
            "Academic_Year",
            "Semester"
        ]
    ]

    .merge(
        students[
            [
                "Student_ID",
                "Current_Year",
                "Current_Semester"
            ]
        ],

        on="Student_ID",

        how="left"
    )
)

result_history["Result_Position"] = (
    (
        result_history["Academic_Year"] - 1
    )
    * 2
    +
    (
        result_history["Semester"]
        -
        (
            (result_history["Academic_Year"] - 1)
            * 2
        )
    )
)

result_history["Result_Position"] = (
    result_history["Semester"]
)

result_history["Current_Position"] = (
    result_history["Current_Semester"]
)

future_results = result_history[
    result_history["Result_Position"]
    >
    result_history["Current_Position"]
]

if future_results.empty:
    passed(
        "No student has results beyond their current semester."
    )

else:
    error(
        f"{len(future_results)} result records "
        "occur after the student's current semester."
    )

    print(
        future_results.head(20).to_string(
            index=False
        )
    )

section("19. MARK RANGE CHECK")

invalid_marks = results[
    (results["Marks"] < 0)
    |
    (results["Marks"] > 100)
]


if invalid_marks.empty:
    passed(
        "All marks are within 0-100."
    )

else:
    error(
        f"{len(invalid_marks)} results contain "
        "marks outside 0-100."
    )


def get_grade(mark):
    if mark >= 85:
        return "A+", 4.0

    elif mark >= 75:
        return "A", 4.0

    elif mark >= 70:
        return "A-", 3.7

    elif mark >= 65:
        return "B+", 3.3

    elif mark >= 60:
        return "B", 3.0

    elif mark >= 55:
        return "B-", 2.7

    elif mark >= 50:
        return "C+", 2.3

    elif mark >= 45:
        return "C", 2.0

    elif mark >= 40:
        return "C-", 1.7

    elif mark >= 35:
        return "D+", 1.3

    else:
        return "F", 0.0



section("20. GRADE / MARK CONSISTENCY")

grade_errors = []

for _, row in results.iterrows():

    expected_grade, expected_point = get_grade(
        row["Marks"]
    )

    if row["Grade"] != expected_grade:
        grade_errors.append(
            (
                row["Result_ID"],
                row["Marks"],
                row["Grade"],
                expected_grade
            )
        )
        continue


    if abs(
        float(row["Grade_Point"])
        -
        expected_point
    ) > 0.0001:
        grade_errors.append(
            (
                row["Result_ID"],
                row["Marks"],
                row["Grade_Point"],
                expected_point
            )
        )


if not grade_errors:
    passed(
        "All Grade and Grade_Point values "
        "match the Marks."
    )

else:
    error(
        f"{len(grade_errors)} grade inconsistencies found."
    )

    print(
        grade_errors[:20]
    )


section("21. RESULT STATUS CHECK")

status_errors = []

for _, row in results.iterrows():
    expected_status = (
        "Fail"
        if row["Grade"] == "F"
        else "Pass"
    )

    if row["Result_Status"] != expected_status:
        status_errors.append(
            (
                row["Result_ID"],
                row["Grade"],
                row["Result_Status"],
                expected_status
            )
        )


if not status_errors:
    passed(
        "Result_Status correctly corresponds to Grade."
    )

else:
    error(
        f"{len(status_errors)} Result_Status inconsistencies found."
    )

    print(
        status_errors[:20]
    )


section("22. GPA CONSISTENCY CHECK")

# Get course credits.
modules_gpa = modules.copy()

modules_gpa["Credits"] = pd.to_numeric(
    modules_gpa["Credits"],
    errors="coerce"
)

modules_gpa["Semester"] = pd.to_numeric(
    modules_gpa["Semester"],
    errors="coerce"
)

modules_gpa["Year"] = pd.to_numeric(
    modules_gpa["Year"],
    errors="coerce"
)

results_gpa = results.merge(
    modules_gpa[
        [
            "Course_Code",
            "Credits",
            "Year",
            "Semester"
        ]
    ],

    left_on=[
        "Course_Code",
        "Academic_Year",
        "Semester"
    ],

    right_on=[
        "Course_Code",
        "Year",
        "Semester"
    ],

    how="left"
)

missing_credits = results_gpa[
    results_gpa["Credits"].isna()
]

if not missing_credits.empty:
    error(
        f"{len(missing_credits)} results could not "
        "be matched to module credits."
    )

else:
    passed(
        "All results have valid course credits."
    )


# Calculate weighted grade points
results_gpa["Weighted_GP"] = (
    results_gpa["Grade_Point"]
    *
    results_gpa["Credits"]
)


# SGPA per student per semester
sgpa_check = (
    results_gpa
    .groupby(
        [
            "Student_ID",
            "Semester"
        ]
    )
    .agg(
        weighted_points=(
            "Weighted_GP",
            "sum"
        ),

        total_credits=(
            "Credits",
            "sum"
        )
    )
)


sgpa_check["Calculated_SGPA"] = (
    sgpa_check["weighted_points"]
    /
    sgpa_check["total_credits"]
).round(4)


gpa_errors = []


for _, student in students.iterrows():
    sid = student["Student_ID"]

    current_semester = int(
        student["Current_Semester"]
    )


    key = (
        sid,
        current_semester
    )


    if key not in sgpa_check.index:
        continue


    calculated_sgpa = sgpa_check.loc[
        key,
        "Calculated_SGPA"
    ]


    stored_sgpa = float(
        student["Current_SGPA"]
    )


    if abs(
        calculated_sgpa
        -
        stored_sgpa
    ) > 0.0002:
        gpa_errors.append(
            (
                sid,
                "Current_SGPA",
                calculated_sgpa,
                stored_sgpa
            )
        )


if not gpa_errors:
    passed(
        "Current_SGPA values are consistent "
        "with student results."
    )

else:
    error(
        f"{len(gpa_errors)} Current_SGPA mismatches found."
    )

    print(
        gpa_errors[:20]
    )

cumulative_gpa = (
    results_gpa
    .groupby("Student_ID")
    .agg(
        weighted_points=(
            "Weighted_GP",
            "sum"
        ),

        total_credits=(
            "Credits",
            "sum"
        )
    )
)

cumulative_gpa["Calculated_FGPA"] = (
    cumulative_gpa["weighted_points"]
    /
    cumulative_gpa["total_credits"]
).round(4)

fgpa_errors = []

for _, student in students.iterrows():
    sid = student["Student_ID"]


    if sid not in cumulative_gpa.index:
        continue


    calculated_fgpa = cumulative_gpa.loc[
        sid,
        "Calculated_FGPA"
    ]

    stored_fgpa = float(
        student["FGPA"]
    )


    if abs(
        calculated_fgpa
        -
        stored_fgpa
    ) > 0.0002:

        fgpa_errors.append(
            (
                sid,
                calculated_fgpa,
                stored_fgpa
            )
        )


if not fgpa_errors:
    passed(
        "FGPA values are consistent with results."
    )

else:
    error(
        f"{len(fgpa_errors)} FGPA mismatches found."
    )

    print(
        fgpa_errors[:20]
    )

section("23. GPA RANGE CHECK")

for column in [
    "Current_SGPA",
    "Previous_SGPA",
    "FGPA"
]:

    invalid = students[
        (students[column] < 0)
        |
        (students[column] > 4)
    ]

    if invalid.empty:
        passed(
            f"{column} values are within 0.0-4.0."
        )

    else:
        error(
            f"{len(invalid)} {column} values "
            "are outside 0.0-4.0."
        )


section("24. ATTENDANCE RANGE CHECK")

invalid_attendance = students[
    (
        students[
            "Attendance_Percentage"
        ]
        < 0
    )
    |
    (
        students[
            "Attendance_Percentage"
        ]
        > 100
    )
]

if invalid_attendance.empty:
    passed(
        "Attendance values are within 0-100%."
    )

else:
    error(
        f"{len(invalid_attendance)} students have "
        "invalid attendance values."
    )


section("25. CATEGORICAL VALUE CHECK")


def check_categories(
    dataframe,
    column,
    valid_values
):

    actual = set(
        dataframe[column]
        .dropna()
        .astype(str)
    )

    invalid = actual - valid_values

    if not invalid:
        passed(
            f"{column} contains only valid values."
        )

    else:
        error(
            f"{column} contains invalid values: "
            f"{invalid}"
        )


check_categories(
    students,
    "Gender",
    VALID_GENDERS
)

check_categories(
    students,
    "Attendance_Approved",
    VALID_ATTENDANCE_APPROVAL
)

check_categories(
    students,
    "Fee_Paid",
    VALID_FEE_STATUS
)

check_categories(
    students,
    "Exam_Eligibility",
    VALID_ELIGIBILITY
)

check_categories(
    students,
    "Academic_Risk",
    VALID_RISK
)

check_categories(
    results,
    "Result_Status",
    VALID_RESULT_STATUS
)

section("26. EXAM ELIGIBILITY LOGIC CHECK")

eligibility_errors = []

for _, row in students.iterrows():
    attendance = float(
        row["Attendance_Percentage"]
    )

    approved = str(
        row["Attendance_Approved"]
    )

    fee_paid = str(
        row["Fee_Paid"]
    )


    attendance_condition = (
        attendance >= 80
        or
        approved == "Yes"
    )


    fee_condition = (
        fee_paid == "Yes"
    )


    expected = (
        "Eligible"
        if (
            attendance_condition
            and
            fee_condition
        )
        else
        "Not Eligible"
    )

    if row["Exam_Eligibility"] != expected:
        eligibility_errors.append(
            (
                row["Student_ID"],
                row["Attendance_Percentage"],
                row["Attendance_Approved"],
                row["Fee_Paid"],
                row["Exam_Eligibility"],
                expected
            )
        )


if not eligibility_errors:
    passed(
        "Exam eligibility follows attendance approval "
        "and fee rules."
    )

else:
    error(
        f"{len(eligibility_errors)} exam eligibility "
        "logic errors found."
    )

    print(
        eligibility_errors[:20]
    )


section("27. REPEATED COURSE CHECK")

fail_counts = (
    results[
        results["Result_Status"] == "Fail"
    ]
    .groupby("Student_ID")
    .size()
)

repeat_errors = []

for _, student in students.iterrows():
    sid = student["Student_ID"]

    expected_repeats = int(
        fail_counts.get(
            sid,
            0
        )
    )

    stored_repeats = int(
        student["Repeated_Courses"]
    )

    if expected_repeats != stored_repeats:
        repeat_errors.append(
            (
                sid,
                expected_repeats,
                stored_repeats
            )
        )


if not repeat_errors:
    passed(
        "Repeated_Courses matches the number of failed results."
    )

else:
    error(
        f"{len(repeat_errors)} Repeated_Courses mismatches found."
    )

    print(
        repeat_errors[:20]
    )


section("28. ACADEMIC RISK CHECK")

risk_errors = []

for _, student in students.iterrows():
    fgpa = float(
        student["FGPA"]
    )

    repeats = int(
        student["Repeated_Courses"]
    )


    risk_score = 0


    if fgpa < 2.0:

        risk_score += 2

    elif fgpa < 3.0:

        risk_score += 1


    if repeats >= 2:

        risk_score += 2


    if risk_score >= 3:

        expected_risk = "High Risk"

    elif risk_score >= 1:

        expected_risk = "Medium Risk"

    else:
        expected_risk = "Low Risk"


    if student["Academic_Risk"] != expected_risk:
        risk_errors.append(
            (
                student["Student_ID"],
                fgpa,
                repeats,
                student["Academic_Risk"],
                expected_risk
            )
        )


if not risk_errors:
    passed(
        "Academic_Risk follows the defined risk rules."
    )

else:
    error(
        f"{len(risk_errors)} Academic_Risk mismatches found."
    )

    print(
        risk_errors[:20]
    )


section("29. RESULT DUPLICATE CHECK")

duplicate_result_rows = results[
    results.duplicated(
        subset=[
            "Student_ID",
            "Course_Code",
            "Academic_Year",
            "Semester",
            "Attempt"
        ],
        keep=False
    )
]

if duplicate_result_rows.empty:
    passed(
        "No duplicate Student/Course/Semester/Attempt records."
    )

else:
    warning(
        f"{len(duplicate_result_rows)} possible duplicate "
        "result records found."
    )

    print(
        duplicate_result_rows.head(20).to_string(
            index=False
        )
    )


section("30. ATTEMPT VALUE CHECK")

invalid_attempts = results[
    results["Attempt"] < 1
]

if invalid_attempts.empty:
    passed(
        "All Attempt values are valid."
    )

else:
    error(
        f"{len(invalid_attempts)} results have invalid Attempt values."
    )

section("31. STUDENT DISTRIBUTION")

print("\nStudents by Year:")

print(
    students[
        "Current_Year"
    ]
    .value_counts()
    .sort_index()
)

print("\nStudents by Intake:")

print(
    students[
        "Intake"
    ]
    .value_counts()
    .sort_index()
)

print("\nStudents by Gender:")

print(
    students[
        "Gender"
    ]
    .value_counts()
)

print("\nStudents by Degree:")

print(
    students[
        "Degree_ID"
    ]
    .value_counts()
)

print("\nExam Eligibility:")

print(
    students[
        "Exam_Eligibility"
    ]
    .value_counts()
)

print("\nAcademic Risk:")

print(
    students[
        "Academic_Risk"
    ]
    .value_counts()
)

print("\nStudent Status:")

print(
    students[
        "Student_Status"
    ]
    .value_counts()
)

section("32. RESULT DISTRIBUTION")

print("\nResults by Grade:")

print(
    results[
        "Grade"
    ]
    .value_counts()
    .sort_index()
)

print("\nResults by Result Status:")

print(
    results[
        "Result_Status"
    ]
    .value_counts()
)

print("\nResults by Semester:")

print(
    results[
        "Semester"
    ]
    .value_counts()
    .sort_index()
)

section("33. GPA STATISTICS")

print("\nCurrent SGPA:")

print(
    students[
        "Current_SGPA"
    ]
    .describe()
)

print("\nPrevious SGPA:")

print(
    students[
        "Previous_SGPA"
    ]
    .describe()
)


print("\nFGPA:")

print(
    students[
        "FGPA"
    ]
    .describe()
)

section("34. ATTENDANCE STATISTICS")

print(
    students[
        "Attendance_Percentage"
    ]
    .describe()
)

section("35. REPEATED COURSE STATISTICS")

print(
    students[
        "Repeated_Courses"
    ]
    .describe()
)

section("36. MACHINE LEARNING SUITABILITY CHECK")

fgpa_unique = (
    students[
        "FGPA"
    ]
    .nunique()
)

print(
    f"Unique FGPA values: {fgpa_unique:,}"
)

if fgpa_unique >= 100:
    passed(
        "FGPA has sufficient variation for regression."
    )

else:
    warning(
        "FGPA has very few unique values. "
        "Check whether the target has enough variation."
    )

fgpa_std = (
    students[
        "FGPA"
    ]
    .std()
)

print(
    f"FGPA standard deviation: {fgpa_std:.4f}"
)

if fgpa_std > 0.1:
    passed(
        "FGPA has reasonable variation."
    )

else:
    warning(
        "FGPA variation is very low."
    )

risk_distribution = (
    students[
        "Academic_Risk"
    ]
    .value_counts(
        normalize=True
    )
    *
    100
)

print(
    "\nAcademic Risk percentage:"
)

print(
    risk_distribution.round(2)
)

# Check result class balance.
result_distribution = (
    results[
        "Result_Status"
    ]
    .value_counts(
        normalize=True
    )
    *
    100
)

print(
    "\nResult Status percentage:"
)

print(
    result_distribution.round(2)
)

section("37. DISTRIBUTION QUALITY WARNINGS")

def check_extreme_distribution(
    series,
    name
):
    distribution = (
        series
        .value_counts(
            normalize=True
        )
        *
        100
    )

    if distribution.empty:
        return

    highest = distribution.max()
    most_common = distribution.idxmax()

    print(
        f"{name}: "
        f"{most_common} = "
        f"{highest:.2f}%"
    )

    if highest >= 90:
        warning(
            f"{name} is highly imbalanced. "
            f"{most_common} represents "
            f"{highest:.2f}% of records."
        )

    else:
        passed(
            f"{name} distribution does not "
            "have a >90% dominant category."
        )


check_extreme_distribution(
    students["Degree_ID"],
    "Degree"
)

check_extreme_distribution(
    students["Current_Year"],
    "Current Year"
)

check_extreme_distribution(
    students["Academic_Risk"],
    "Academic Risk"
)

check_extreme_distribution(
    students["Exam_Eligibility"],
    "Exam Eligibility"
)

check_extreme_distribution(
    results["Grade"],
    "Grade"
)

check_extreme_distribution(
    results["Result_Status"],
    "Result Status"
)

section("FINAL DATASET QUALITY SUMMARY")

print(
    f"Passed checks   : {PASS_COUNT}"
)

print(
    f"Warnings        : {WARNING_COUNT}"
)

print(
    f"Errors          : {ERROR_COUNT}"
)

print()
print("=" * 75)

if ERROR_COUNT == 0:
    if WARNING_COUNT == 0:
        print(
            "DATASET QUALITY RESULT: EXCELLENT"
        )

        print(
            "The dataset passed all validation checks."
        )

    else:
        print(
            "DATASET QUALITY RESULT: VALID WITH WARNINGS"
        )

        print(
            "The dataset passed all critical validation "
            "checks, but review the warnings before ML training."
        )

else:
    print(
        "DATASET QUALITY RESULT: NOT READY"
    )

    print(
        "Critical errors were detected. "
        "Fix them before using the dataset for AI model training."
    )


print("=" * 75)
print()
print("NEXT STEPS")
print("-" * 75)

if ERROR_COUNT == 0:
    print(
        "1. Dataset structure is valid."
    )

    print(
        "2. Review the distribution statistics above."
    )

    print(
        "3. Create an ML feature-engineering dataset."
    )

    print(
        "4. Split data into training/validation/test sets."
    )

    print(
        "5. Train and evaluate the Neural Network."
    )

    print(
        "6. Build the Genetic Algorithm using module-level data."
    )

    print(
        "7. Implement the Rule-Based Expert System."
    )

else:
    print(
        "1. Fix every [ERROR] shown above."
    )

    print(
        "2. Run this script again."
    )

    print(
        "3. Continue to AI model development only "
        "after critical errors are resolved."
    )


print()
print(
    "Dataset quality check completed."
)