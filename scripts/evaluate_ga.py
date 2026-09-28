import random
import time
from pathlib import Path
from typing import List, Dict, Tuple

import pandas as pd
import matplotlib.pyplot as plt

import study_plan_ga as ga

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "ga_evaluation"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DEFAULT_STUDENT_ID = "D/BSE/25/0005"
DEFAULT_AVAILABLE_HOURS = 20

MULTI_SEEDS = list(range(1, 31))

HOUR_SCENARIOS = [
    9,
    10,
    11,
    15,
    20,
    25,
    30,
    40
]

FEASIBILITY_SCENARIOS = [
    7,
    8,
    9,
    11,
    14,
    19,
    20,
    30,
    40
]

PROFILE_STUDENTS = [
    "D/ICT/25/0003",
    "D/ICT/25/0002",
    "D/BCS/25/0006"
]

# Experiment 7 configurations
PARAMETER_CONFIGURATIONS = [
    {
        "name": "Baseline",
        "population_size": 80,
        "generations": 150,
        "mutation_rate": 0.15,
        "crossover_rate": 0.85,
    },
    {
        "name": "Small Population",
        "population_size": 40,
        "generations": 150,
        "mutation_rate": 0.15,
        "crossover_rate": 0.85,
    },
    {
        "name": "Large Population",
        "population_size": 120,
        "generations": 150,
        "mutation_rate": 0.15,
        "crossover_rate": 0.85,
    },
    {
        "name": "Low Mutation",
        "population_size": 80,
        "generations": 150,
        "mutation_rate": 0.05,
        "crossover_rate": 0.85,
    },
    {
        "name": "High Mutation",
        "population_size": 80,
        "generations": 150,
        "mutation_rate": 0.30,
        "crossover_rate": 0.85,
    },
    {
        "name": "Low Crossover",
        "population_size": 80,
        "generations": 150,
        "mutation_rate": 0.15,
        "crossover_rate": 0.60,
    },
    {
        "name": "High Crossover",
        "population_size": 80,
        "generations": 150,
        "mutation_rate": 0.15,
        "crossover_rate": 0.95,
    },
]

def print_header(title: str):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def calculate_hour_error(
    chromosome: List[int],
    modules,
    available_hours: int
) -> Tuple[float, float]:

    targets = ga.calculate_target_hours(
        modules,
        available_hours
    )

    errors = [
        abs(
            allocated - target
        )
        for allocated, target in zip(
            chromosome,
            targets
        )
    ]

    if not errors:
        return 0.0, 0.0

    return (
        sum(errors) / len(errors),
        max(errors)
    )


def evaluate_chromosome(
    chromosome: List[int],
    modules,
    available_hours: int
) -> Dict:

    mean_error, max_error = calculate_hour_error(
        chromosome,
        modules,
        available_hours
    )

    return {
        "fitness": ga.calculate_fitness(
            chromosome,
            modules,
            available_hours
        ),
        "total_hours": sum(chromosome),
        "mean_absolute_hour_error": mean_error,
        "maximum_hour_error": max_error,
        "minimum_hours": min(chromosome),
        "maximum_hours": max(chromosome),
    }


def get_student_context(
    students: pd.DataFrame,
    results: pd.DataFrame,
    course_modules: pd.DataFrame,
    degree_modules: pd.DataFrame,
    student_id: str,
    available_hours: int
):

    student = ga.find_student(
        students,
        student_id
    )

    current_semester = ga.safe_int(
        student["Current_Semester"],
        default=1
    )

    target_semester = ga.determine_target_semester(
        student
    )

    student_results = results[
        results["Student_ID"].astype(str).str.strip()
        == str(student["Student_ID"]).strip()
    ].copy()

    student_results["Semester"] = (
        student_results["Semester"].apply(
            ga.safe_int
        )
    )

    student_results = student_results[
        student_results["Semester"] < target_semester
    ]

    modules = ga.get_target_modules(
        student,
        target_semester,
        course_modules,
        degree_modules,
        student_results
    )

    if not modules:
        raise ValueError(
            f"No target modules found for student "
            f"{student_id}"
        )

    if available_hours < len(modules):
        raise ValueError(
            f"Available hours ({available_hours}) are less than "
            f"the number of target modules ({len(modules)})."
        )

    return (
        student,
        target_semester,
        student_results,
        modules
    )


def run_ga_with_history(
    modules,
    available_hours: int,
    random_seed: int,
    population_size: int = None,
    generations: int = None,
    mutation_rate: float = None,
    crossover_rate: float = None,
    elitism_count: int = None,
    tournament_size: int = None
):

    original_population_size = ga.POPULATION_SIZE
    original_generations = ga.GENERATIONS
    original_mutation_rate = ga.MUTATION_RATE
    original_crossover_rate = ga.CROSSOVER_RATE
    original_elitism_count = ga.ELITISM_COUNT
    original_tournament_size = ga.TOURNAMENT_SIZE

    try:

        if population_size is None:
            population_size = ga.POPULATION_SIZE

        if generations is None:
            generations = ga.GENERATIONS

        if mutation_rate is None:
            mutation_rate = ga.MUTATION_RATE

        if crossover_rate is None:
            crossover_rate = ga.CROSSOVER_RATE

        if elitism_count is None:
            elitism_count = ga.ELITISM_COUNT

        if tournament_size is None:
            tournament_size = ga.TOURNAMENT_SIZE

        ga.POPULATION_SIZE = population_size
        ga.GENERATIONS = generations
        ga.MUTATION_RATE = mutation_rate
        ga.CROSSOVER_RATE = crossover_rate
        ga.ELITISM_COUNT = elitism_count
        ga.TOURNAMENT_SIZE = tournament_size

        random.seed(
            random_seed
        )

        start_time = time.perf_counter()

        population = ga.create_initial_population(
            len(modules),
            available_hours
        )

        best_chromosome = None
        best_fitness = float("-inf")

        history = []

        for generation in range(
            generations
        ):

            fitnesses = [
                ga.calculate_fitness(
                    chromosome,
                    modules,
                    available_hours
                )
                for chromosome in population
            ]

            generation_best_index = max(
                range(len(population)),
                key=lambda index: fitnesses[index]
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

            if generation_best_fitness > best_fitness:

                best_fitness = (
                    generation_best_fitness
                )

                best_chromosome = (
                    population[
                        generation_best_index
                    ].copy()
                )

            history.append(
                {
                    "generation": generation + 1,
                    "best_fitness": generation_best_fitness,
                    "average_fitness": generation_average_fitness,
                    "global_best_fitness": best_fitness,
                }
            )

            ranked_indices = sorted(
                range(len(population)),
                key=lambda index: fitnesses[index],
                reverse=True
            )

            new_population = [
                population[index].copy()
                for index in ranked_indices[
                    :elitism_count
                ]
            ]

            while len(new_population) < population_size:

                parent1 = ga.tournament_selection(
                    population,
                    fitnesses
                )

                parent2 = ga.tournament_selection(
                    population,
                    fitnesses
                )

                child1, child2 = ga.crossover(
                    parent1,
                    parent2,
                    available_hours
                )

                child1 = ga.mutate(
                    child1,
                    available_hours
                )

                child2 = ga.mutate(
                    child2,
                    available_hours
                )

                new_population.append(
                    child1
                )

                if len(new_population) < population_size:
                    new_population.append(
                        child2
                    )

            population = new_population

        runtime = (
            time.perf_counter()
            - start_time
        )

        return (
            best_chromosome,
            best_fitness,
            pd.DataFrame(history),
            runtime
        )

    finally:

        ga.POPULATION_SIZE = (
            original_population_size
        )

        ga.GENERATIONS = (
            original_generations
        )

        ga.MUTATION_RATE = (
            original_mutation_rate
        )

        ga.CROSSOVER_RATE = (
            original_crossover_rate
        )

        ga.ELITISM_COUNT = (
            original_elitism_count
        )

        ga.TOURNAMENT_SIZE = (
            original_tournament_size
        )


# =============================================================================
# EXPERIMENT 1
# GA CONVERGENCE
# =============================================================================

def experiment_1_convergence(
    modules,
    available_hours
):

    print_header(
        "EXPERIMENT 1 — GA CONVERGENCE"
    )

    (
        chromosome,
        fitness,
        history,
        runtime
    ) = run_ga_with_history(
        modules=modules,
        available_hours=available_hours,
        random_seed=42,
        population_size=80,
        generations=150,
        mutation_rate=0.15,
        crossover_rate=0.85
    )

    output_file = (
        OUTPUT_DIR
        / "ga_convergence.csv"
    )

    history.to_csv(
        output_file,
        index=False
    )

    print(
        history.tail()
    )

    print()
    print(
        f"Initial best fitness: "
        f"{history.iloc[0]['best_fitness']}"
    )

    print(
        f"Final best fitness: "
        f"{history.iloc[-1]['best_fitness']}"
    )

    print(
        f"Final global best: "
        f"{history.iloc[-1]['global_best_fitness']}"
    )

    print(
        f"Runtime: {runtime:.4f} seconds"
    )

    print(
        f"Saved: {output_file}"
    )

    return history


# =============================================================================
# EXPERIMENT 2
# RANDOM SEEDS
# =============================================================================

def experiment_2_random_seeds(
    modules,
    available_hours
):

    print_header(
        "EXPERIMENT 2 — 30 RANDOM SEEDS"
    )

    rows = []

    for seed in MULTI_SEEDS:

        (
            chromosome,
            fitness,
            history,
            runtime
        ) = run_ga_with_history(
            modules=modules,
            available_hours=available_hours,
            random_seed=seed
        )

        metrics = evaluate_chromosome(
            chromosome,
            modules,
            available_hours
        )

        rows.append(
            {
                "seed": seed,
                "fitness": fitness,
                "total_hours": metrics[
                    "total_hours"
                ],
                "mean_absolute_hour_error": metrics[
                    "mean_absolute_hour_error"
                ],
                "maximum_hour_error": metrics[
                    "maximum_hour_error"
                ],
                "minimum_hours": metrics[
                    "minimum_hours"
                ],
                "maximum_hours": metrics[
                    "maximum_hours"
                ],
                "runtime_seconds": runtime,
            }
        )

    df = pd.DataFrame(
        rows
    )

    output_file = (
        OUTPUT_DIR
        / "ga_multi_seed.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(df)

    print()
    print(
        f"Fitness mean: "
        f"{df['fitness'].mean():.10f}"
    )

    print(
        f"Fitness standard deviation: "
        f"{df['fitness'].std():.10f}"
    )

    print(
        f"Fitness minimum: "
        f"{df['fitness'].min():.10f}"
    )

    print(
        f"Fitness maximum: "
        f"{df['fitness'].max():.10f}"
    )

    print(
        f"Average runtime: "
        f"{df['runtime_seconds'].mean():.4f} seconds"
    )

    print(
        f"Saved: {output_file}"
    )

    return df


# =============================================================================
# BASELINE FUNCTIONS
# =============================================================================

def equal_allocation(
    modules,
    available_hours
):

    number_of_modules = len(
        modules
    )

    chromosome = [
        1
        for _ in range(
            number_of_modules
        )
    ]

    remaining = (
        available_hours
        - number_of_modules
    )

    index = 0

    while remaining > 0:

        chromosome[
            index % number_of_modules
        ] += 1

        remaining -= 1

        index += 1

    return chromosome


def priority_allocation(
    modules,
    available_hours
):

    number_of_modules = len(
        modules
    )

    chromosome = [
        1
        for _ in range(
            number_of_modules
        )
    ]

    remaining = (
        available_hours
        - number_of_modules
    )

    priorities = [
        module.priority
        for module in modules
    ]

    ranked_indices = sorted(
        range(number_of_modules),
        key=lambda index: priorities[index],
        reverse=True
    )

    pointer = 0

    while remaining > 0:

        index = ranked_indices[
            pointer % len(ranked_indices)
        ]

        chromosome[index] += 1

        remaining -= 1

        pointer += 1

    return chromosome


# =============================================================================
# EXPERIMENT 3
# BASELINE COMPARISON
# =============================================================================

def experiment_3_baselines(
    modules,
    available_hours
):

    print_header(
        "EXPERIMENT 3 — BASELINE COMPARISON"
    )

    (
        ga_chromosome,
        ga_fitness,
        history,
        runtime
    ) = run_ga_with_history(
        modules=modules,
        available_hours=available_hours,
        random_seed=42
    )

    equal_chromosome = equal_allocation(
        modules,
        available_hours
    )

    priority_chromosome = priority_allocation(
        modules,
        available_hours
    )

    ga_metrics = evaluate_chromosome(
        ga_chromosome,
        modules,
        available_hours
    )

    equal_metrics = evaluate_chromosome(
        equal_chromosome,
        modules,
        available_hours
    )

    priority_metrics = evaluate_chromosome(
        priority_chromosome,
        modules,
        available_hours
    )

    rows = [
        {
            "method": "Genetic Algorithm",
            **ga_metrics
        },
        {
            "method": "Equal Allocation",
            **equal_metrics
        },
        {
            "method": "Priority Allocation",
            **priority_metrics
        }
    ]

    df = pd.DataFrame(
        rows
    )

    output_file = (
        OUTPUT_DIR
        / "ga_baseline_comparison.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(df)

    print()
    print(
        "GA improvement over Equal Allocation: "
        f"{ga_metrics['fitness'] - equal_metrics['fitness']:.4f}"
    )

    print(
        "GA improvement over Priority Allocation: "
        f"{ga_metrics['fitness'] - priority_metrics['fitness']:.4f}"
    )

    print(
        f"Saved: {output_file}"
    )

    return df


# =============================================================================
# EXPERIMENT 4
# FEASIBILITY
# =============================================================================

def experiment_4_feasibility(
    modules
):

    print_header(
        "EXPERIMENT 4 — FEASIBILITY TESTING"
    )

    number_of_modules = len(
        modules
    )

    rows = []

    for available_hours in FEASIBILITY_SCENARIOS:

        expected_feasible = (
            available_hours
            >= number_of_modules
        )

        actual_feasible = False
        total_allocated_hours = None
        minimum_constraint_satisfied = False

        try:

            chromosome, fitness = (
                ga.optimize_study_plan(
                    modules,
                    available_hours,
                    random_seed=42
                )
            )

            actual_feasible = True

            total_allocated_hours = sum(
                chromosome
            )

            minimum_constraint_satisfied = all(
                hours >= 1
                for hours in chromosome
            )

        except Exception:

            actual_feasible = False

        rows.append(
            {
                "available_hours": available_hours,
                "modules": number_of_modules,
                "expected_feasible": expected_feasible,
                "actual_feasible": actual_feasible,
                "feasibility_correct": (
                    expected_feasible
                    == actual_feasible
                ),
                "total_allocated_hours": total_allocated_hours,
                "minimum_constraint_satisfied": (
                    minimum_constraint_satisfied
                )
            }
        )

    df = pd.DataFrame(
        rows
    )

    output_file = (
        OUTPUT_DIR
        / "ga_feasibility.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(df)

    print()
    print(
        "Feasibility accuracy: "
        f"{df['feasibility_correct'].mean() * 100:.2f}%"
    )

    print(
        f"Saved: {output_file}"
    )

    return df


# =============================================================================
# EXPERIMENT 5
# AVAILABLE HOUR SCENARIOS
# =============================================================================

def experiment_5_hour_scenarios(
    modules
):

    print_header(
        "EXPERIMENT 5 — AVAILABLE HOUR SCENARIOS"
    )

    rows = []

    for available_hours in HOUR_SCENARIOS:

        if available_hours < len(modules):

            rows.append(
                {
                    "available_hours": available_hours,
                    "status": "Infeasible",
                    "fitness": None,
                    "allocated_hours": None,
                    "mean_absolute_hour_error": None,
                    "minimum_module_hours": None,
                    "maximum_module_hours": None,
                }
            )

            continue

        (
            chromosome,
            fitness,
            history,
            runtime
        ) = run_ga_with_history(
            modules,
            available_hours,
            random_seed=42
        )

        mean_error, max_error = (
            calculate_hour_error(
                chromosome,
                modules,
                available_hours
            )
        )

        rows.append(
            {
                "available_hours": available_hours,
                "status": "Feasible",
                "fitness": fitness,
                "allocated_hours": sum(chromosome),
                "mean_absolute_hour_error": mean_error,
                "minimum_module_hours": min(chromosome),
                "maximum_module_hours": max(chromosome),
                "runtime_seconds": runtime,
            }
        )

    df = pd.DataFrame(
        rows
    )

    output_file = (
        OUTPUT_DIR
        / "ga_hour_scenarios.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(df)

    print(
        f"Saved: {output_file}"
    )

    return df


# =============================================================================
# EXPERIMENT 6
# DIFFERENT STUDENT PROFILES
# =============================================================================

def experiment_6_student_profiles(
    students,
    results,
    course_modules,
    degree_modules
):

    print_header(
        "EXPERIMENT 6 — DIFFERENT STUDENT PROFILES"
    )

    rows = []

    for student_id in PROFILE_STUDENTS:

        try:

            (
                student,
                target_semester,
                student_results,
                modules
            ) = get_student_context(
                students,
                results,
                course_modules,
                degree_modules,
                student_id,
                DEFAULT_AVAILABLE_HOURS
            )

            (
                chromosome,
                fitness,
                history,
                runtime
            ) = run_ga_with_history(
                modules,
                DEFAULT_AVAILABLE_HOURS,
                random_seed=42
            )

            current_sgpa = ga.safe_float(
                student.get(
                    "Current_SGPA"
                ),
                None
            )

            academic_risk = str(
                student.get(
                    "Academic_Risk",
                    "Unknown"
                )
            )

            rows.append(
                {
                    "student_id": student_id,
                    "degree_id": student["Degree_ID"],
                    "current_sgpa": current_sgpa,
                    "academic_risk": academic_risk,
                    "target_semester": target_semester,
                    "target_modules": len(modules),
                    "fitness": fitness,
                    "allocated_hours": sum(chromosome),
                    "minimum_hours": min(chromosome),
                    "maximum_hours": max(chromosome),
                    "runtime_seconds": runtime,
                    "status": "Success",
                }
            )

        except Exception as error:

            rows.append(
                {
                    "student_id": student_id,
                    "degree_id": None,
                    "current_sgpa": None,
                    "academic_risk": None,
                    "target_semester": None,
                    "target_modules": None,
                    "fitness": None,
                    "allocated_hours": None,
                    "minimum_hours": None,
                    "maximum_hours": None,
                    "runtime_seconds": None,
                    "status": f"Failed: {error}",
                }
            )

    df = pd.DataFrame(
        rows
    )

    output_file = (
        OUTPUT_DIR
        / "ga_student_profiles.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(df)

    print(
        f"Saved: {output_file}"
    )

    return df


# =============================================================================
# EXPERIMENT 7
# GA PARAMETER SENSITIVITY
# =============================================================================

def experiment_7_parameter_sensitivity(
    modules,
    available_hours
):

    print_header(
        "EXPERIMENT 7 — GA PARAMETER SENSITIVITY"
    )

    rows = []

    for config in PARAMETER_CONFIGURATIONS:

        (
            chromosome,
            fitness,
            history,
            runtime
        ) = run_ga_with_history(
            modules=modules,
            available_hours=available_hours,
            random_seed=42,
            population_size=config[
                "population_size"
            ],
            generations=config[
                "generations"
            ],
            mutation_rate=config[
                "mutation_rate"
            ],
            crossover_rate=config[
                "crossover_rate"
            ]
        )

        metrics = evaluate_chromosome(
            chromosome,
            modules,
            available_hours
        )

        rows.append(
            {
                "configuration": config[
                    "name"
                ],
                "population_size": config[
                    "population_size"
                ],
                "generations": config[
                    "generations"
                ],
                "mutation_rate": config[
                    "mutation_rate"
                ],
                "crossover_rate": config[
                    "crossover_rate"
                ],
                "fitness": fitness,
                "total_hours": metrics[
                    "total_hours"
                ],
                "mean_absolute_hour_error": metrics[
                    "mean_absolute_hour_error"
                ],
                "maximum_hour_error": metrics[
                    "maximum_hour_error"
                ],
                "minimum_hours": metrics[
                    "minimum_hours"
                ],
                "maximum_hours": metrics[
                    "maximum_hours"
                ],
                "runtime_seconds": runtime,
            }
        )

    df = pd.DataFrame(
        rows
    )

    output_file = (
        OUTPUT_DIR
        / "ga_parameter_sensitivity.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(df)

    print()
    print(
        "Fitness range: "
        f"{df['fitness'].min():.4f} - "
        f"{df['fitness'].max():.4f}"
    )

    print(
        "Average runtime: "
        f"{df['runtime_seconds'].mean():.4f} seconds"
    )

    print(
        f"Saved: {output_file}"
    )

    return df


# =============================================================================
# GRAPH 1
# CONVERGENCE
# =============================================================================

def generate_convergence_graph(
    convergence_df
):

    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        convergence_df["generation"],
        convergence_df["best_fitness"],
        label="Generation Best Fitness"
    )

    plt.plot(
        convergence_df["generation"],
        convergence_df["global_best_fitness"],
        label="Global Best Fitness"
    )

    plt.xlabel(
        "Generation"
    )

    plt.ylabel(
        "Fitness"
    )

    plt.title(
        "Genetic Algorithm Convergence"
    )

    plt.legend()

    plt.grid(
        True,
        alpha=0.3
    )

    plt.tight_layout()

    output_file = (
        OUTPUT_DIR
        / "ga_convergence.png"
    )

    plt.savefig(
        output_file,
        dpi=300
    )

    plt.close()

    print(
        f"Saved graph: {output_file}"
    )


# =============================================================================
# GRAPH 2
# BASELINE COMPARISON
# =============================================================================

def generate_baseline_graph(
    baseline_df
):

    plt.figure(
        figsize=(9, 6)
    )

    plt.bar(
        baseline_df["method"],
        baseline_df["fitness"]
    )

    plt.ylabel(
        "Fitness"
    )

    plt.xlabel(
        "Method"
    )

    plt.title(
        "GA Fitness Compared with Baseline Methods"
    )

    plt.xticks(
        rotation=15
    )

    plt.grid(
        axis="y",
        alpha=0.3
    )

    plt.tight_layout()

    output_file = (
        OUTPUT_DIR
        / "ga_baseline_comparison.png"
    )

    plt.savefig(
        output_file,
        dpi=300
    )

    plt.close()

    print(
        f"Saved graph: {output_file}"
    )


# =============================================================================
# GRAPH 3
# AVAILABLE HOURS
# =============================================================================

def generate_hour_scenario_graph(
    hours_df
):

    feasible = hours_df[
        hours_df["status"]
        == "Feasible"
    ].copy()

    if feasible.empty:
        return

    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        feasible["available_hours"],
        feasible["fitness"],
        marker="o"
    )

    plt.xlabel(
        "Available Weekly Study Hours"
    )

    plt.ylabel(
        "GA Fitness"
    )

    plt.title(
        "GA Performance under Different Available-Hour Scenarios"
    )

    plt.grid(
        True,
        alpha=0.3
    )

    plt.tight_layout()

    output_file = (
        OUTPUT_DIR
        / "ga_hour_scenarios.png"
    )

    plt.savefig(
        output_file,
        dpi=300
    )

    plt.close()

    print(
        f"Saved graph: {output_file}"
    )


# =============================================================================
# GRAPH 4
# STUDENT PROFILES
# =============================================================================

def generate_student_profile_graph(
    profile_df
):

    successful = profile_df[
        profile_df["status"]
        == "Success"
    ].copy()

    if successful.empty:
        return

    plt.figure(
        figsize=(10, 6)
    )

    plt.bar(
        successful["student_id"],
        successful["fitness"]
    )

    plt.xlabel(
        "Student Profile"
    )

    plt.ylabel(
        "GA Fitness"
    )

    plt.title(
        "GA Fitness across Different Student Profiles"
    )

    plt.xticks(
        rotation=20
    )

    plt.grid(
        axis="y",
        alpha=0.3
    )

    plt.tight_layout()

    output_file = (
        OUTPUT_DIR
        / "ga_student_profiles.png"
    )

    plt.savefig(
        output_file,
        dpi=300
    )

    plt.close()

    print(
        f"Saved graph: {output_file}"
    )


# =============================================================================
# GRAPH 5
# PARAMETER SENSITIVITY
# =============================================================================

def generate_parameter_graph(
    parameter_df
):

    plt.figure(
        figsize=(12, 6)
    )

    plt.bar(
        parameter_df["configuration"],
        parameter_df["fitness"]
    )

    plt.xlabel(
        "GA Configuration"
    )

    plt.ylabel(
        "Fitness"
    )

    plt.title(
        "GA Parameter Sensitivity"
    )

    plt.xticks(
        rotation=30,
        ha="right"
    )

    plt.grid(
        axis="y",
        alpha=0.3
    )

    plt.tight_layout()

    output_file = (
        OUTPUT_DIR
        / "ga_parameter_sensitivity.png"
    )

    plt.savefig(
        output_file,
        dpi=300
    )

    plt.close()

    print(
        f"Saved graph: {output_file}"
    )


# =============================================================================
# FINAL SUMMARY TABLES
# =============================================================================

def create_summary_tables(
    convergence_df,
    seed_df,
    baseline_df,
    feasibility_df,
    hours_df,
    profile_df,
    parameter_df
):

    # -------------------------------------------------------------------------
    # TABLE 1 — Overall GA performance
    # -------------------------------------------------------------------------

    initial_fitness = (
        convergence_df.iloc[0]["best_fitness"]
    )

    final_fitness = (
        convergence_df.iloc[-1]["global_best_fitness"]
    )

    fitness_improvement = (
        final_fitness
        - initial_fitness
    )

    improvement_percentage = (
        fitness_improvement
        / abs(initial_fitness)
    ) * 100

    overall_df = pd.DataFrame(
        [
            {
                "Metric": "Population Size",
                "Value": ga.POPULATION_SIZE
            },
            {
                "Metric": "Generations",
                "Value": ga.GENERATIONS
            },
            {
                "Metric": "Mutation Rate",
                "Value": ga.MUTATION_RATE
            },
            {
                "Metric": "Crossover Rate",
                "Value": ga.CROSSOVER_RATE
            },
            {
                "Metric": "Initial Best Fitness",
                "Value": initial_fitness
            },
            {
                "Metric": "Final Global Best Fitness",
                "Value": final_fitness
            },
            {
                "Metric": "Fitness Improvement",
                "Value": fitness_improvement
            },
            {
                "Metric": "Improvement Percentage",
                "Value": improvement_percentage
            },
            {
                "Metric": "30-Seed Mean Fitness",
                "Value": seed_df["fitness"].mean()
            },
            {
                "Metric": "30-Seed Fitness Std Dev",
                "Value": seed_df["fitness"].std()
            },
            {
                "Metric": "30-Seed Minimum Fitness",
                "Value": seed_df["fitness"].min()
            },
            {
                "Metric": "30-Seed Maximum Fitness",
                "Value": seed_df["fitness"].max()
            },
            {
                "Metric": "Feasibility Accuracy",
                "Value": (
                    feasibility_df[
                        "feasibility_correct"
                    ].mean()
                    * 100
                )
            }
        ]
    )

    # -------------------------------------------------------------------------
    # TABLE 2 — Baseline improvement
    # -------------------------------------------------------------------------

    ga_fitness = baseline_df.loc[
        baseline_df["method"]
        == "Genetic Algorithm",
        "fitness"
    ].iloc[0]

    equal_fitness = baseline_df.loc[
        baseline_df["method"]
        == "Equal Allocation",
        "fitness"
    ].iloc[0]

    priority_fitness = baseline_df.loc[
        baseline_df["method"]
        == "Priority Allocation",
        "fitness"
    ].iloc[0]

    baseline_summary_df = pd.DataFrame(
        [
            {
                "Comparison": "GA vs Equal Allocation",
                "GA Fitness": ga_fitness,
                "Baseline Fitness": equal_fitness,
                "Fitness Difference": (
                    ga_fitness
                    - equal_fitness
                ),
                "Percentage Difference": (
                    (
                        ga_fitness
                        - equal_fitness
                    )
                    / abs(equal_fitness)
                ) * 100
            },
            {
                "Comparison": "GA vs Priority Allocation",
                "GA Fitness": ga_fitness,
                "Baseline Fitness": priority_fitness,
                "Fitness Difference": (
                    ga_fitness
                    - priority_fitness
                ),
                "Percentage Difference": (
                    (
                        ga_fitness
                        - priority_fitness
                    )
                    / abs(priority_fitness)
                ) * 100
            }
        ]
    )

    # -------------------------------------------------------------------------
    # TABLE 3 — Feasibility summary
    # -------------------------------------------------------------------------

    feasibility_summary_df = pd.DataFrame(
        [
            {
                "Total Scenarios": len(
                    feasibility_df
                ),
                "Correct Scenarios": int(
                    feasibility_df[
                        "feasibility_correct"
                    ].sum()
                ),
                "Feasibility Accuracy (%)": (
                    feasibility_df[
                        "feasibility_correct"
                    ].mean()
                    * 100
                ),
                "Minimum Modules": int(
                    feasibility_df[
                        "modules"
                    ].iloc[0]
                )
            }
        ]
    )

    return (
        overall_df,
        baseline_summary_df,
        feasibility_summary_df
    )


# =============================================================================
# SAVE FINAL EXCEL REPORT
# =============================================================================

def save_excel_report(
    convergence_df,
    seed_df,
    baseline_df,
    feasibility_df,
    hours_df,
    profile_df,
    parameter_df,
    overall_df,
    baseline_summary_df,
    feasibility_summary_df
):

    output_file = (
        OUTPUT_DIR
        / "GA_Final_Evaluation_Summary.xlsx"
    )

    with pd.ExcelWriter(
        output_file,
        engine="openpyxl"
    ) as writer:

        overall_df.to_excel(
            writer,
            sheet_name="Overall Summary",
            index=False
        )

        baseline_summary_df.to_excel(
            writer,
            sheet_name="Baseline Summary",
            index=False
        )

        feasibility_summary_df.to_excel(
            writer,
            sheet_name="Feasibility Summary",
            index=False
        )

        convergence_df.to_excel(
            writer,
            sheet_name="Convergence",
            index=False
        )

        seed_df.to_excel(
            writer,
            sheet_name="30 Random Seeds",
            index=False
        )

        baseline_df.to_excel(
            writer,
            sheet_name="Baseline Comparison",
            index=False
        )

        feasibility_df.to_excel(
            writer,
            sheet_name="Feasibility",
            index=False
        )

        hours_df.to_excel(
            writer,
            sheet_name="Hour Scenarios",
            index=False
        )

        profile_df.to_excel(
            writer,
            sheet_name="Student Profiles",
            index=False
        )

        parameter_df.to_excel(
            writer,
            sheet_name="Parameter Sensitivity",
            index=False
        )

    print()
    print(
        f"Saved Excel report: {output_file}"
    )

    return output_file


# =============================================================================
# FINAL TEXT REPORT
# =============================================================================

def save_text_report(
    convergence_df,
    seed_df,
    baseline_df,
    feasibility_df,
    hours_df,
    profile_df,
    parameter_df
):

    output_file = (
        OUTPUT_DIR
        / "GA_Final_Evaluation_Report.txt"
    )

    initial_fitness = (
        convergence_df.iloc[0]["best_fitness"]
    )

    final_fitness = (
        convergence_df.iloc[-1]["global_best_fitness"]
    )

    fitness_improvement = (
        final_fitness
        - initial_fitness
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "GENETIC ALGORITHM FINAL EVALUATION REPORT\n"
        )

        file.write(
            "=" * 80
            + "\n\n"
        )

        file.write(
            "Experiment 1 — GA Convergence\n"
        )

        file.write(
            f"Initial best fitness: "
            f"{initial_fitness:.6f}\n"
        )

        file.write(
            f"Final global best fitness: "
            f"{final_fitness:.6f}\n"
        )

        file.write(
            f"Fitness improvement: "
            f"{fitness_improvement:.6f}\n\n"
        )

        file.write(
            "Experiment 2 — Random Seed Stability\n"
        )

        file.write(
            f"Number of seeds: "
            f"{len(seed_df)}\n"
        )

        file.write(
            f"Mean fitness: "
            f"{seed_df['fitness'].mean():.6f}\n"
        )

        file.write(
            f"Fitness standard deviation: "
            f"{seed_df['fitness'].std():.6f}\n"
        )

        file.write(
            f"Minimum fitness: "
            f"{seed_df['fitness'].min():.6f}\n"
        )

        file.write(
            f"Maximum fitness: "
            f"{seed_df['fitness'].max():.6f}\n\n"
        )

        file.write(
            "Experiment 3 — Baseline Comparison\n"
        )

        file.write(
            baseline_df.to_string(
                index=False
            )
            + "\n\n"
        )

        file.write(
            "Experiment 4 — Feasibility\n"
        )

        file.write(
            f"Accuracy: "
            f"{feasibility_df['feasibility_correct'].mean() * 100:.2f}%\n\n"
        )

        file.write(
            "Experiment 5 — Available Hours\n"
        )

        file.write(
            hours_df.to_string(
                index=False
            )
            + "\n\n"
        )

        file.write(
            "Experiment 6 — Student Profiles\n"
        )

        file.write(
            profile_df.to_string(
                index=False
            )
            + "\n\n"
        )

        file.write(
            "Experiment 7 — Parameter Sensitivity\n"
        )

        file.write(
            parameter_df.to_string(
                index=False
            )
            + "\n\n"
        )

    print(
        f"Saved text report: {output_file}"
    )

    return output_file


def main():

    print_header(
        "GENETIC ALGORITHM FINAL EVALUATION"
    )

    print(
        f"Project: AI-Based Smart Campus Decision Support System"
    )

    print(
        f"Output directory: {OUTPUT_DIR}"
    )

    # Load data

    students, results, course_modules, degree_modules = (
        ga.load_data()
    )

    # Main evaluation student

    (
        student,
        target_semester,
        student_results,
        modules
    ) = get_student_context(
        students,
        results,
        course_modules,
        degree_modules,
        DEFAULT_STUDENT_ID,
        DEFAULT_AVAILABLE_HOURS
    )

    print()
    print(
        f"Student: {student['Registration_No']}"
    )

    print(
        f"Degree: {student['Degree_ID']}"
    )

    print(
        f"Current semester: "
        f"{student['Current_Semester']}"
    )

    print(
        f"Target semester: "
        f"{target_semester}"
    )

    print(
        f"Target modules: "
        f"{len(modules)}"
    )

    print(
        f"Available hours: "
        f"{DEFAULT_AVAILABLE_HOURS}"
    )

    # Experiment 1

    convergence_df = (
        experiment_1_convergence(
            modules,
            DEFAULT_AVAILABLE_HOURS
        )
    )

    # Experiment 2

    seed_df = (
        experiment_2_random_seeds(
            modules,
            DEFAULT_AVAILABLE_HOURS
        )
    )

    # Experiment 3

    baseline_df = (
        experiment_3_baselines(
            modules,
            DEFAULT_AVAILABLE_HOURS
        )
    )

    # Experiment 4

    feasibility_df = (
        experiment_4_feasibility(
            modules
        )
    )

    # Experiment 5

    hours_df = (
        experiment_5_hour_scenarios(
            modules
        )
    )

    # Experiment 6

    profile_df = (
        experiment_6_student_profiles(
            students,
            results,
            course_modules,
            degree_modules
        )
    )

    # Experiment 7

    parameter_df = (
        experiment_7_parameter_sensitivity(
            modules,
            DEFAULT_AVAILABLE_HOURS
        )
    )

    # Generate graphs

    print_header(
        "GENERATING GRAPHS"
    )

    generate_convergence_graph(
        convergence_df
    )

    generate_baseline_graph(
        baseline_df
    )

    generate_hour_scenario_graph(
        hours_df
    )

    generate_student_profile_graph(
        profile_df
    )

    generate_parameter_graph(
        parameter_df
    )

    # Summary tables

    print_header(
        "GENERATING FINAL SUMMARY TABLES"
    )

    (
        overall_df,
        baseline_summary_df,
        feasibility_summary_df
    ) = create_summary_tables(
        convergence_df,
        seed_df,
        baseline_df,
        feasibility_df,
        hours_df,
        profile_df,
        parameter_df
    )

    print()
    print(
        "OVERALL SUMMARY"
    )

    print(
        overall_df.to_string(
            index=False
        )
    )

    print()
    print(
        "BASELINE SUMMARY"
    )

    print(
        baseline_summary_df.to_string(
            index=False
        )
    )

    print()
    print(
        "FEASIBILITY SUMMARY"
    )

    print(
        feasibility_summary_df.to_string(
            index=False
        )
    )

    # Excel report

    save_excel_report(
        convergence_df,
        seed_df,
        baseline_df,
        feasibility_df,
        hours_df,
        profile_df,
        parameter_df,
        overall_df,
        baseline_summary_df,
        feasibility_summary_df
    )

    # Text report

    save_text_report(
        convergence_df,
        seed_df,
        baseline_df,
        feasibility_df,
        hours_df,
        profile_df,
        parameter_df
    )

    # Final message

    print_header(
        "GA EVALUATION COMPLETE"
    )

    print(
        f"Results directory:\n{OUTPUT_DIR}"
    )

    print()
    print(
        "CSV files:"
    )

    for file in sorted(
        OUTPUT_DIR.glob("*.csv")
    ):
        print(
            f"  - {file.name}"
        )

    print()
    print(
        "Graphs:"
    )

    for file in sorted(
        OUTPUT_DIR.glob("*.png")
    ):
        print(
            f"  - {file.name}"
        )

    print()
    print(
        "Final reports:"
    )

    print(
        "  - GA_Final_Evaluation_Summary.xlsx"
    )

    print(
        "  - GA_Final_Evaluation_Report.txt"
    )

    print()
    print(
        "Use the generated CSV/Excel tables and PNG graphs "
        "in the final report."
    )


if __name__ == "__main__":
    main()