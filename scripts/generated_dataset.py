import pandas as pd
import numpy as np
from pathlib import Path

SEED = 42
TARGET_STUDENTS = 3000

# Preserve S0001-S0025
# Generate S0026-S3000
START_NEW_ID = 26

rng = np.random.default_rng(SEED)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

OUTPUT_DIR = (
    PROJECT_ROOT
    / "scripts"
    / "generated_dataset"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# INPUT FILES
FACULTIES_FILE = DATA_DIR / "faculties.csv"
DEGREES_FILE = DATA_DIR / "degrees.csv"
MODULES_FILE = DATA_DIR / "course_modules.csv"
DEGREE_MODULES_FILE = DATA_DIR / "degree_modules.csv"
STUDENTS_FILE = DATA_DIR / "students.csv"
RESULTS_FILE = DATA_DIR / "student_results.csv"

required_files = [
    FACULTIES_FILE,
    DEGREES_FILE,
    MODULES_FILE,
    DEGREE_MODULES_FILE,
    STUDENTS_FILE,
    RESULTS_FILE
]

for file in required_files:
    if not file.exists():
        raise FileNotFoundError(
            f"\nRequired file not found:\n{file}"
        )


print("\nLoading CSV files...")

faculties = pd.read_csv(
    FACULTIES_FILE,
    dtype=str
)

degrees = pd.read_csv(
    DEGREES_FILE,
    dtype=str
)

modules = pd.read_csv(
    MODULES_FILE,
    dtype=str
)

degree_modules = pd.read_csv(
    DEGREE_MODULES_FILE,
    dtype=str
)

students = pd.read_csv(
    STUDENTS_FILE,
    dtype=str
)

results = pd.read_csv(
    RESULTS_FILE,
    dtype=str
)

required_student_cols = [
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

required_result_cols = [
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

def validate_columns(df, required, filename):
    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"{filename} is missing columns:\n"
            +
            "\n".join(
                f" - {column}"
                for column in missing
            )
        )


validate_columns(
    students,
    required_student_cols,
    "students.csv"
)

validate_columns(
    results,
    required_result_cols,
    "student_results.csv"
)

validate_columns(
    degrees,
    ["Degree_ID"],
    "degrees.csv"
)

validate_columns(
    modules,
    [
        "Course_Code",
        "Year",
        "Semester",
        "Credits"
    ],
    "course_modules.csv"
)

validate_columns(
    degree_modules,
    [
        "Degree_Module_ID",
        "Degree_ID",
        "Course_Code",
        "Module_Type"
    ],
    "degree_modules.csv"
)

# NUMERIC CONVERSION
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

for column in student_numeric_columns:
    students[column] = pd.to_numeric(
        students[column],
        errors="raise"
    )


result_numeric_columns = [
    "Academic_Year",
    "Semester",
    "Attempt",
    "Marks",
    "Grade_Point"
]

for column in result_numeric_columns:
    results[column] = pd.to_numeric(
        results[column],
        errors="raise"
    )


# PRESERVE ORIGINAL DATA
original_students = students.copy()
original_results = results.copy()

if students["Student_ID"].duplicated().any():
    raise ValueError(
        "Duplicate Student_ID values found "
        "in students.csv."
    )


if results["Result_ID"].duplicated().any():
    raise ValueError(
        "Duplicate Result_ID values found "
        "in student_results.csv."
    )


valid_degrees = set(
    degrees["Degree_ID"]
    .astype(str)
)

unknown_degrees = (
    set(students["Degree_ID"].astype(str))
    -
    valid_degrees
)

if unknown_degrees:
    raise ValueError(
        "Unknown Degree_ID values in students.csv:\n"
        f"{unknown_degrees}"
    )


valid_courses = set(
    modules["Course_Code"]
    .astype(str)
)

unknown_courses = (
    set(results["Course_Code"].astype(str))
    -
    valid_courses
)

if unknown_courses:
    raise ValueError(
        "Unknown Course_Code values in "
        "student_results.csv:\n"
        f"{unknown_courses}"
    )


# REQUIRED ORIGINAL STUDENTS
existing_ids = set(
    students["Student_ID"]
    .astype(str)
)

expected_original_ids = {
    f"S{i:04d}"

    for i in range(
        1,
        START_NEW_ID
    )
}

missing_original = (
    expected_original_ids
    -
    existing_ids
)

if missing_original:
    raise ValueError(
        "students.csv must contain "
        "S0001-S0025.\n"

        f"Missing: "
        f"{sorted(missing_original)}"
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


degree_prefix = {
    "D001": "BSE",
    "D002": "BCS",
    "D003": "COE",
    "D004": "DBA",
    "D005": "ICT"
}

for degree_id in degrees["Degree_ID"]:
    if degree_id not in degree_prefix:
        raise ValueError(
            f"No registration prefix configured "
            f"for Degree_ID={degree_id}"
        )


# NEXT REGISTRATION NUMBER
registration_numbers = []

for registration in students[
    "Registration_No"
].astype(str):

    parts = registration.split("/")

    if (
        parts
        and
        parts[-1].isdigit()
    ):

        registration_numbers.append(
            int(parts[-1])
        )


next_registration = (
    max(
        registration_numbers,
        default=0
    )
    +
    1
)

# NEXT RESULT ID
result_numbers = []

for result_id in results[
    "Result_ID"
].astype(str):
    if (
        result_id.startswith("R")
        and
        result_id[1:].isdigit()
    ):
        result_numbers.append(
            int(result_id[1:])
        )


next_result_id = (
    max(
        result_numbers,
        default=0
    )
    +
    1
)

# DEGREE DISTRIBUTION
degree_choices = [
    "D001",
    "D002",
    "D003",
    "D004",
    "D005"
]

degree_probabilities = [
    0.28,
    0.24,
    0.18,
    0.12,
    0.18
]

# PREPARE COURSE MODULE DATA
modules_numeric = modules.copy()

modules_numeric["Year_Num"] = pd.to_numeric(
    modules_numeric["Year"],
    errors="coerce"
)

modules_numeric["Semester_Num"] = pd.to_numeric(
    modules_numeric["Semester"],
    errors="coerce"
)

modules_numeric["Credits_Num"] = pd.to_numeric(
    modules_numeric["Credits"],
    errors="coerce"
)

if modules_numeric["Year_Num"].isna().any():
    raise ValueError(
        "course_modules.csv contains invalid Year values."
    )


if modules_numeric["Semester_Num"].isna().any():
    raise ValueError(
        "course_modules.csv contains invalid Semester values."
    )


if modules_numeric["Credits_Num"].isna().any():
    raise ValueError(
        "course_modules.csv contains invalid Credits values."
    )


modules_numeric["Year_Num"] = (
    modules_numeric["Year_Num"]
    .astype(int)
)

modules_numeric["Semester_Num"] = (
    modules_numeric["Semester_Num"]
    .astype(int)
)

modules_numeric["Credits_Num"] = (
    modules_numeric["Credits_Num"]
    .astype(float)
)

# CHECK CREDIT CONFLICTS
credit_conflicts = (
    modules_numeric

    .groupby(
        [
            "Course_Code",
            "Year_Num",
            "Semester_Num"
        ]
    )["Credits_Num"]

    .nunique()
)

credit_conflicts = (
    credit_conflicts[
        credit_conflicts > 1
    ]
)

if not credit_conflicts.empty:
    raise ValueError(
        "Conflicting Credits values found:\n"
        f"{credit_conflicts}"
    )


course_credit_lookup = (
    modules_numeric[
        [
            "Course_Code",
            "Year_Num",
            "Semester_Num",
            "Credits_Num"
        ]
    ]

    .drop_duplicates(
        subset=[
            "Course_Code",
            "Year_Num",
            "Semester_Num"
        ]
    )

    .copy()
)

degree_module_map = {}

for degree_id in (
    degrees[
        "Degree_ID"
    ]

    .astype(str)
    .unique()
):
    merged = (
        degree_modules[
            degree_modules[
                "Degree_ID"
            ]
            .astype(str)
            ==
            degree_id
        ]

        .merge(
            modules_numeric,
            on="Course_Code",
            how="inner",

            suffixes=(
                "_DM",
                "_CM"
            )
        )
    )

    merged = merged.dropna(
        subset=[
            "Year_Num",
            "Semester_Num",
            "Credits_Num"
        ]
    )

    merged = (
        merged

        .drop_duplicates(
            subset=[
                "Course_Code",
                "Year_Num",
                "Semester_Num"
            ]
        )

        .reset_index(
            drop=True
        )

    )

    degree_module_map[
        degree_id
    ] = merged


semester_options = {
    1: [1, 2],
    2: [3, 4],
    3: [5, 6],
    4: [7, 8]
}

intake_by_year = {
    1: 42,
    2: 41,
    3: 40,
    4: 39
}

def credit_weighted_gpa(rows):
    total_credits = sum(
        credits
        for _, credits in rows
    )

    if total_credits <= 0:
        return 0.0

    weighted_points = sum(
        grade_point * credits

        for grade_point, credits
        in rows
    )

    return (
        weighted_points
        /
        total_credits
    )


new_students = []
new_results = []

generated_student_ids = set()

print(
    "\nGenerating students S0026-S3000...\n"
)

for student_number in range(
    START_NEW_ID,
    TARGET_STUDENTS + 1
):
    student_id = (
        f"S{student_number:04d}"
    )

    degree_id = str(
        rng.choice(
            degree_choices,
            p=degree_probabilities
        )
    )

    gender = rng.choice(
        [
            "Female",
            "Male"
        ],

        p=[
            0.35,
            0.65
        ]
    )

    year = int(
        rng.choice(
            [
                1,
                2,
                3,
                4
            ],

            p=[
                0.32,
                0.30,
                0.25,
                0.13
            ]
        )
    )

    intake = intake_by_year[
        year
    ]

    semester = int(
        rng.choice(
            semester_options[
                year
            ]
        )
    )

    attendance = int(
        np.clip(
            rng.normal(
                loc=85,
                scale=9
            ),

            55,
            100
        )
    )

    if attendance >= 80:
        attendance_approved = "No"

    else:
        attendance_approved = (
            "Yes"

            if rng.random() < 0.25

            else "No"
        )


    fee_paid = (
        "Yes"

        if rng.random() < 0.96

        else "No"
    )

    attendance_condition = (
        attendance >= 80
        or
        attendance_approved == "Yes"
    )

    fee_condition = (
        fee_paid == "Yes"
    )

    if (
        attendance_condition
        and
        fee_condition
    ):
        exam_eligibility = "Eligible"

    else:
        exam_eligibility = "Not Eligible"


    registration_no = (
        f"D/{degree_prefix[degree_id]}/25/"
        f"{next_registration:04d}"
    )

    next_registration += 1

    ability = float(
        np.clip(
            rng.normal(
                loc=0.0,
                scale=1.0
            ),

            -2.2,
            2.2
        )
    )

    degree_modules_df = (
        degree_module_map.get(
            degree_id
        )
    )

    if (
        degree_modules_df is None
        or
        degree_modules_df.empty
    ):

        raise ValueError(
            f"No modules found for "
            f"Degree_ID={degree_id}."
        )

    completed_modules = (
        degree_modules_df[
            degree_modules_df[
                "Semester_Num"
            ]
            <=
            semester
        ]
        .copy()
    )

    if completed_modules.empty:
        raise ValueError(
            f"No completed modules found "
            f"for {student_id}."
        )

    student_result_rows = []
    semester_gp_credits = {}

    # GENERATE RESULTS FOR THIS STUDENT
    for _, module in (
        completed_modules.iterrows()
    ):
        course_code = str(
            module["Course_Code"]
        )

        module_category = ""

        if (
            "Module_Category"
            in
            module.index
            and
            pd.notna(
                module[
                    "Module_Category"
                ]
            )
        ):

            module_category = str(
                module[
                    "Module_Category"
                ]
            )


        # BASE MARK
        if (
            module_category.upper()
            ==
            "GPA"
        ):

            mean_mark = 72

        else:
            mean_mark = 68

        mean_mark += (
            ability * 10
        )

        # GENERATE MARK
        mark = int(
            np.clip(
                rng.normal(
                    loc=mean_mark,
                    scale=11
                ),

                20,
                98
            )
        )

        grade_name, grade_point = (
            get_grade(mark)
        )

        # MODULE INFORMATION
        academic_year = int(
            module["Year_Num"]
        )

        module_semester = int(
            module["Semester_Num"]
        )

        credits = float(
            module["Credits_Num"]
        )

        if grade_name == "F":
            result_status = "Fail"

        else:
            result_status = "Pass"


        result_id = (
            f"R{next_result_id:06d}"
        )

        next_result_id += 1

        result_row = {
            "Result_ID":
                result_id,

            "Student_ID":
                student_id,

            "Course_Code":
                course_code,

            "Academic_Year":
                academic_year,

            "Semester":
                module_semester,

            "Attempt":
                1,

            "Marks":
                mark,

            "Grade":
                grade_name,

            "Grade_Point":
                grade_point,

            "Result_Status":
                result_status
        }


        student_result_rows.append(
            result_row
        )

        # STORE GPA INFORMATION
        semester_gp_credits.setdefault(
            module_semester,
            []
        ).append(
            (
                grade_point,
                credits
            )
        )

    # ENSURE STUDENT HAS RESULTS
    if not student_result_rows:
        raise ValueError(
            f"No results generated for "
            f"{student_id}."
        )

    # SGPA FOR EACH SEMESTER
    sgpa_by_semester = {
        sem:
        round(
            credit_weighted_gpa(
                rows
            ),
            4
        )
        for sem, rows
        in semester_gp_credits.items()
    }

    current_sgpa = (
        sgpa_by_semester.get(
            semester,
            0.0
        )
    )

    if (
        year == 1
        and
        semester == 1
    ):
        previous_sgpa = 0.0
    else:
        previous_sgpa = (
            sgpa_by_semester.get(
                semester - 1,
                0.0
            )
        )


    total_weighted_points = 0.0
    total_credits = 0.0

    for semester_rows in (
        semester_gp_credits.values()
    ):
        for grade_point, credits in (
            semester_rows
        ):
            total_weighted_points += (
                grade_point * credits
            )
            total_credits += credits


    if total_credits > 0:
        fgpa = (
            total_weighted_points
            /
            total_credits
        )

    else:
        fgpa = 0.0


    current_sgpa = round(
        current_sgpa,
        4
    )

    previous_sgpa = round(
        previous_sgpa,
        4
    )

    fgpa = round(
        fgpa,
        4
    )

    repeated_courses = sum(
        1

        for row
        in student_result_rows

        if row[
            "Result_Status"
        ] == "Fail"
    )

    if repeated_courses > 0:
        student_status = (
            "Not Completed"
        )

    else:
        student_status = (
            "Completed"
        )


    risk_score = 0

    if fgpa < 2.0:
        risk_score += 2

    elif fgpa < 3.0:
        risk_score += 1


    if repeated_courses >= 2:
        risk_score += 2


    if risk_score >= 3:
        academic_risk = (
            "High Risk"
        )

    elif risk_score >= 1:
        academic_risk = (
            "Medium Risk"
        )

    else:
        academic_risk = (
            "Low Risk"
        )


    new_student = {
        "Student_ID":
            student_id,

        "Registration_No":
            registration_no,

        "Name":
            f"Student_{student_number:04d}",

        "Gender":
            gender,

        "Intake":
            intake,

        "Degree_ID":
            degree_id,

        "Current_Year":
            year,

        "Current_Semester":
            semester,

        "Current_SGPA":
            current_sgpa,

        "Previous_SGPA":
            previous_sgpa,

        "FGPA":
            fgpa,

        "Attendance_Percentage":
            attendance,

        "Attendance_Approved":
            attendance_approved,

        "Fee_Paid":
            fee_paid,

        "Exam_Eligibility":
            exam_eligibility,

        "Repeated_Courses":
            repeated_courses,

        "Student_Status":
            student_status,

        "Academic_Risk":
            academic_risk
    }

    new_students.append(
        new_student
    )

    new_results.extend(
        student_result_rows
    )

    # Track exact generated student
    generated_student_ids.add(
        student_id
    )

    if student_number % 250 == 0:
        print(
            f"Generated up to "
            f"S{student_number:04d}"
        )


new_students_df = pd.DataFrame(
    new_students,
    columns=required_student_cols
)

new_results_df = pd.DataFrame(
    new_results,
    columns=required_result_cols
)

expected_generated_count = (
    TARGET_STUDENTS
    -
    START_NEW_ID
    +
    1
)

if len(new_students_df) != (
    expected_generated_count
):
    raise ValueError(
        "Generated student count incorrect.\n"

        f"Expected: "
        f"{expected_generated_count}\n"

        f"Found: "
        f"{len(new_students_df)}"
    )


generated_result_student_ids = set(
    new_results_df[
        "Student_ID"
    ]
    .astype(str)
)

missing_result_students = (
    generated_student_ids
    -
    generated_result_student_ids
)

orphan_generated_results = (
    generated_result_student_ids
    -
    generated_student_ids
)

if missing_result_students:
    raise ValueError(
        "Generated students without results:\n"
        f"{sorted(missing_result_students)[:50]}"
    )


if orphan_generated_results:
    raise ValueError(
        "Generated results belong to "
        "students that were not generated:\n"

        f"{sorted(orphan_generated_results)[:50]}"
    )


students_out = pd.concat(
    [
        original_students,
        new_students_df
    ],

    ignore_index=True
)

results_out = pd.concat(
    [
        original_results,
        new_results_df
    ],

    ignore_index=True
)

students_out = students_out[
    required_student_cols
]

results_out = results_out[
    required_result_cols
]

for column in [
    "Current_SGPA",
    "Previous_SGPA",
    "FGPA"
]:
    students_out[column] = (
        pd.to_numeric(
            students_out[column]
        )

        .round(4)
    )


results_out["Grade_Point"] = (
    pd.to_numeric(
        results_out["Grade_Point"]
    )

    .round(1)
)

print(
    "\nRunning final validation..."
)

if len(students_out) != TARGET_STUDENTS:
    raise ValueError(
        f"Expected {TARGET_STUDENTS} students, "

        f"found {len(students_out)}."
    )

expected_all_ids = {
    f"S{i:04d}"

    for i in range(
        1,
        TARGET_STUDENTS + 1
    )
}

actual_all_ids = set(
    students_out[
        "Student_ID"
    ]
    .astype(str)
)

if actual_all_ids != expected_all_ids:
    missing_ids = (
        expected_all_ids
        -
        actual_all_ids
    )

    extra_ids = (
        actual_all_ids
        -
        expected_all_ids
    )

    raise ValueError(

        "Student ID range incorrect.\n"

        f"Missing: "
        f"{sorted(missing_ids)[:50]}\n"

        f"Unexpected: "
        f"{sorted(extra_ids)[:50]}"

    )


if not students_out[
    "Student_ID"
].is_unique:

    raise ValueError(
        "Duplicate Student_ID values detected."
    )


if not results_out[
    "Result_ID"
].is_unique:

    raise ValueError(
        "Duplicate Result_ID values detected."
    )


student_id_set = set(
    students_out[
        "Student_ID"
    ]
    .astype(str)
)


result_student_id_set = set(
    results_out[
        "Student_ID"
    ]
    .astype(str)
)

orphan_result_students = (
    result_student_id_set
    -
    student_id_set
)


if orphan_result_students:
    raise ValueError(
        "CRITICAL ERROR:\n"

        "student_results.csv contains "
        "students that do not exist "
        "in students.csv.\n\n"

        f"Orphan Student_ID values:\n"
        f"{sorted(orphan_result_students)[:100]}"
    )


generated_ids_final = {
    f"S{i:04d}"

    for i in range(
        START_NEW_ID,
        TARGET_STUDENTS + 1
    )
}

generated_result_ids_final = set(
    results_out.loc[
        results_out[
            "Student_ID"
        ]
        .isin(
            generated_ids_final
        ),

        "Student_ID"
    ]
    .astype(str)
)

students_without_results = (
    generated_ids_final
    -
    generated_result_ids_final
)

if students_without_results:
    raise ValueError(
        "Some generated students "
        "have no results.\n"

        f"{sorted(students_without_results)[:50]}"
    )


result_courses_final = set(
    results_out[
        "Course_Code"
    ]
    .astype(str)
)


if not result_courses_final.issubset(
    valid_courses
):
    unknown_result_courses = (
        result_courses_final
        -
        valid_courses
    )

    raise ValueError(
        "Results contain unknown courses:\n"

        f"{sorted(unknown_result_courses)[:50]}"
    )

results_with_degree = (
    results_out

    .merge(
        students_out[
            [
                "Student_ID",
                "Degree_ID"
            ]
        ],

        on="Student_ID",
        how="left"
    )
)

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

results_with_degree["pair"] = list(
    zip(
        results_with_degree[
            "Degree_ID"
        ].astype(str),

        results_with_degree[
            "Course_Code"
        ].astype(str)
    )
)

invalid_pairs = (
    results_with_degree.loc[
        ~results_with_degree[
            "pair"
        ]
        .isin(
            valid_degree_course_pairs
        )
    ]
)

if not invalid_pairs.empty:
    raise ValueError(
        "Some results use courses "
        "that do not belong to "
        "the student's degree.\n\n"

        f"{invalid_pairs.head(20)}"
    )


gen_results = (
    results_out[
        results_out[
            "Student_ID"
        ]
        .isin(
            generated_ids_final
        )
    ]

    .copy()
)

gen_results = gen_results.merge(
    course_credit_lookup[
        [
            "Course_Code",
            "Year_Num",
            "Semester_Num",
            "Credits_Num"
        ]
    ],

    left_on=[
        "Course_Code",
        "Academic_Year",
        "Semester"
    ],

    right_on=[
        "Course_Code",
        "Year_Num",
        "Semester_Num"
    ],

    how="left",
    validate="many_to_one"
)

if gen_results[
    "Credits_Num"
].isna().any():

    bad_rows = gen_results.loc[
        gen_results[
            "Credits_Num"
        ].isna(),

        [
            "Student_ID",
            "Course_Code",
            "Academic_Year",
            "Semester"
        ]
    ]

    raise ValueError(
        "Could not determine module "
        "credits for generated results.\n\n"

        f"{bad_rows.head(20)}"
    )


gen_results["weighted"] = (
    gen_results[
        "Grade_Point"
    ]
    *
    gen_results[
        "Credits_Num"
    ]
)

sgpa_check = (
    gen_results

    .groupby(
        [
            "Student_ID",
            "Semester"
        ]
    )

    .agg(
        weighted_sum=(
            "weighted",
            "sum"
        ),

        credit_sum=(
            "Credits_Num",
            "sum"
        )
    )
)


sgpa_check["sgpa"] = (
    sgpa_check[
        "weighted_sum"
    ]

    /

    sgpa_check[
        "credit_sum"
    ]

).round(4)


sgpa_lookup = (
    sgpa_check[
        "sgpa"
    ]
    .to_dict()
)

fgpa_check = (
    gen_results

    .groupby(
        "Student_ID"
    )

    .agg(

        weighted_sum=(
            "weighted",
            "sum"
        ),

        credit_sum=(
            "Credits_Num",
            "sum"
        )
    )
)

fgpa_check["fgpa"] = (
    fgpa_check[
        "weighted_sum"
    ]

    /

    fgpa_check[
        "credit_sum"
    ]
).round(4)

fgpa_lookup = (
    fgpa_check[
        "fgpa"
    ]
    .to_dict()
)

gen_students_out = (
    students_out[
        students_out[
            "Student_ID"
        ]
        .isin(
            generated_ids_final
        )

    ]
    .copy()
)

gpa_mismatches = []

for _, row in (
    gen_students_out.iterrows()
):
    sid = row[
        "Student_ID"
    ]

    semester = int(
        row[
            "Current_Semester"
        ]
    )

    year = int(
        row[
            "Current_Year"
        ]
    )

    expected_current_sgpa = (
        sgpa_lookup.get(
            (
                sid,
                semester
            ),
            0.0
        )
    )

    if abs(
        expected_current_sgpa
        -
        float(
            row["Current_SGPA"]
        )

    ) > 0.0002:
        gpa_mismatches.append(
            (
                sid,
                "Current_SGPA",
                expected_current_sgpa,
                row["Current_SGPA"]
            )
        )


    if (
        year == 1
        and
        semester == 1
    ):
        expected_previous_sgpa = 0.0

    else:
        expected_previous_sgpa = (
            sgpa_lookup.get(
                (
                    sid,
                    semester - 1
                ),

                0.0
            )
        )


    if abs(
        expected_previous_sgpa
        -
        float(
            row["Previous_SGPA"]
        )

    ) > 0.0002:
        gpa_mismatches.append(
            (
                sid,
                "Previous_SGPA",
                expected_previous_sgpa,
                row["Previous_SGPA"]
            )
        )


    expected_fgpa = (
        fgpa_lookup.get(
            sid,
            0.0
        )
    )


    if abs(
        expected_fgpa
        -
        float(
            row["FGPA"]
        )

    ) > 0.0002:
        gpa_mismatches.append(
            (
                sid,
                "FGPA",
                expected_fgpa,
                row["FGPA"]
            )
        )


if gpa_mismatches:
    raise ValueError(
        "Generated GPA values are "
        "inconsistent with generated results.\n\n"

        "Examples:\n"

        f"{gpa_mismatches[:20]}"
    )


def validate_grade(row):
    expected_grade, expected_point = (
        get_grade(
            row["Marks"]
        )
    )

    return (
        row["Grade"]
        ==
        expected_grade
        and
        abs(
            float(
                row["Grade_Point"]
            )
            -
            expected_point
        ) < 1e-6
    )


grade_check = gen_results.apply(
    validate_grade,
    axis=1
)

if not grade_check.all():
    raise ValueError(
        "Generated results contain "
        "Grade/Grade_Point values "
        "that do not match Marks."

    )


expected_status = (
    gen_results[
        "Grade"
    ]
    ==
    "F"
)

actual_status = (
    gen_results[
        "Result_Status"
    ]
    ==
    "Fail"
)

if not (
    expected_status == actual_status
).all():
    raise ValueError(

        "Result_Status does not match "
        "Grade for generated results."
    )

fail_counts = (
    gen_results[
        gen_results[
            "Result_Status"
        ]
        ==
        "Fail"
    ]
    .groupby(
        "Student_ID"
    )
    .size()
)


for _, row in (
    gen_students_out.iterrows()
):
    sid = row[
        "Student_ID"
    ]

    expected_repeated = int(

        fail_counts.get(
            sid,
            0
        )
    )

    actual_repeated = int(
        row[
            "Repeated_Courses"
        ]
    )

    if (
        expected_repeated
        !=
        actual_repeated
    ):
        raise ValueError(

            f"Repeated_Courses mismatch "
            f"for {sid}.\n"

            f"Expected: "
            f"{expected_repeated}\n"

            f"Found: "
            f"{actual_repeated}"
        )


for _, row in (
    gen_students_out.iterrows()
):
    sid = row[
        "Student_ID"
    ]

    repeated = int(
        row[
            "Repeated_Courses"
        ]
    )


    if repeated > 0:
        expected_status = (
            "Not Completed"
        )

    else:
        expected_status = (
            "Completed"
        )


    if (
        row[
            "Student_Status"
        ]
        !=
        expected_status
    ):
        raise ValueError(

            f"Student_Status mismatch "
            f"for {sid}.\n"

            f"Expected: "
            f"{expected_status}\n"

            f"Found: "
            f"{row['Student_Status']}"
        )


for _, row in (
    gen_students_out.iterrows()
):
    sid = row[
        "Student_ID"
    ]

    attendance = int(
        row[
            "Attendance_Percentage"
        ]
    )

    approved = str(
        row[
            "Attendance_Approved"
        ]
    )

    fee_paid = str(
        row[
            "Fee_Paid"
        ]
    )

    attendance_ok = (
        attendance >= 80
        or
        approved == "Yes"
    )

    fee_ok = (
        fee_paid == "Yes"
    )


    if (
        attendance_ok
        and
        fee_ok
    ):
        expected_eligibility = (
            "Eligible"
        )

    else:
        expected_eligibility = (
            "Not Eligible"
        )


    if (
        row[
            "Exam_Eligibility"
        ]
        !=
        expected_eligibility
    ):
        raise ValueError(
            f"Exam_Eligibility mismatch "
            f"for {sid}.\n"

            f"Expected: "
            f"{expected_eligibility}\n"

            f"Found: "
            f"{row['Exam_Eligibility']}"
        )


for _, row in (
    gen_students_out.iterrows()
):
    sid = row[
        "Student_ID"
    ]

    fgpa = float(
        row[
            "FGPA"
        ]
    )

    repeated = int(
        row[
            "Repeated_Courses"
        ]
    )

    risk_score = 0


    if fgpa < 2.0:
        risk_score += 2

    elif fgpa < 3.0:
        risk_score += 1


    if repeated >= 2:
        risk_score += 2


    if risk_score >= 3:
        expected_risk = (
            "High Risk"
        )

    elif risk_score >= 1:
        expected_risk = (
            "Medium Risk"
        )

    else:
        expected_risk = (
            "Low Risk"
        )


    if (
        row[
            "Academic_Risk"
        ]
        !=
        expected_risk
    ):
        raise ValueError(
            f"Academic_Risk mismatch "
            f"for {sid}.\n"

            f"Expected: "
            f"{expected_risk}\n"

            f"Found: "
            f"{row['Academic_Risk']}"
        )


for _, row in (
    gen_students_out.iterrows()
):
    sid = row[
        "Student_ID"
    ]

    year = int(
        row[
            "Current_Year"
        ]
    )

    intake = int(
        row[
            "Intake"
        ]
    )

    expected_intake = (
        intake_by_year[
            year
        ]
    )

    if intake != expected_intake:
        raise ValueError(
            f"Intake mismatch for {sid}.\n"

            f"Year {year} must use "
            f"Intake {expected_intake}.\n"

            f"Found: {intake}"
        )


for _, row in (
    gen_students_out.iterrows()
):
    year = int(
        row[
            "Current_Year"
        ]
    )

    semester = int(
        row[
            "Current_Semester"
        ]
    )

    if semester not in (
        semester_options[
            year
        ]
    ):
        raise ValueError(
            f"Invalid Year/Semester "
            f"combination for "
            f"{row['Student_ID']}.\n"

            f"Year: {year}\n"
            f"Semester: {semester}"
        )


result_semester_check = (
    gen_results

    .merge(
        gen_students_out[
            [
                "Student_ID",
                "Current_Semester"
            ]
        ],
        on="Student_ID",
        how="left"
    )
)

invalid_future_results = (
    result_semester_check[
        result_semester_check[
            "Semester"
        ]
        >
        result_semester_check[
            "Current_Semester"
        ]
    ]
)

if not invalid_future_results.empty:
    raise ValueError(
        "Some students have results "
        "after their current semester.\n\n"

        f"{invalid_future_results.head(20)}"
    )


original_ids = (
    original_students[
        "Student_ID"
    ]
    .tolist()
)

check_original = (
    students_out[
        students_out[
            "Student_ID"
        ]
        .isin(original_ids)
    ]

    .set_index(
        "Student_ID"
    )

    .loc[original_ids]
    .reset_index()
)

original_reference = (
    original_students
    .reset_index(
        drop=True
    )
)

for column in required_student_cols:
    original_values = (
        check_original[
            column
        ]
        .astype(str)
        .values
    )


    reference_values = (
        original_reference[
            column
        ]
        .astype(str)
        .values
    )

    if not (
        original_values
        ==
        reference_values
    ).all():
        raise ValueError(
            f"Original student data "
            f"was modified in column "
            f"'{column}'."
        )



print(
    "\nChecking student-result relationships..."
)

final_student_ids = set(
    students_out[
        "Student_ID"
    ]
    .astype(str)
)

final_result_student_ids = set(
    results_out[
        "Student_ID"
    ]
    .astype(str)
)

final_orphan_ids = (
    final_result_student_ids
    -
    final_student_ids
)

if final_orphan_ids:
    raise ValueError(
        "FINAL VALIDATION FAILED.\n\n"

        "The following Student_ID values "
        "exist in student_results.csv "
        "but not students.csv:\n"

        f"{sorted(final_orphan_ids)[:100]}"
    )


duplicate_result_keys = (
    results_out
    .groupby(
        [
            "Student_ID",
            "Course_Code",
            "Semester",
            "Attempt"
        ]
    )
    .size()
)

duplicate_result_keys = (
    duplicate_result_keys[
        duplicate_result_keys > 1
    ]
)

if not duplicate_result_keys.empty:
    raise ValueError(

        "Duplicate Student/Course/"
        "Semester/Attempt records found.\n\n"

        f"{duplicate_result_keys.head(20)}"
    )


print(
    "\nAll validation checks passed."
)

print(
    "\nSaving generated dataset..."
)

students_output_file = (
    OUTPUT_DIR
    /
    "students.csv"
)

results_output_file = (
    OUTPUT_DIR
    /
    "student_results.csv"
)

faculties_output_file = (
    OUTPUT_DIR
    /
    "faculties.csv"
)

degrees_output_file = (
    OUTPUT_DIR
    /
    "degrees.csv"
)

modules_output_file = (
    OUTPUT_DIR
    /
    "course_modules.csv"
)

degree_modules_output_file = (
    OUTPUT_DIR
    /
    "degree_modules.csv"
)

students_out.to_csv(
    students_output_file,
    index=False
)

results_out.to_csv(
    results_output_file,
    index=False
)

faculties.to_csv(
    faculties_output_file,
    index=False
)

degrees.to_csv(
    degrees_output_file,
    index=False
)

modules.to_csv(
    modules_output_file,
    index=False
)

degree_modules.to_csv(
    degree_modules_output_file,
    index=False
)

generated_student_count = (
    len(new_students_df)
)

generated_result_count = (
    len(new_results_df)
)

original_result_count = (
    len(original_results)
)


print("\n")

print(
    "=" * 70
)

print(
    "SMART CAMPUS DATASET GENERATION COMPLETE"
)

print(
    "=" * 70
)

print(
    f"Original students preserved : "
    f"{len(original_students):,}"
)

print(
    f"New students generated      : "
    f"{generated_student_count:,}"
)

print(
    f"Total students              : "
    f"{len(students_out):,}"
)

print(
    f"Original results preserved  : "
    f"{original_result_count:,}"
)

print(
    f"New results generated       : "
    f"{generated_result_count:,}"
)

print(
    f"Total results               : "
    f"{len(results_out):,}"
)

print(
    "\nYear → Intake:"
)

print(
    "Year 1 → Intake 42"
)

print(
    "Year 2 → Intake 41"
)

print(
    "Year 3 → Intake 40"
)

print(
    "Year 4 → Intake 39"
)

print(
    "\nInput directory:"
)

print(
    DATA_DIR
)

print(
    "\nOutput directory:"
)

print(
    OUTPUT_DIR
)

print(
    "\nGenerated files:"
)

print(
    " - students.csv"
)

print(
    " - student_results.csv"
)

print(
    " - faculties.csv"
)

print(
    " - degrees.csv"
)

print(
    " - course_modules.csv"
)

print(
    " - degree_modules.csv"
)

print(
    "=" * 70
)

print(
    "\nDataset generation finished successfully."
)