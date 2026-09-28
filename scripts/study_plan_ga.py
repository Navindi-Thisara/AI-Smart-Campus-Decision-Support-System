import argparse
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

STUDENTS_FILE = DATA_DIR / "students.csv"
RESULTS_FILE = DATA_DIR / "student_results.csv"
COURSE_MODULES_FILE = DATA_DIR / "course_modules.csv"
DEGREE_MODULES_FILE = DATA_DIR / "degree_modules.csv"

DEFAULT_STUDENT_ID = "D/BSE/25/0005"
DEFAULT_AVAILABLE_HOURS = 20
DEFAULT_RANDOM_SEED = 42

POPULATION_SIZE = 80
GENERATIONS = 150

MUTATION_RATE = 0.15
CROSSOVER_RATE = 0.85

ELITISM_COUNT = 2
TOURNAMENT_SIZE = 4

@dataclass
class Module:

    course_code: str
    module_name: str
    credits: int
    module_type: str

    historical_grade_point: Optional[float]

    overall_grade_point: Optional[float]

    performance_basis: str

    priority: float


def load_data():

    print("Loading Smart Campus datasets...")

    students = pd.read_csv(STUDENTS_FILE)

    results = pd.read_csv(RESULTS_FILE)

    course_modules = pd.read_csv(
        COURSE_MODULES_FILE
    )

    degree_modules = pd.read_csv(
        DEGREE_MODULES_FILE
    )

    return (
        students,
        results,
        course_modules,
        degree_modules
    )


def find_student(
    students: pd.DataFrame,
    student_identifier: str
) -> pd.Series:

    registration_match = students[
        students["Registration_No"]
        .astype(str)
        .str.strip()
        == str(student_identifier).strip()
    ]

    if not registration_match.empty:

        return registration_match.iloc[0]

    student_id_match = students[
        students["Student_ID"]
        .astype(str)
        .str.strip()
        == str(student_identifier).strip()
    ]

    if not student_id_match.empty:

        return student_id_match.iloc[0]

    raise ValueError(
        f"Student '{student_identifier}' "
        f"was not found in students.csv"
    )


def safe_float(
    value,
    default: Optional[float] = None
):

    try:

        if pd.isna(value):

            return default

        number = float(value)

        if pd.isna(number):

            return default

        return number

    except (ValueError, TypeError):

        return default


def safe_int(
    value,
    default: int = 0
):

    try:

        if pd.isna(value):

            return default

        return int(float(value))

    except (ValueError, TypeError):

        return default


def determine_target_semester(
    student: pd.Series
) -> int:

    current_semester = safe_int(
        student["Current_Semester"],
        default=1
    )

    target_semester = (
        current_semester + 1
    )

    return min(
        target_semester,
        8
    )


def get_course_family(
    course_code: str
) -> str:

    match = re.match(
        r"^[A-Za-z]+",
        str(course_code).strip()
    )

    if match:

        return match.group(0).upper()

    return ""


def calculate_overall_grade_point(
    student: pd.Series,
    student_results: pd.DataFrame
) -> Optional[float]:

    current_sgpa = safe_float(
        student.get("Current_SGPA"),
        None
    )

    if (
        current_sgpa is not None
        and current_sgpa > 0
    ):

        return current_sgpa

    previous_sgpa = safe_float(
        student.get("Previous_SGPA"),
        None
    )

    if (
        previous_sgpa is not None
        and previous_sgpa > 0
    ):

        return previous_sgpa

    if (
        not student_results.empty
        and "Grade_Point" in student_results
    ):

        grade_points = pd.to_numeric(
            student_results["Grade_Point"],
            errors="coerce"
        ).dropna()

        grade_points = grade_points[
            grade_points >= 0
        ]

        if not grade_points.empty:

            return float(
                grade_points.mean()
            )

    return None


def build_course_family_performance(
    student_results: pd.DataFrame
) -> Dict[str, float]:

    if student_results.empty:

        return {}

    results = student_results.copy()

    results["Grade_Point"] = pd.to_numeric(
        results["Grade_Point"],
        errors="coerce"
    )

    results = results.dropna(
        subset=["Grade_Point"]
    )

    results["Course_Family"] = (
        results["Course_Code"]
        .apply(get_course_family)
    )

    results = results[
        results["Course_Family"]
        .astype(str)
        .str.len()
        > 0
    ]

    if results.empty:

        return {}

    family_average = (
        results
        .groupby("Course_Family")
        ["Grade_Point"]
        .mean()
        .to_dict()
    )

    return {
        str(family): float(value)
        for family, value
        in family_average.items()
    }


def get_risk_multiplier(
    student: pd.Series
) -> float:

    risk = str(
        student.get(
            "Academic_Risk",
            ""
        )
    ).strip().lower()

    if risk == "high risk":

        return 1.20

    if risk == "medium risk":

        return 1.10

    return 1.00


def calculate_performance_factor(
    grade_point: Optional[float]
) -> float:

    if grade_point is None:

        return 1.00

    grade_point = max(
        0.0,
        min(
            4.0,
            float(grade_point)
        )
    )

    weakness = (
        4.0 - grade_point
    ) / 4.0

    return (
        1.0
        + (weakness * 0.50)
    )


def get_target_modules(
    student: pd.Series,
    target_semester: int,
    course_modules: pd.DataFrame,
    degree_modules: pd.DataFrame,
    student_results: pd.DataFrame
) -> List[Module]:

    degree_id = str(
        student["Degree_ID"]
    ).strip()

    degree_target = degree_modules[
        degree_modules["Degree_ID"]
        .astype(str)
        .str.strip()
        == degree_id
    ].copy()

    course_target = course_modules[
        course_modules["Semester"]
        .apply(safe_int)
        == target_semester
    ].copy()

    merged = degree_target.merge(
        course_target,
        on="Course_Code",
        how="inner"
    )

    merged = merged[
        merged["Module_Type"]
        .astype(str)
        .str.strip()
        .str.lower()
        == "core"
    ]

    family_performance = (
        build_course_family_performance(
            student_results
        )
    )

    overall_grade_point = (
        calculate_overall_grade_point(
            student,
            student_results
        )
    )

    risk_multiplier = (
        get_risk_multiplier(student)
    )

    repeated_courses = safe_int(
        student.get(
            "Repeated_Courses"
        ),
        default=0
    )

    modules: List[Module] = []

    for _, row in merged.iterrows():

        course_code = str(
            row["Course_Code"]
        ).strip()

        module_name = str(
            row["Module_Name"]
        ).strip()

        credits = safe_int(
            row["Credits"],
            default=1
        )

        module_type = str(
            row["Module_Type"]
        ).strip()

        course_family = get_course_family(
            course_code
        )

        family_gp = family_performance.get(
            course_family
        )

        if family_gp is not None:

            performance_gp = family_gp

            performance_basis = (
                f"{course_family} family "
                f"historical average"
            )

        elif overall_grade_point is not None:

            performance_gp = (
                overall_grade_point
            )

            performance_basis = (
                "overall previous "
                "academic performance"
            )

        else:

            performance_gp = None

            performance_basis = (
                "no historical performance"
            )

        credit_factor = (
            1.0
            + (
                max(
                    0,
                    credits - 1
                )
                * 0.15
            )
        )

        if module_type.upper() == "GPA":

            module_type_factor = 1.10

        else:

            module_type_factor = 0.90

        performance_factor = (
            calculate_performance_factor(
                performance_gp
            )
        )

        if module_type.upper() == "GPA":

            risk_factor = (
                risk_multiplier
            )

        else:

            risk_factor = 1.0

        if (
            repeated_courses > 0
            and module_type.upper() == "GPA"
        ):

            repeat_factor = (
                1.0
                + min(
                    repeated_courses,
                    3
                ) * 0.03
            )

        else:

            repeat_factor = 1.0

        priority = (
            credit_factor
            * module_type_factor
            * performance_factor
            * risk_factor
            * repeat_factor
        )

        modules.append(
            Module(
                course_code=course_code,
                module_name=module_name,
                credits=credits,
                module_type=module_type,
                historical_grade_point=family_gp,
                overall_grade_point=(
                    overall_grade_point
                ),
                performance_basis=(
                    performance_basis
                ),
                priority=priority
            )
        )

    modules.sort(
        key=lambda module:
        module.course_code
    )

    return modules


def repair_chromosome(
    chromosome: List[int],
    total_hours: int,
    minimum_hours: int = 1
) -> List[int]:

    chromosome = [
        max(
            minimum_hours,
            int(hours)
        )
        for hours in chromosome
    ]

    while sum(chromosome) > total_hours:

        candidates = [
            index
            for index, hours
            in enumerate(chromosome)
            if hours > minimum_hours
        ]

        if not candidates:

            break

        index = random.choice(
            candidates
        )

        chromosome[index] -= 1

    while sum(chromosome) < total_hours:

        index = random.randrange(
            len(chromosome)
        )

        chromosome[index] += 1

    return chromosome


def create_initial_population(
    number_of_modules: int,
    available_hours: int
) -> List[List[int]]:

    minimum_required = (
        number_of_modules
    )

    if (
        available_hours
        < minimum_required
    ):

        raise ValueError(
            f"Available hours "
            f"({available_hours}) must be "
            f"at least {number_of_modules}."
        )

    population = []

    for _ in range(
        POPULATION_SIZE
    ):

        chromosome = [
            1
            for _ in range(
                number_of_modules
            )
        ]

        remaining_hours = (
            available_hours
            - number_of_modules
        )

        while remaining_hours > 0:

            index = random.randrange(
                number_of_modules
            )

            chromosome[index] += 1

            remaining_hours -= 1

        population.append(
            chromosome
        )

    return population


def calculate_target_hours(
    modules: List[Module],
    available_hours: int
) -> List[float]:

    total_priority = sum(
        module.priority
        for module in modules
    )

    if total_priority <= 0:

        equal_hours = (
            available_hours
            / len(modules)
        )

        return [
            equal_hours
            for _ in modules
        ]

    return [
        (
            module.priority
            / total_priority
        )
        * available_hours
        for module in modules
    ]


def calculate_fitness(
    chromosome: List[int],
    modules: List[Module],
    available_hours: int
) -> float:

    target_hours = (
        calculate_target_hours(
            modules,
            available_hours
        )
    )

    weighted_error = 0.0

    for allocated, target, module in zip(
        chromosome,
        target_hours,
        modules
    ):

        difference = abs(
            allocated - target
        )

        weighted_error += (
            difference
            * module.priority
        )

    total_allocated = sum(
        chromosome
    )

    utilization_bonus = (
        total_allocated
        / available_hours
    ) * 2.0

    balance_penalty = 0.0

    max_reasonable_hours = max(
        5,
        int(
            available_hours
            * 0.40
        )
    )

    for hours in chromosome:

        if (
            hours
            > max_reasonable_hours
        ):

            excess = (
                hours
                - max_reasonable_hours
            )

            balance_penalty += (
                excess * 0.5
            )

    fitness = (
        30.0
        - weighted_error
        - balance_penalty
        + utilization_bonus
    )

    return fitness


# ============================================================
# TOURNAMENT SELECTION
# ============================================================

def tournament_selection(
    population: List[List[int]],
    fitnesses: List[float]
) -> List[int]:

    candidates = random.sample(
        range(
            len(population)
        ),
        min(
            TOURNAMENT_SIZE,
            len(population)
        )
    )

    winner = max(
        candidates,
        key=lambda index:
        fitnesses[index]
    )

    return population[
        winner
    ].copy()


def crossover(
    parent1: List[int],
    parent2: List[int],
    available_hours: int
) -> Tuple[List[int], List[int]]:

    if len(parent1) <= 1:

        return (
            parent1.copy(),
            parent2.copy()
        )

    if (
        random.random()
        > CROSSOVER_RATE
    ):

        return (
            parent1.copy(),
            parent2.copy()
        )

    point = random.randint(
        1,
        len(parent1) - 1
    )

    child1 = (
        parent1[:point]
        + parent2[point:]
    )

    child2 = (
        parent2[:point]
        + parent1[point:]
    )

    child1 = repair_chromosome(
        child1,
        available_hours
    )

    child2 = repair_chromosome(
        child2,
        available_hours
    )

    return child1, child2


def mutate(
    chromosome: List[int],
    available_hours: int
) -> List[int]:

    mutated = chromosome.copy()

    if (
        len(mutated) < 2
        or random.random()
        > MUTATION_RATE
    ):

        return mutated

    donor_candidates = [
        index
        for index, hours
        in enumerate(mutated)
        if hours > 1
    ]

    if not donor_candidates:

        return mutated

    donor = random.choice(
        donor_candidates
    )

    receiver_candidates = [
        index
        for index
        in range(
            len(mutated)
        )
        if index != donor
    ]

    receiver = random.choice(
        receiver_candidates
    )

    mutated[donor] -= 1

    mutated[receiver] += 1

    return repair_chromosome(
        mutated,
        available_hours
    )


# GA OPTIMIZATION

def optimize_study_plan(
    modules: List[Module],
    available_hours: int,
    random_seed: int = DEFAULT_RANDOM_SEED,
    return_history: bool = False
):

    if not modules:

        raise ValueError(
            "No target modules available "
            "for optimization."
        )

    if (
        available_hours
        < len(modules)
    ):

        raise ValueError(
            f"Available hours "
            f"({available_hours}) are not "
            f"enough to allocate at least "
            f"one hour to each of the "
            f"{len(modules)} modules."
        )

    random.seed(
        random_seed
    )

    population = (
        create_initial_population(
            len(modules),
            available_hours
        )
    )

    best_chromosome = None

    best_fitness = float("-inf")

    convergence_history = []

    for generation in range(
        GENERATIONS
    ):

        fitnesses = [
            calculate_fitness(
                chromosome,
                modules,
                available_hours
            )
            for chromosome
            in population
        ]

        generation_best_index = max(
            range(
                len(population)
            ),
            key=lambda index:
            fitnesses[index]
        )

        generation_best_fitness = (
            fitnesses[
                generation_best_index
            ]
        )

        generation_average_fitness = (
            sum(fitnesses)
            / len(fitnesses)
        )

        if (
            generation_best_fitness
            > best_fitness
        ):

            best_fitness = (
                generation_best_fitness
            )

            best_chromosome = (
                population[
                    generation_best_index
                ].copy()
            )

        convergence_history.append(
            {
                "generation":
                    generation + 1,

                "best_fitness":
                    generation_best_fitness,

                "average_fitness":
                    generation_average_fitness,

                "global_best_fitness":
                    best_fitness
            }
        )

        ranked_indices = sorted(
            range(
                len(population)
            ),
            key=lambda index:
            fitnesses[index],
            reverse=True
        )

        new_population = [
            population[index].copy()
            for index
            in ranked_indices[
                :ELITISM_COUNT
            ]
        ]

        while (
            len(new_population)
            < POPULATION_SIZE
        ):

            parent1 = (
                tournament_selection(
                    population,
                    fitnesses
                )
            )

            parent2 = (
                tournament_selection(
                    population,
                    fitnesses
                )
            )

            child1, child2 = (
                crossover(
                    parent1,
                    parent2,
                    available_hours
                )
            )

            child1 = mutate(
                child1,
                available_hours
            )

            child2 = mutate(
                child2,
                available_hours
            )

            new_population.append(
                child1
            )

            if (
                len(new_population)
                < POPULATION_SIZE
            ):

                new_population.append(
                    child2
                )

        population = (
            new_population
        )

    if return_history:

        return (
            best_chromosome,
            best_fitness,
            convergence_history
        )

    return (
        best_chromosome,
        best_fitness
    )


# BASELINE 1 — EQUAL ALLOCATION

def equal_allocation(
    modules: List[Module],
    available_hours: int
) -> List[int]:

    number_of_modules = len(
        modules
    )

    if (
        number_of_modules == 0
    ):

        raise ValueError(
            "No modules available."
        )

    if (
        available_hours
        < number_of_modules
    ):

        raise ValueError(
            "Not enough hours."
        )

    chromosome = [
        1
        for _ in modules
    ]

    remaining = (
        available_hours
        - number_of_modules
    )

    index = 0

    while remaining > 0:

        chromosome[
            index
        ] += 1

        remaining -= 1

        index = (
            index + 1
        ) % number_of_modules

    return chromosome


# BASELINE 2 — PRIORITY ALLOCATION

def priority_allocation(
    modules: List[Module],
    available_hours: int
) -> List[int]:

    number_of_modules = len(
        modules
    )

    if (
        number_of_modules == 0
    ):

        raise ValueError(
            "No modules available."
        )

    if (
        available_hours
        < number_of_modules
    ):

        raise ValueError(
            "Not enough hours."
        )

    targets = calculate_target_hours(
        modules,
        available_hours
    )

    chromosome = [
        max(
            1,
            int(target)
        )
        for target in targets
    ]

    chromosome = repair_chromosome(
        chromosome,
        available_hours
    )

    return chromosome


# SOLUTION METRICS

def calculate_solution_metrics(
    chromosome: List[int],
    modules: List[Module],
    available_hours: int
) -> Dict[str, float]:

    target_hours = (
        calculate_target_hours(
            modules,
            available_hours
        )
    )

    absolute_errors = [
        abs(
            allocated - target
        )
        for allocated, target
        in zip(
            chromosome,
            target_hours
        )
    ]

    total_absolute_error = sum(
        absolute_errors
    )

    mean_absolute_error = (
        total_absolute_error
        / len(
            absolute_errors
        )
    )

    fitness = calculate_fitness(
        chromosome,
        modules,
        available_hours
    )

    return {
        "fitness": fitness,

        "total_hours":
            float(
                sum(chromosome)
            ),

        "mean_absolute_hour_error":
            mean_absolute_error,

        "maximum_hour_error":
            max(
                absolute_errors
            ),

        "minimum_hours":
            float(
                min(chromosome)
            ),

        "maximum_hours":
            float(
                max(chromosome)
            )
    }


# CONVERGENCE EXPERIMENT

def run_convergence_experiment(
    modules: List[Module],
    available_hours: int,
    seed: int = 42
) -> pd.DataFrame:

    (
        chromosome,
        fitness,
        history
    ) = optimize_study_plan(
        modules,
        available_hours,
        random_seed=seed,
        return_history=True
    )

    dataframe = pd.DataFrame(
        history
    )

    return dataframe


# MULTI-SEED EXPERIMENT

def run_multi_seed_experiment(
    modules: List[Module],
    available_hours: int,
    seeds: List[int]
) -> pd.DataFrame:

    rows = []

    for seed in seeds:

        (
            chromosome,
            fitness
        ) = optimize_study_plan(
            modules,
            available_hours,
            random_seed=seed
        )

        metrics = (
            calculate_solution_metrics(
                chromosome,
                modules,
                available_hours
            )
        )

        rows.append(
            {
                "seed": seed,
                "fitness": fitness,
                "total_hours":
                    sum(chromosome),
                "mean_absolute_hour_error":
                    metrics[
                        "mean_absolute_hour_error"
                    ],
                "maximum_hour_error":
                    metrics[
                        "maximum_hour_error"
                    ],
                "minimum_hours":
                    min(chromosome),
                "maximum_hours":
                    max(chromosome)
            }
        )

    return pd.DataFrame(
        rows
    )


# BASELINE COMPARISON

def compare_baselines(
    modules: List[Module],
    available_hours: int,
    seed: int = 42
) -> pd.DataFrame:

    (
        ga_solution,
        ga_fitness
    ) = optimize_study_plan(
        modules,
        available_hours,
        random_seed=seed
    )

    equal_solution = (
        equal_allocation(
            modules,
            available_hours
        )
    )

    priority_solution = (
        priority_allocation(
            modules,
            available_hours
        )
    )

    solutions = {
        "Genetic Algorithm":
            ga_solution,

        "Equal Allocation":
            equal_solution,

        "Priority Allocation":
            priority_solution
    }

    rows = []

    for method, solution in (
        solutions.items()
    ):

        metrics = (
            calculate_solution_metrics(
                solution,
                modules,
                available_hours
            )
        )

        rows.append(
            {
                "method": method,

                "fitness":
                    metrics["fitness"],

                "total_hours":
                    sum(solution),

                "mean_absolute_hour_error":
                    metrics[
                        "mean_absolute_hour_error"
                    ],

                "maximum_hour_error":
                    metrics[
                        "maximum_hour_error"
                    ],

                "minimum_hours":
                    min(solution),

                "maximum_hours":
                    max(solution)
            }
        )

    return pd.DataFrame(
        rows
    )


# FEASIBILITY TEST

def test_feasibility(
    modules: List[Module],
    hour_values: List[int]
) -> pd.DataFrame:

    number_of_modules = len(
        modules
    )

    rows = []

    for hours in hour_values:

        expected_feasible = (
            hours >= number_of_modules
        )

        try:

            chromosome, fitness = (
                optimize_study_plan(
                    modules,
                    hours,
                    random_seed=42
                )
            )

            actual_feasible = True

            total_hours = sum(
                chromosome
            )

            all_minimum_satisfied = all(
                value >= 1
                for value
                in chromosome
            )

        except ValueError:

            actual_feasible = False

            total_hours = None

            all_minimum_satisfied = False

        rows.append(
            {
                "available_hours":
                    hours,

                "modules":
                    number_of_modules,

                "expected_feasible":
                    expected_feasible,

                "actual_feasible":
                    actual_feasible,

                "feasibility_correct":
                    (
                        expected_feasible
                        == actual_feasible
                    ),

                "total_allocated_hours":
                    total_hours,

                "minimum_constraint_satisfied":
                    all_minimum_satisfied
            }
        )

    return pd.DataFrame(
        rows
    )


# AVAILABLE HOURS EXPERIMENT

def run_hour_scenario_experiment(
    modules: List[Module],
    hour_values: List[int],
    seed: int = 42
) -> pd.DataFrame:

    rows = []

    for hours in hour_values:

        try:

            (
                chromosome,
                fitness
            ) = optimize_study_plan(
                modules,
                hours,
                random_seed=seed
            )

            metrics = (
                calculate_solution_metrics(
                    chromosome,
                    modules,
                    hours
                )
            )

            rows.append(
                {
                    "available_hours":
                        hours,

                    "status":
                        "Feasible",

                    "fitness":
                        fitness,

                    "allocated_hours":
                        sum(chromosome),

                    "mean_absolute_hour_error":
                        metrics[
                            "mean_absolute_hour_error"
                        ],

                    "minimum_module_hours":
                        min(chromosome),

                    "maximum_module_hours":
                        max(chromosome)
                }
            )

        except ValueError as error:

            rows.append(
                {
                    "available_hours":
                        hours,

                    "status":
                        "Infeasible",

                    "fitness":
                        None,

                    "allocated_hours":
                        None,

                    "mean_absolute_hour_error":
                        None,

                    "minimum_module_hours":
                        None,

                    "maximum_module_hours":
                        None
                }
            )

    return pd.DataFrame(
        rows
    )


# STUDENT PROFILE EXPERIMENT

def run_student_profile_experiment(
    students: pd.DataFrame,
    results: pd.DataFrame,
    course_modules: pd.DataFrame,
    degree_modules: pd.DataFrame,
    student_ids: List[str],
    available_hours: int = 20,
    seed: int = 42
) -> pd.DataFrame:

    rows = []

    for student_id in student_ids:

        try:

            student = find_student(
                students,
                student_id
            )

            target_semester = (
                determine_target_semester(
                    student
                )
            )

            student_results = (
                results[
                    results[
                        "Student_ID"
                    ]
                    .astype(str)
                    .str.strip()
                    ==
                    str(
                        student["Student_ID"]
                    ).strip()
                ].copy()
            )

            student_results[
                "Semester"
            ] = student_results[
                "Semester"
            ].apply(
                safe_int
            )

            student_results = (
                student_results[
                    student_results[
                        "Semester"
                    ]
                    < target_semester
                ]
                .copy()
            )

            modules = (
                get_target_modules(
                    student,
                    target_semester,
                    course_modules,
                    degree_modules,
                    student_results
                )
            )

            if not modules:

                rows.append(
                    {
                        "student_id":
                            student_id,

                        "degree_id":
                            student[
                                "Degree_ID"
                            ],

                        "current_sgpa":
                            student.get(
                                "Current_SGPA"
                            ),

                        "academic_risk":
                            student.get(
                                "Academic_Risk",
                                "Unknown"
                            ),

                        "target_semester":
                            target_semester,

                        "module_count":
                            0,

                        "status":
                            "No target modules"
                    }
                )

                continue

            (
                chromosome,
                fitness
            ) = optimize_study_plan(
                modules,
                available_hours,
                random_seed=seed
            )

            rows.append(
                {
                    "student_id":
                        student_id,

                    "degree_id":
                        student[
                            "Degree_ID"
                        ],

                    "current_sgpa":
                        student.get(
                            "Current_SGPA"
                        ),

                    "academic_risk":
                        student.get(
                            "Academic_Risk",
                            "Unknown"
                        ),

                    "target_semester":
                        target_semester,

                    "module_count":
                        len(modules),

                    "fitness":
                        fitness,

                    "allocated_hours":
                        sum(chromosome),

                    "minimum_hours":
                        min(chromosome),

                    "maximum_hours":
                        max(chromosome),

                    "status":
                        "Success"
                }
            )

        except Exception as error:

            rows.append(
                {
                    "student_id":
                        student_id,

                    "status":
                        f"Error: {error}"
                }
            )

    return pd.DataFrame(
        rows
    )


# DISPLAY PLAN

def display_study_plan(
    student: pd.Series,
    target_semester: int,
    available_hours: int,
    modules: List[Module],
    chromosome: List[int],
    fitness: float
):

    print()

    print(
        "=" * 72
    )

    print(
        "GENETIC ALGORITHM - "
        "PERSONALIZED STUDY PLAN"
    )

    print(
        "=" * 72
    )

    print(
        f"Student: "
        f"{student['Registration_No']}"
    )

    print(
        f"Student ID: "
        f"{student['Student_ID']}"
    )

    print(
        f"Degree: "
        f"{student['Degree_ID']}"
    )

    print(
        f"Current Semester: "
        f"{student['Current_Semester']}"
    )

    print(
        f"Target Semester: "
        f"{target_semester}"
    )

    print(
        f"Academic Risk: "
        f"{student.get('Academic_Risk', 'Unknown')}"
    )

    print(
        f"Current SGPA: "
        f"{student.get('Current_SGPA', 'Unknown')}"
    )

    print(
        f"Available Weekly Hours: "
        f"{available_hours}"
    )

    print(
        f"Total Allocated Hours: "
        f"{sum(chromosome)}"
    )

    print(
        f"GA Fitness: "
        f"{fitness:.4f}"
    )

    print()

    print(
        "-" * 72
    )

    print(
        "MODULE ALLOCATION"
    )

    print(
        "-" * 72
    )

    for module, hours in zip(
        modules,
        chromosome
    ):

        if (
            module.historical_grade_point
            is not None
        ):

            historical_gp = (
                f"{module.historical_grade_point:.2f}"
            )

        else:

            historical_gp = "N/A"

        print(
            f"{module.course_code:<10} "
            f"{module.module_name:<42} "
            f"{module.credits} credit(s) | "
            f"GP: {historical_gp:<5} | "
            f"Priority: "
            f"{module.priority:.3f} | "
            f"{hours} hour(s)"
        )

    print()

    print(
        "-" * 72
    )

    print(
        "PERSONALIZATION INFORMATION"
    )

    print(
        "-" * 72
    )

    for module in modules:

        print(
            f"{module.course_code}: "
            f"{module.performance_basis}"
        )

    print()

    print(
        "=" * 72
    )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Generate a personalized "
            "weekly study plan using "
            "a Genetic Algorithm."
        )
    )

    parser.add_argument(
        "student_id",
        nargs="?",
        default=DEFAULT_STUDENT_ID
    )

    parser.add_argument(
        "available_hours",
        nargs="?",
        type=int,
        default=DEFAULT_AVAILABLE_HOURS
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_RANDOM_SEED
    )

    args = parser.parse_args()

    (
        students,
        results,
        course_modules,
        degree_modules
    ) = load_data()

    student = find_student(
        students,
        args.student_id
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
        results[
            results["Student_ID"]
            .astype(str)
            .str.strip()
            ==
            str(
                student["Student_ID"]
            ).strip()
        ].copy()
    )

    student_results[
        "Semester"
    ] = student_results[
        "Semester"
    ].apply(
        safe_int
    )

    student_results = (
        student_results[
            student_results[
                "Semester"
            ]
            < target_semester
        ].copy()
    )

    modules = (
        get_target_modules(
            student,
            target_semester,
            course_modules,
            degree_modules,
            student_results
        )
    )

    print(
        f"Target modules found: "
        f"{len(modules)}"
    )

    if (
        args.available_hours
        < len(modules)
    ):

        raise ValueError(
            f"Available weekly hours "
            f"({args.available_hours}) "
            f"are less than the minimum "
            f"required hours "
            f"({len(modules)})."
        )

    (
        best_chromosome,
        best_fitness
    ) = optimize_study_plan(
        modules,
        args.available_hours,
        random_seed=args.seed
    )

    display_study_plan(
        student,
        target_semester,
        args.available_hours,
        modules,
        best_chromosome,
        best_fitness
    )


if __name__ == "__main__":

    main()