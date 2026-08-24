"""
Final Evaluation of Next Semester SGPA Neural Network

Evaluates the already-trained Neural Network using the saved test predictions and produces detailed metrics and analysis for the project report.

Actual target:
    Next_SGPA

Neural Network prediction:
    Predicted_Next_SGPA_NN

Random Forest prediction:
    Predicted_Next_SGPA_RF
"""

from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PREDICTIONS_FILE = (
    PROJECT_ROOT
    / "data"
    / "ml"
    / "next_sgpa_test_predictions.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "ml"
    / "final_next_sgpa_evaluation_report.txt"
)

DETAILED_OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "ml"
    / "next_sgpa_detailed_evaluation.csv"
)

ACTUAL_COLUMN = "Next_SGPA"

NN_PREDICTED_COLUMN = "Predicted_Next_SGPA_NN"

RF_PREDICTED_COLUMN = "Predicted_Next_SGPA_RF"

def print_section(title):
    """Print formatted section heading."""

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def load_predictions():
    """Load saved test predictions."""

    if not PREDICTIONS_FILE.exists():
        raise FileNotFoundError(
            f"Prediction file not found:\n{PREDICTIONS_FILE}"
        )

    df = pd.read_csv(PREDICTIONS_FILE)

    if df.empty:
        raise ValueError(
            "Prediction file is empty."
        )

    return df


def calculate_metrics(y_true, y_pred):
    """Calculate MAE, RMSE and R²."""

    mae = mean_absolute_error(
        y_true,
        y_pred
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_true,
            y_pred
        )
    )

    r2 = r2_score(
        y_true,
        y_pred
    )

    return mae, rmse, r2


def main():

    print("=" * 70)
    print("FINAL NEXT SEMESTER SGPA MODEL EVALUATION")
    print("=" * 70)

    print()
    print("Prediction file:")
    print(PREDICTIONS_FILE)

    df = load_predictions()

    print()
    print(f"Prediction records: {len(df)}")

    print()
    print("Available columns:")
    print(list(df.columns))


    print_section(
        "COLUMN VALIDATION"
    )

    required_columns = [
        ACTUAL_COLUMN,
        NN_PREDICTED_COLUMN,
        RF_PREDICTED_COLUMN,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Required prediction columns are missing.\n"
            f"Missing columns: {missing_columns}\n"
            f"Available columns: {list(df.columns)}"
        )

    print(
        f"Actual column    : {ACTUAL_COLUMN}"
    )

    print(
        f"NN prediction    : {NN_PREDICTED_COLUMN}"
    )

    print(
        f"RF prediction    : {RF_PREDICTED_COLUMN}"
    )

    print(
        "\nRequired prediction columns: PASS"
    )

    for column in [
        ACTUAL_COLUMN,
        NN_PREDICTED_COLUMN,
        RF_PREDICTED_COLUMN,
    ]:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


    before = len(df)

    df = df.dropna(
        subset=[
            ACTUAL_COLUMN,
            NN_PREDICTED_COLUMN,
            RF_PREDICTED_COLUMN,
        ]
    ).copy()

    removed = before - len(df)

    print()
    print(
        f"Invalid prediction rows removed: {removed}"
    )

    if df.empty:

        raise ValueError(
            "No valid prediction records remain."
        )


    print_section(
        "1. PREDICTION RANGE VALIDATION"
    )

    actual_invalid = (
        (df[ACTUAL_COLUMN] < 0.0)
        |
        (df[ACTUAL_COLUMN] > 4.0)
    ).sum()

    nn_invalid = (
        (df[NN_PREDICTED_COLUMN] < 0.0)
        |
        (df[NN_PREDICTED_COLUMN] > 4.0)
    ).sum()

    rf_invalid = (
        (df[RF_PREDICTED_COLUMN] < 0.0)
        |
        (df[RF_PREDICTED_COLUMN] > 4.0)
    ).sum()

    print(
        f"Invalid actual Next_SGPA values       : "
        f"{actual_invalid}"
    )

    print(
        f"Invalid NN prediction values           : "
        f"{nn_invalid}"
    )

    print(
        f"Invalid RF prediction values           : "
        f"{rf_invalid}"
    )

    y_true = df[
        ACTUAL_COLUMN
    ].to_numpy()

    y_pred_nn = df[
        NN_PREDICTED_COLUMN
    ].to_numpy()

    y_pred_rf = df[
        RF_PREDICTED_COLUMN
    ].to_numpy()

    # NEURAL NETWORK PERFORMANCE
    print_section(
        "2. NEURAL NETWORK OVERALL PERFORMANCE"
    )

    nn_mae, nn_rmse, nn_r2 = calculate_metrics(
        y_true,
        y_pred_nn
    )

    print(
        f"MAE  : {nn_mae:.4f}"
    )

    print(
        f"RMSE : {nn_rmse:.4f}"
    )

    print(
        f"R²   : {nn_r2:.4f}"
    )

    # RANDOM FOREST PERFORMANCE
    print_section(
        "3. RANDOM FOREST PERFORMANCE"
    )

    rf_mae, rf_rmse, rf_r2 = calculate_metrics(
        y_true,
        y_pred_rf
    )

    print(
        f"MAE  : {rf_mae:.4f}"
    )

    print(
        f"RMSE : {rf_rmse:.4f}"
    )

    print(
        f"R²   : {rf_r2:.4f}"
    )

    # MODEL COMPARISON
    print_section(
        "4. MODEL COMPARISON"
    )

    comparison = pd.DataFrame(
        {
            "Model": [
                "Random Forest",
                "Neural Network",
            ],
            "MAE": [
                rf_mae,
                nn_mae,
            ],
            "RMSE": [
                rf_rmse,
                nn_rmse,
            ],
            "R2": [
                rf_r2,
                nn_r2,
            ],
        }
    )

    print(
        comparison.to_string(
            index=False
        )
    )

    if nn_rmse < rf_rmse:
        best_model = "Neural Network"
    else:
        best_model = "Random Forest"

    print()
    print(
        f"Best model based on RMSE: {best_model}"
    )

    # NEURAL NETWORK ERROR ANALYSIS
    print_section(
        "5. NEURAL NETWORK PREDICTION ERROR ANALYSIS"
    )

    df["NN_Error"] = (
        df[NN_PREDICTED_COLUMN]
        -
        df[ACTUAL_COLUMN]
    )

    df["NN_Absolute_Error"] = (
        df["NN_Error"].abs()
    )

    print(
        f"Mean Error          : "
        f"{df['NN_Error'].mean():.4f}"
    )

    print(
        f"Mean Absolute Error : "
        f"{df['NN_Absolute_Error'].mean():.4f}"
    )

    print(
        f"Minimum Error       : "
        f"{df['NN_Error'].min():.4f}"
    )

    print(
        f"Maximum Error       : "
        f"{df['NN_Error'].max():.4f}"
    )

    # PREDICTION ACCURACY WITHIN GPA TOLERANCE
    print_section(
        "6. PREDICTION ACCURACY WITHIN GPA TOLERANCE"
    )

    tolerance_levels = [
        0.10,
        0.20,
        0.30,
        0.50,
    ]

    tolerance_results = []

    for tolerance in tolerance_levels:

        count = (
            df["NN_Absolute_Error"]
            <= tolerance
        ).sum()

        percentage = (
            count
            /
            len(df)
        ) * 100

        tolerance_results.append(
            (
                tolerance,
                count,
                percentage,
            )
        )

        print(
            f"Within ±{tolerance:.2f}: "
            f"{count} / {len(df)} "
            f"({percentage:.2f}%)"
        )

    # OVER / UNDER PREDICTION
    print_section(
        "7. OVER-PREDICTION / UNDER-PREDICTION"
    )

    over = (
        df["NN_Error"] > 0
    ).sum()

    under = (
        df["NN_Error"] < 0
    ).sum()

    exact = (
        df["NN_Error"] == 0
    ).sum()

    print(
        f"Over-predicted : {over} "
        f"({over / len(df) * 100:.2f}%)"
    )

    print(
        f"Under-predicted: {under} "
        f"({under / len(df) * 100:.2f}%)"
    )

    print(
        f"Exact          : {exact} "
        f"({exact / len(df) * 100:.2f}%)"
    )

    # PERFORMANCE BY ACTUAL GPA RANGE
    print_section(
        "8. PERFORMANCE BY ACTUAL GPA RANGE"
    )

    bins = [
        0.0,
        2.0,
        2.5,
        3.0,
        3.5,
        4.01,
    ]

    labels = [
        "Below 2.0",
        "2.0 - 2.49",
        "2.5 - 2.99",
        "3.0 - 3.49",
        "3.5 - 4.0",
    ]

    df["GPA_Range"] = pd.cut(
        df[ACTUAL_COLUMN],
        bins=bins,
        labels=labels,
        right=False,
        include_lowest=True,
    )

    range_results = []

    for label in labels:

        group = df[
            df["GPA_Range"] == label
        ]

        if len(group) == 0:
            continue

        group_mae = mean_absolute_error(
            group[ACTUAL_COLUMN],
            group[NN_PREDICTED_COLUMN],
        )

        group_rmse = np.sqrt(
            mean_squared_error(
                group[ACTUAL_COLUMN],
                group[NN_PREDICTED_COLUMN],
            )
        )

        range_results.append(
            (
                label,
                len(group),
                group_mae,
                group_rmse,
            )
        )

        print()
        print(
            f"Range: {label}"
        )

        print(
            f"Records: {len(group)}"
        )

        print(
            f"MAE   : {group_mae:.4f}"
        )

        print(
            f"RMSE  : {group_rmse:.4f}"
        )

    # ACTUAL VS PREDICTED STATISTICS
    print_section(
        "9. ACTUAL VS PREDICTED STATISTICS"
    )

    print(
        f"Actual mean      : "
        f"{df[ACTUAL_COLUMN].mean():.4f}"
    )

    print(
        f"Predicted mean   : "
        f"{df[NN_PREDICTED_COLUMN].mean():.4f}"
    )

    print(
        f"Actual median    : "
        f"{df[ACTUAL_COLUMN].median():.4f}"
    )

    print(
        f"Predicted median : "
        f"{df[NN_PREDICTED_COLUMN].median():.4f}"
    )

    print(
        f"Actual minimum   : "
        f"{df[ACTUAL_COLUMN].min():.4f}"
    )

    print(
        f"Predicted minimum: "
        f"{df[NN_PREDICTED_COLUMN].min():.4f}"
    )

    print(
        f"Actual maximum   : "
        f"{df[ACTUAL_COLUMN].max():.4f}"
    )

    print(
        f"Predicted maximum: "
        f"{df[NN_PREDICTED_COLUMN].max():.4f}"
    )

    print_section(
        "10. LARGEST NEURAL NETWORK PREDICTION ERRORS"
    )

    worst = df.sort_values(
        "NN_Absolute_Error",
        ascending=False
    ).head(10)

    display_columns = []

    for column in [
        "Student_ID",
        "Degree_ID",
        "Intake",
        "Gender",
        "Current_Year",
        "Current_Semester",
        "Previous_SGPA",
        "Current_SGPA",
        "Repeated_Courses",
        ACTUAL_COLUMN,
        NN_PREDICTED_COLUMN,
        "NN_Error",
        "NN_Absolute_Error",
    ]:

        if column in worst.columns:
            display_columns.append(column)

    print(
        worst[
            display_columns
        ].to_string(
            index=False
        )
    )

    print_section(
        "11. CLOSEST NEURAL NETWORK PREDICTIONS"
    )

    best = df.sort_values(
        "NN_Absolute_Error",
        ascending=True
    ).head(10)

    print(
        best[
            display_columns
        ].to_string(
            index=False
        )
    )

    print_section(
        "12. STUDENT-LEVEL TEST SET CHECK"
    )

    if "Student_ID" in df.columns:

        unique_students = (
            df["Student_ID"]
            .nunique()
        )

        print(
            f"Unique students in test set: "
            f"{unique_students}"
        )

        duplicate_student_records = (
            df["Student_ID"]
            .duplicated()
            .sum()
        )

        print(
            f"Additional records from students "
            f"with multiple semesters: "
            f"{duplicate_student_records}"
        )

        print(
            "The training script performed the "
            "train/test split at student level."
        )

    else:

        print(
            "Student_ID column is not available."
        )

    df.to_csv(
        DETAILED_OUTPUT_FILE,
        index=False
    )

    print_section(
        "13. OUTPUT FILES"
    )

    print(
        "Detailed evaluation data saved to:"
    )

    print(
        DETAILED_OUTPUT_FILE
    )

    report_lines = []

    report_lines.append(
        "FINAL NEXT SEMESTER SGPA MODEL EVALUATION"
    )

    report_lines.append(
        "=" * 70
    )

    report_lines.append("")

    report_lines.append(
        "MODEL"
    )

    report_lines.append(
        "Neural Network"
    )

    report_lines.append(
        f"Prediction column: {NN_PREDICTED_COLUMN}"
    )

    report_lines.append(
        f"Actual column: {ACTUAL_COLUMN}"
    )

    report_lines.append("")

    report_lines.append(
        f"Prediction records: {len(df)}"
    )

    report_lines.append("")

    # OVERALL PERFORMANCE
    report_lines.append(
        "NEURAL NETWORK OVERALL PERFORMANCE"
    )

    report_lines.append(
        f"MAE  : {nn_mae:.4f}"
    )

    report_lines.append(
        f"RMSE : {nn_rmse:.4f}"
    )

    report_lines.append(
        f"R2   : {nn_r2:.4f}"
    )

    report_lines.append("")

    # RANDOM FOREST
    report_lines.append(
        "RANDOM FOREST PERFORMANCE"
    )

    report_lines.append(
        f"MAE  : {rf_mae:.4f}"
    )

    report_lines.append(
        f"RMSE : {rf_rmse:.4f}"
    )

    report_lines.append(
        f"R2   : {rf_r2:.4f}"
    )

    report_lines.append("")

    report_lines.append(
        f"Best model based on RMSE: {best_model}"
    )

    report_lines.append("")

    report_lines.append(
        "NEURAL NETWORK ERROR ANALYSIS"
    )

    report_lines.append(
        f"Mean Error          : "
        f"{df['NN_Error'].mean():.4f}"
    )

    report_lines.append(
        f"Mean Absolute Error : "
        f"{df['NN_Absolute_Error'].mean():.4f}"
    )

    report_lines.append(
        f"Minimum Error       : "
        f"{df['NN_Error'].min():.4f}"
    )

    report_lines.append(
        f"Maximum Error       : "
        f"{df['NN_Error'].max():.4f}"
    )

    report_lines.append("")

    report_lines.append(
        "PREDICTION ACCURACY WITHIN GPA TOLERANCE"
    )

    for tolerance, count, percentage in tolerance_results:

        report_lines.append(
            f"Within +/- {tolerance:.2f}: "
            f"{count}/{len(df)} "
            f"({percentage:.2f}%)"
        )

    report_lines.append("")

    report_lines.append(
        "OVER / UNDER PREDICTION"
    )

    report_lines.append(
        f"Over-predicted : {over}"
    )

    report_lines.append(
        f"Under-predicted: {under}"
    )

    report_lines.append(
        f"Exact          : {exact}"
    )

    report_lines.append("")

    report_lines.append(
        "PERFORMANCE BY GPA RANGE"
    )

    for (
        label,
        count,
        group_mae,
        group_rmse,
    ) in range_results:

        report_lines.append(
            f"{label}: "
            f"Records={count}, "
            f"MAE={group_mae:.4f}, "
            f"RMSE={group_rmse:.4f}"
        )

    report_lines.append("")

    report_lines.append(
        "ACTUAL VS PREDICTED STATISTICS"
    )

    report_lines.append(
        f"Actual mean      : "
        f"{df[ACTUAL_COLUMN].mean():.4f}"
    )

    report_lines.append(
        f"Predicted mean   : "
        f"{df[NN_PREDICTED_COLUMN].mean():.4f}"
    )

    report_lines.append(
        f"Actual median    : "
        f"{df[ACTUAL_COLUMN].median():.4f}"
    )

    report_lines.append(
        f"Predicted median : "
        f"{df[NN_PREDICTED_COLUMN].median():.4f}"
    )

    report_lines.append("")

    report_lines.append(
        "CONCLUSION"
    )

    report_lines.append(
        "The Neural Network was evaluated using the held-out "
        "student-level test set."
    )

    report_lines.append(
        "The test set was separated at student level to prevent "
        "the same student's records from appearing in both "
        "training and testing datasets."
    )

    report_lines.append(
        f"The final test MAE was {nn_mae:.4f}, "
        f"RMSE was {nn_rmse:.4f}, and R2 was {nn_r2:.4f}."
    )

    report_lines.append(
        f"The Random Forest baseline achieved an MAE of "
        f"{rf_mae:.4f}, RMSE of {rf_rmse:.4f}, "
        f"and R2 of {rf_r2:.4f}."
    )

    report_lines.append(
        f"Based on RMSE, the selected best model was "
        f"{best_model}."
    )

    report_lines.append(
        "Next_SGPA was used as the prediction target and "
        "was not used as an input feature."
    )

    report_lines.append(
        "The results should be interpreted as predictive "
        "performance on the synthetic project dataset and "
        "not as official university academic predictions."
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        "\n".join(report_lines),
        encoding="utf-8"
    )

    print()
    print(
        "Evaluation report saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print_section(
        "FINAL EVALUATION SUMMARY"
    )

    print(
        f"Test records : {len(df)}"
    )

    print(
        f"Neural Network MAE  : "
        f"{nn_mae:.4f}"
    )

    print(
        f"Neural Network RMSE : "
        f"{nn_rmse:.4f}"
    )

    print(
        f"Neural Network R²   : "
        f"{nn_r2:.4f}"
    )

    print()

    print(
        f"Random Forest MAE   : "
        f"{rf_mae:.4f}"
    )

    print(
        f"Random Forest RMSE  : "
        f"{rf_rmse:.4f}"
    )

    print(
        f"Random Forest R²    : "
        f"{rf_r2:.4f}"
    )

    print()

    print(
        f"Best model           : "
        f"{best_model}"
    )

    print()

    print(
        "Model evaluation completed successfully."
    )


if __name__ == "__main__":
    main()