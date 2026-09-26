from pathlib import Path
import sys
import json
from typing import List, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SCRIPTS_DIR = PROJECT_ROOT / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


from study_plan_ga import (  # noqa: E402
    load_data,
    determine_target_semester,
    get_target_modules,
    optimize_study_plan,
    safe_int,
    safe_float,
)

SPRING_BOOT_BASE_URL = "https://ai-smart-campus-decision-support-system-production.up.railway.app"

app = FastAPI(
    title="Smart Campus Personalized Study Plan API",
    description=(
        "API for generating a personalized weekly study plan "
        "using the Genetic Algorithm."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:

    (
        STUDENTS,
        RESULTS,
        COURSE_MODULES,
        DEGREE_MODULES,
    ) = load_data()

    DATA_LOAD_ERROR = None

except Exception as error:

    STUDENTS = None
    RESULTS = None
    COURSE_MODULES = None
    DEGREE_MODULES = None

    DATA_LOAD_ERROR = str(error)


class StudyPlanRequest(BaseModel):

    student_id: str = Field(
        ...,
        min_length=1,
        description=(
            "Logged-in KDU student ID"
        ),
        examples=["KDU/BSE/25/0001"],
    )

    available_hours: int = Field(
        ...,
        ge=1,
        le=168,
        description=(
            "Number of hours available for weekly self-study"
        ),
        examples=[20],
    )

    random_seed: int = Field(
        42,
        ge=0,
        description=(
            "Random seed used to make GA results reproducible"
        ),
    )


class StudyPlanModule(BaseModel):

    course_code: str

    module_name: str

    credits: int

    module_type: str

    historical_grade_point: Optional[float]

    performance_basis: str

    priority: float

    recommended_hours: int


class StudyPlanResponse(BaseModel):

    student_id: str

    registration_no: str

    student_name: str

    degree_id: str

    current_year: int

    current_semester: int

    target_semester: int

    academic_risk: str

    current_sgpa: Optional[float]

    previous_sgpa: Optional[float]

    available_hours: int

    total_allocated_hours: int

    fitness: float

    study_plan: List[StudyPlanModule]


def get_backend_student_dashboard(
    student_id: str
) -> dict:

    url = (
        f"{SPRING_BOOT_BASE_URL}"
        f"/api/students/dashboard"
        f"?studentId={student_id}"
    )

    request = Request(
        url,
        headers={
            "Accept": "application/json"
        },
        method="GET",
    )

    try:

        with urlopen(
            request,
            timeout=10
        ) as response:

            response_data = response.read().decode(
                "utf-8"
            )

            return json.loads(response_data)

    except HTTPError as error:

        if error.code == 404:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"Student '{student_id}' was not found "
                    "in the Spring Boot backend."
                ),
            )

        raise HTTPException(
            status_code=503,
            detail=(
                "Unable to retrieve student data from "
                f"the Spring Boot backend. HTTP {error.code}."
            ),
        )

    except URLError as error:

        raise HTTPException(
            status_code=503,
            detail=(
                "Spring Boot backend is not available. "
                "Please make sure the backend is running "
                f"on {SPRING_BOOT_BASE_URL}. "
                f"Connection error: {error.reason}"
            ),
        )

    except json.JSONDecodeError:

        raise HTTPException(
            status_code=503,
            detail=(
                "The Spring Boot backend returned an "
                "invalid response."
            ),
        )


def build_student_results_from_backend(
    dashboard: dict
) -> pd.DataFrame:
    

    rows = []

    grades = dashboard.get(
        "grades",
        {}
    )

    if not isinstance(grades, dict):
        grades = {}

    for semester_key, semester_grades in grades.items():

        semester = safe_int(
            semester_key,
            default=0
        )

        if not isinstance(
            semester_grades,
            list
        ):
            continue

        for grade_record in semester_grades:

            if not isinstance(
                grade_record,
                dict
            ):
                continue

            course_code = str(
                grade_record.get(
                    "courseCode",
                    ""
                )
            ).strip()

            if not course_code:
                continue

            grade = str(
                grade_record.get(
                    "grade",
                    ""
                )
            ).strip()

            grade_point = safe_float(
                grade_record.get(
                    "gradePoint"
                ),
                None
            )

            rows.append(
                {
                    "Result_ID": "",
                    "Student_ID": str(
                        dashboard.get(
                            "profile",
                            {}
                        ).get(
                            "studentId",
                            ""
                        )
                    ),
                    "Course_Code": course_code,
                    "Academic_Year": "",
                    "Semester": semester,
                    "Attempt": 1,
                    "Marks": "",
                    "Grade": grade,
                    "Grade_Point": grade_point,
                    "Result_Status": "Pass",
                }
            )

    return pd.DataFrame(
        rows,
        columns=[
            "Result_ID",
            "Student_ID",
            "Course_Code",
            "Academic_Year",
            "Semester",
            "Attempt",
            "Marks",
            "Grade",
            "Grade_Point",
            "Result_Status",
        ],
    )


def get_sgpa_information(
    dashboard: dict
):

    semester_records = dashboard.get(
        "semesterRecords",
        []
    )

    if not isinstance(
        semester_records,
        list
    ):
        semester_records = []

    records = []

    for record in semester_records:

        if not isinstance(
            record,
            dict
        ):
            continue

        semester = safe_int(
            record.get("semester"),
            default=0
        )

        sgpa = safe_float(
            record.get("sgpa"),
            None
        )

        if semester > 0 and sgpa is not None:

            records.append(
                (
                    semester,
                    sgpa
                )
            )

    records.sort(
        key=lambda item: item[0]
    )

    if not records:

        return None, None

    current_sgpa = records[-1][1]

    previous_sgpa = None

    if len(records) >= 2:
        previous_sgpa = records[-2][1]

    return current_sgpa, previous_sgpa


def determine_academic_risk(
    current_sgpa: Optional[float]
) -> str:
   

    if current_sgpa is None:

        return "Unknown"

    if current_sgpa >= 3.00:

        return "Low Risk"

    if current_sgpa >= 2.00:

        return "Medium Risk"

    return "High Risk"


def build_ga_student(
    dashboard: dict,
    student_results: pd.DataFrame
) -> pd.Series:

    profile = dashboard.get(
        "profile"
    )

    if not isinstance(
        profile,
        dict
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "The student does not have a complete "
                "academic profile."
            ),
        )

    student_id = str(
        profile.get(
            "studentId",
            ""
        )
    ).strip()

    if not student_id:

        raise HTTPException(
            status_code=400,
            detail=(
                "Student ID is missing from the academic profile."
            ),
        )

    current_sgpa, previous_sgpa = (
        get_sgpa_information(
            dashboard
        )
    )

    current_year = safe_int(
        profile.get(
            "currentYear"
        ),
        default=1
    )

    current_semester = safe_int(
        profile.get(
            "currentSemester"
        ),
        default=1
    )

    degree_id = str(
        profile.get(
            "degreeId",
            ""
        )
    ).strip()

    if not degree_id:

        raise HTTPException(
            status_code=400,
            detail=(
                "Degree information is missing "
                "from the academic profile."
            ),
        )

    academic_risk = determine_academic_risk(
        current_sgpa
    )

    return pd.Series(
        {

            "Student_ID": student_id,

            "Registration_No": student_id,

            "Name": dashboard.get(
                "profile",
                {}
            ).get(
                "studentId",
                student_id
            ),

            "Intake": safe_int(
                profile.get(
                    "intake"
                ),
                default=0
            ),

            "Degree_ID": degree_id,

            "Current_Year": current_year,

            "Current_Semester": current_semester,

 
            "Current_SGPA": (
                current_sgpa
                if current_sgpa is not None
                else 0.0
            ),

            "Previous_SGPA": (
                previous_sgpa
                if previous_sgpa is not None
                else 0.0
            ),


            "Academic_Risk": academic_risk,

            "Repeated_Courses": 0,

            "Gender": "",
            "Faculty_ID": str(
                profile.get(
                    "facultyId",
                    ""
                )
            ),
            "FGPA": (
                current_sgpa
                if current_sgpa is not None
                else 0.0
            ),
            "Attendance_Percentage": 0,
            "Attendance_Approved": "",
            "Fee_Paid": "",
            "Exam_Eligibility": "",
            "Student_Status": "",
        }
    )


def get_previous_student_results(
    student_results: pd.DataFrame,
    target_semester: int
) -> pd.DataFrame:


    if student_results.empty:

        return student_results.copy()

    results = student_results.copy()

    results["Semester"] = (
        results["Semester"]
        .apply(
            safe_int
        )
    )

    return results[
        results["Semester"] < target_semester
    ].copy()


@app.get("/")
def root():

    return {
        "service": (
            "Smart Campus Personalized Study Plan API"
        ),
        "status": "running",
        "data_loaded": (
            STUDENTS is not None
            and RESULTS is not None
            and COURSE_MODULES is not None
            and DEGREE_MODULES is not None
        ),
        "backend_url": SPRING_BOOT_BASE_URL,
    }


@app.get("/health")
def health():

    if (
        STUDENTS is None
        or RESULTS is None
        or COURSE_MODULES is None
        or DEGREE_MODULES is None
    ):

        return {
            "status": "unhealthy",
            "data_loaded": False,
            "error": DATA_LOAD_ERROR,
        }

    return {
        "status": "healthy",
        "data_loaded": True,
        "students_dataset": len(STUDENTS),
        "results_dataset": len(RESULTS),
        "course_modules": len(COURSE_MODULES),
        "degree_modules": len(DEGREE_MODULES),
        "spring_boot_backend": SPRING_BOOT_BASE_URL,
    }


@app.post(
    "/generate-study-plan",
    response_model=StudyPlanResponse,
)
def generate_study_plan(
    request: StudyPlanRequest
):


    if (
        COURSE_MODULES is None
        or DEGREE_MODULES is None
    ):

        raise HTTPException(
            status_code=503,
            detail=(
                "Study-plan module datasets are not available. "
                f"Error: {DATA_LOAD_ERROR}"
            ),
        )

    try:

        dashboard = (
            get_backend_student_dashboard(
                request.student_id
            )
        )

        profile = dashboard.get(
            "profile"
        )

        if not isinstance(
            profile,
            dict
        ):

            raise HTTPException(
                status_code=404,
                detail=(
                    "No academic profile was found for "
                    f"student '{request.student_id}'."
                ),
            )

        student_results = (
            build_student_results_from_backend(
                dashboard
            )
        )

        student = build_ga_student(
            dashboard,
            student_results
        )

        current_semester = safe_int(
            student["Current_Semester"],
            default=1
        )

        target_semester = (
            determine_target_semester(
                student
            )
        )

        student_results = (
            get_previous_student_results(
                student_results,
                target_semester
            )
        )

        modules = get_target_modules(
            student=student,
            target_semester=target_semester,
            course_modules=COURSE_MODULES,
            degree_modules=DEGREE_MODULES,
            student_results=student_results,
        )

        if not modules:

            raise HTTPException(
                status_code=404,
                detail=(
                    "No eligible target-semester modules "
                    "were found for this student's degree."
                ),
            )


        if request.available_hours < len(modules):

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Available hours "
                    f"({request.available_hours}) are not "
                    f"enough to allocate at least one hour "
                    f"to each of the {len(modules)} modules."
                ),
            )


        chromosome, fitness = (
            optimize_study_plan(
                modules=modules,
                available_hours=request.available_hours,
                random_seed=request.random_seed,
            )
        )

        study_plan = []

        for module, hours in zip(
            modules,
            chromosome
        ):

            study_plan.append(
                StudyPlanModule(
                    course_code=module.course_code,
                    module_name=module.module_name,
                    credits=module.credits,
                    module_type=module.module_type,
                    historical_grade_point=(
                        module.historical_grade_point
                    ),
                    performance_basis=(
                        module.performance_basis
                    ),
                    priority=round(
                        module.priority,
                        4
                    ),
                    recommended_hours=int(
                        hours
                    ),
                )
            )


        current_sgpa = safe_float(
            student.get(
                "Current_SGPA"
            ),
            None
        )

        previous_sgpa = safe_float(
            student.get(
                "Previous_SGPA"
            ),
            None
        )

        return StudyPlanResponse(

            student_id=str(
                request.student_id
            ),

            registration_no=str(
                request.student_id
            ),

            student_name=str(
                profile.get(
                    "studentId",
                    request.student_id
                )
            ),

            degree_id=str(
                student["Degree_ID"]
            ),

            current_year=safe_int(
                student["Current_Year"],
                default=1
            ),

            current_semester=current_semester,

            target_semester=target_semester,

            academic_risk=str(
                student.get(
                    "Academic_Risk",
                    "Unknown"
                )
            ),

            current_sgpa=current_sgpa,

            previous_sgpa=previous_sgpa,

            available_hours=(
                request.available_hours
            ),

            total_allocated_hours=sum(
                chromosome
            ),

            fitness=round(
                fitness,
                4
            ),

            study_plan=study_plan,
        )

    except HTTPException:

        raise

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Study-plan generation failed: "
                f"{error}"
            ),
        )