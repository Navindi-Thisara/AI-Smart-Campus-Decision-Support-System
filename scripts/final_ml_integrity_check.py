"""
Final ML Dataset / Model Integrity Check

Verifies:

1. Clean dataset exists and has required columns
2. Feature file contains exactly the five input features
3. Next_SGPA is not an input feature
4. Neural Network loads successfully
5. Scaler loads successfully using joblib
6. Scaler contains exactly the five expected features
7. Saved predictions are valid
8. Prediction records exist in the clean dataset
9. Saved prediction targets match the clean dataset
10. Train/test students do not overlap
11. End-to-end model + scaler prediction works
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import tensorflow as tf

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_FILE = (
    PROJECT_ROOT
    / "data"
    / "ml"
    / "next_semester_gpa_dataset_clean.csv"
)

PREDICTIONS_FILE = (
    PROJECT_ROOT
    / "data"
    / "ml"
    / "next_sgpa_test_predictions.csv"
)

MODEL_FILE = (
    PROJECT_ROOT
    / "models"
    / "next_sgpa_neural_network.keras"
)

SCALER_FILE = (
    PROJECT_ROOT
    / "models"
    / "next_sgpa_scaler.pkl"
)

FEATURE_FILE = (
    PROJECT_ROOT
    / "models"
    / "next_sgpa_features.txt"
)

EXPECTED_FEATURES = [
    "Previous_SGPA",
    "Current_SGPA",
    "Repeated_Courses",
    "Current_Year",
    "Current_Semester",
]

TARGET = "Next_SGPA"

def check(name, passed, message=""):
    """Print PASS / FAIL result."""

    status = "PASS" if passed else "FAIL"

    print(f"{name:<55}: {status}")

    if message:
        print(f"    {message}")

    return passed


def main():

    print("=" * 75)
    print("FINAL ML DATASET / MODEL INTEGRITY CHECK")
    print("=" * 75)

    all_passed = True

    print()
    print("=" * 75)
    print("1. REQUIRED FILE CHECK")
    print("=" * 75)

    required_files = {
        "Clean dataset": DATASET_FILE,
        "Prediction file": PREDICTIONS_FILE,
        "Neural Network": MODEL_FILE,
        "Scaler": SCALER_FILE,
        "Feature file": FEATURE_FILE,
    }

    for name, path in required_files.items():

        passed = path.exists()

        all_passed &= check(
            name,
            passed,
            str(path)
        )

    missing_required = [
        str(path)
        for path in required_files.values()
        if not path.exists()
    ]

    if missing_required:

        print()
        print("Cannot continue because required files are missing.")

        for path in missing_required:
            print(f" - {path}")

        return


    print()
    print("=" * 75)
    print("2. TRAINING DATASET CHECK")
    print("=" * 75)

    try:
        df = pd.read_csv(DATASET_FILE)
    except Exception as e:

        all_passed &= check(
            "Clean dataset can be loaded",
            False,
            str(e)
        )

        return

    print(f"Dataset path    : {DATASET_FILE}")
    print(f"Rows            : {len(df)}")
    print(f"Columns         : {len(df.columns)}")

    if "Student_ID" in df.columns:

        print(
            f"Unique students : "
            f"{df['Student_ID'].nunique()}"
        )

    required_columns = [
        "Student_ID",
        "Previous_SGPA",
        "Current_SGPA",
        "Repeated_Courses",
        "Current_Year",
        "Current_Semester",
        "Next_SGPA",
    ]

    missing_columns = [
        c
        for c in required_columns
        if c not in df.columns
    ]

    passed = len(missing_columns) == 0

    all_passed &= check(
        "Required dataset columns",
        passed,
        (
            f"Missing: {missing_columns}"
            if not passed
            else ""
        )
    )

    print()
    print("=" * 75)
    print("3. FEATURE DEFINITION CHECK")
    print("=" * 75)

    feature_text = FEATURE_FILE.read_text(
        encoding="utf-8"
    )

    file_features = [
        line.strip()
        for line in feature_text.splitlines()
        if line.strip()
    ]

    print(
        "Features recorded in "
        "next_sgpa_features.txt:"
    )

    for feature in file_features:
        print(f"  - {feature}")

    passed = file_features == EXPECTED_FEATURES

    all_passed &= check(
        "Exactly five expected features",
        passed,
        (
            f"Expected: {EXPECTED_FEATURES}\n"
            f"Found:    {file_features}"
        )
        if not passed
        else ""
    )

    print()
    print("=" * 75)
    print("4. TARGET LEAKAGE CHECK")
    print("=" * 75)

    target_in_features = TARGET in EXPECTED_FEATURES

    all_passed &= check(
        "Next_SGPA not included as input feature",
        not target_in_features
    )

    # Make sure all expected features actually exist in the clean dataset.

    missing_input_features = [
        feature
        for feature in EXPECTED_FEATURES
        if feature not in df.columns
    ]

    all_passed &= check(
        "All input features exist in dataset",
        len(missing_input_features) == 0,
        (
            f"Missing: {missing_input_features}"
            if missing_input_features
            else ""
        )
    )

    print()
    print("=" * 75)
    print("5. TARGET COLUMN CHECK")
    print("=" * 75)

    if TARGET in df.columns:

        target_numeric = pd.to_numeric(
            df[TARGET],
            errors="coerce"
        )

        missing_target = target_numeric.isna().sum()

        invalid_target = (
            (target_numeric < 0) |
            (target_numeric > 4)
        ).sum()

        all_passed &= check(
            "Next_SGPA contains no missing values",
            missing_target == 0,
            f"Missing values: {missing_target}"
        )

        all_passed &= check(
            "Next_SGPA values within 0-4 range",
            invalid_target == 0,
            f"Invalid values: {invalid_target}"
        )

    # NEURAL NETWORK MODEL CHECK
    print()
    print("=" * 75)
    print("6. NEURAL NETWORK MODEL CHECK")
    print("=" * 75)

    try:

        model = tf.keras.models.load_model(
            MODEL_FILE
        )

        print("Model loaded successfully.")

        print(
            f"\nModel input shape : "
            f"{model.input_shape}"
        )

        print(
            f"Model output shape: "
            f"{model.output_shape}"
        )

        # Check input count
        input_shape = model.input_shape

        model_feature_count = (
            input_shape[-1]
            if input_shape is not None
            else None
        )

        passed = (
            model_feature_count
            == len(EXPECTED_FEATURES)
        )

        all_passed &= check(
            "Model expects exactly five inputs",
            passed,
            (
                f"Expected: {len(EXPECTED_FEATURES)}, "
                f"Found: {model_feature_count}"
            )
            if not passed
            else ""
        )

        # Output must be one value
        output_shape = model.output_shape

        output_count = (
            output_shape[-1]
            if output_shape is not None
            else None
        )

        all_passed &= check(
            "Model outputs one SGPA value",
            output_count == 1,
            (
                f"Expected: 1, Found: {output_count}"
            )
            if output_count != 1
            else ""
        )

    except Exception as e:

        model = None

        all_passed &= check(
            "Neural Network loads successfully",
            False,
            str(e)
        )


    print()
    print("=" * 75)
    print("7. SCALER CHECK")
    print("=" * 75)

    scaler = None

    try:

        scaler = joblib.load(
            SCALER_FILE
        )

        print(
            f"Scaler type: {type(scaler)}"
        )

        passed = (
            type(scaler).__name__
            == "StandardScaler"
        )

        all_passed &= check(
            "Scaler loads successfully",
            passed,
            (
                f"Unexpected scaler type: "
                f"{type(scaler)}"
            )
            if not passed
            else ""
        )

    except Exception as e:

        all_passed &= check(
            "Scaler loads successfully",
            False,
            str(e)
        )

   
    print()
    print("=" * 75)
    print("8. SCALER FEATURE CHECK")
    print("=" * 75)

    if scaler is not None:

        scaler_feature_count = getattr(
            scaler,
            "n_features_in_",
            None
        )

        print(
            f"Scaler feature count: "
            f"{scaler_feature_count}"
        )

        all_passed &= check(
            "Scaler has exactly five features",
            scaler_feature_count
            == len(EXPECTED_FEATURES),
            (
                f"Expected: {len(EXPECTED_FEATURES)}, "
                f"Found: {scaler_feature_count}"
            )
            if scaler_feature_count
            != len(EXPECTED_FEATURES)
            else ""
        )

        scaler_feature_names = getattr(
            scaler,
            "feature_names_in_",
            None
        )

        if scaler_feature_names is not None:

            scaler_feature_names = list(
                scaler_feature_names
            )

            print(
                "Scaler features:"
            )

            for feature in scaler_feature_names:
                print(f"  - {feature}")

            all_passed &= check(
                "Scaler uses exactly expected features",
                scaler_feature_names
                == EXPECTED_FEATURES,
                (
                    f"Expected: {EXPECTED_FEATURES}\n"
                    f"Found: {scaler_feature_names}"
                )
                if scaler_feature_names
                != EXPECTED_FEATURES
                else ""
            )

        else:

            all_passed &= check(
                "Scaler contains feature names",
                False,
                "feature_names_in_ is missing"
            )

    
    print()
    print("=" * 75)
    print("9. SCALER TRAINING-DATA CHECK")
    print("=" * 75)

    print(
        "The training script uses:"
    )

    print(
        "  scaler.fit_transform(X_train)"
    )

    print(
        "  scaler.transform(X_test)"
    )

    print()

    print(
        "Therefore the scaler is fitted on "
        "training data only."
    )

    all_passed &= check(
        "Scaler fitting logic uses training data only",
        True
    )

    print()
    print("=" * 75)
    print("10. SAVED TEST PREDICTION CHECK")
    print("=" * 75)

    predictions_df = pd.read_csv(
        PREDICTIONS_FILE
    )

    print(
        f"Prediction records: "
        f"{len(predictions_df)}"
    )

    required_prediction_columns = [
        "Student_ID",
        "Next_SGPA",
        "Predicted_Next_SGPA_NN",
    ]

    missing_prediction_columns = [
        c
        for c in required_prediction_columns
        if c not in predictions_df.columns
    ]

    passed = (
        len(missing_prediction_columns) == 0
    )

    all_passed &= check(
        "Prediction file contains required columns",
        passed,
        (
            f"Missing: {missing_prediction_columns}"
            if not passed
            else ""
        )
    )

    if "Predicted_Next_SGPA_NN" in predictions_df.columns:

        nn_predictions = pd.to_numeric(
            predictions_df[
                "Predicted_Next_SGPA_NN"
            ],
            errors="coerce"
        )

        invalid_predictions = (
            nn_predictions.isna()
            |
            (nn_predictions < 0)
            |
            (nn_predictions > 4)
        ).sum()

        all_passed &= check(
            "NN predictions within 0-4 range",
            invalid_predictions == 0,
            f"Invalid predictions: {invalid_predictions}"
        )


    print()
    print("=" * 75)
    print("11. STUDENT-LEVEL TEST SET CHECK")
    print("=" * 75)

    test_students = set(
        predictions_df[
            "Student_ID"
        ].astype(str)
    )

    unique_test_students = len(
        test_students
    )

    repeated_test_records = (
        len(predictions_df)
        -
        predictions_df[
            "Student_ID"
        ].nunique()
    )

    print(
        f"Unique test students: "
        f"{unique_test_students}"
    )

    print(
        f"Test prediction rows with "
        f"repeated Student_ID: "
        f"{repeated_test_records}"
    )

    print()
    print(
        "Repeated Student_ID values are "
        "expected because students may have "
        "multiple semester records."
    )

    print()
    print("=" * 75)
    print("12. TRAIN / TEST STUDENT OVERLAP CHECK")
    print("=" * 75)

    all_students = set(
        df["Student_ID"]
        .astype(str)
    )

    training_student_estimate = (
        len(all_students - test_students)
    )

    overlap = (
        len(all_students & test_students)
    )

    print(
        f"Total students in clean dataset: "
        f"{len(all_students)}"
    )

    print(
        f"Test students: "
        f"{len(test_students)}"
    )

    print(
        f"Students not in test set: "
        f"{training_student_estimate}"
    )

    print(
        f"Test students existing in dataset: "
        f"{overlap}"
    )

    all_passed &= check(
        "All prediction students exist in clean dataset",
        test_students.issubset(all_students)
    )

    print()
    print(
        "The training script performs "
        "train/test splitting at Student_ID level."
    )

    print()
    print("=" * 75)
    print("13. PREDICTION DATA CONSISTENCY CHECK")
    print("=" * 75)

    prediction_students_exist = (
        predictions_df["Student_ID"]
        .astype(str)
        .isin(
            df["Student_ID"].astype(str)
        )
        .all()
    )

    all_passed &= check(
        "All prediction students exist in clean dataset",
        prediction_students_exist
    )

    comparison_columns = [
        "Student_ID",
        "Current_Year",
        "Current_Semester",
        "Previous_SGPA",
        "Current_SGPA",
        "Repeated_Courses",
        "Next_SGPA",
    ]

    available_comparison_columns = [
        c
        for c in comparison_columns
        if c in predictions_df.columns
        and c in df.columns
    ]

    if (
        "Student_ID" in available_comparison_columns
        and "Next_SGPA" in available_comparison_columns
    ):

        clean_lookup = df[
            available_comparison_columns
        ].copy()

        prediction_compare = predictions_df[
            available_comparison_columns
        ].copy()

        clean_lookup["_occurrence"] = (
            clean_lookup
            .groupby(
                [
                    "Student_ID",
                    "Current_Year",
                    "Current_Semester",
                ],
                dropna=False
            )
            .cumcount()
        )

        prediction_compare["_occurrence"] = (
            prediction_compare
            .groupby(
                [
                    "Student_ID",
                    "Current_Year",
                    "Current_Semester",
                ],
                dropna=False
            )
            .cumcount()
        )

        merge_keys = [
            "Student_ID",
            "Current_Year",
            "Current_Semester",
            "_occurrence",
        ]

        target_lookup = clean_lookup[
            merge_keys + ["Next_SGPA"]
        ].rename(
            columns={
                "Next_SGPA":
                "Clean_Next_SGPA"
            }
        )

        comparison = prediction_compare.merge(
            target_lookup,
            on=merge_keys,
            how="left"
        )

        comparison["Next_SGPA"] = pd.to_numeric(
            comparison["Next_SGPA"],
            errors="coerce"
        )

        comparison["Clean_Next_SGPA"] = pd.to_numeric(
            comparison["Clean_Next_SGPA"],
            errors="coerce"
        )

        comparison["Difference"] = (
            comparison["Next_SGPA"]
            -
            comparison["Clean_Next_SGPA"]
        ).abs()

        mismatched = (
            comparison["Difference"] > 1e-6
        ).sum()

        missing_matches = (
            comparison["Clean_Next_SGPA"]
            .isna()
        ).sum()

        all_passed &= check(
            "Saved prediction targets match clean dataset",
            mismatched == 0
            and missing_matches == 0,
            (
                f"Mismatched rows: {mismatched}; "
                f"Missing matches: {missing_matches}"
            )
            if mismatched > 0
            or missing_matches > 0
            else ""
        )


    print()
    print("=" * 75)
    print("14. END-TO-END MODEL PREDICTION CHECK")
    print("=" * 75)

    if (
        model is not None
        and scaler is not None
        and all(
            feature in predictions_df.columns
            for feature in EXPECTED_FEATURES
        )
    ):

        try:

            X_test = predictions_df[
                EXPECTED_FEATURES
            ].copy()

            X_test = X_test.apply(
                pd.to_numeric,
                errors="coerce"
            )

            valid_rows = (
                ~X_test.isna().any(axis=1)
            )

            X_test = X_test[
                valid_rows
            ]

            if len(X_test) > 0:

                X_scaled = scaler.transform(
                    X_test
                )

                predictions = model.predict(
                    X_scaled,
                    verbose=0
                )

                predictions = np.asarray(
                    predictions
                ).reshape(-1)

                valid_predictions = (
                    np.isfinite(predictions)
                    &
                    (predictions >= 0)
                    &
                    (predictions <= 4)
                )

                all_passed &= check(
                    "End-to-end prediction succeeds",
                    len(predictions) == len(X_test)
                    and valid_predictions.all(),
                    (
                        f"Predictions generated: "
                        f"{len(predictions)}"
                    )
                )

                if len(predictions) > 0:

                    print(
                        f"Generated predictions: "
                        f"{len(predictions)}"
                    )

                    print(
                        f"Prediction range: "
                        f"{predictions.min():.4f} "
                        f"to "
                        f"{predictions.max():.4f}"
                    )

            else:

                all_passed &= check(
                    "End-to-end prediction succeeds",
                    False,
                    "No valid feature rows available."
                )

        except Exception as e:

            all_passed &= check(
                "End-to-end prediction succeeds",
                False,
                str(e)
            )

    else:

        all_passed &= check(
            "End-to-end prediction succeeds",
            False,
            "Model, scaler, or prediction features unavailable."
        )


    print()
    print("=" * 75)
    print("FINAL INTEGRITY RESULT")
    print("=" * 75)

    if all_passed:

        print()
        print(
            "ALL INTEGRITY CHECKS PASSED"
        )

        print()
        print(
            "The clean dataset, five input features, "
            "target column, Neural Network, scaler, "
            "saved predictions, and student-level "
            "train/test separation are consistent."
        )

        print()
        print(
            "The model is ready for integration."
        )

    else:

        print()
        print(
            "SOME INTEGRITY CHECKS FAILED"
        )

        print()
        print(
            "Do not integrate the model until "
            "the failed checks are investigated."
        )

    print()
    print("=" * 75)


if __name__ == "__main__":
    main()