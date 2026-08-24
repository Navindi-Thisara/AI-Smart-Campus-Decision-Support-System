"""
Next Semester SGPA Prediction Service

Loads the validated Neural Network and StandardScaler and predicts the next semester SGPA for a student.

Model:
    models/next_sgpa_neural_network.keras

Scaler:
    models/next_sgpa_scaler.pkl

Input features:
    Previous_SGPA
    Current_SGPA
    Repeated_Courses
    Current_Year
    Current_Semester

Target:
    Next_SGPA
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import tensorflow as tf

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "next_sgpa_neural_network.keras"
)

SCALER_PATH = (
    PROJECT_ROOT
    / "models"
    / "next_sgpa_scaler.pkl"
)

FEATURES = [
    "Previous_SGPA",
    "Current_SGPA",
    "Repeated_Courses",
    "Current_Year",
    "Current_Semester",
]

TARGET = "Next_SGPA"

def load_prediction_model():
    """
    Load the trained Neural Network and StandardScaler.
    """

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Neural Network model not found:\n{MODEL_PATH}"
        )

    if not SCALER_PATH.exists():
        raise FileNotFoundError(
            f"Scaler not found:\n{SCALER_PATH}"
        )

    model = tf.keras.models.load_model(
        MODEL_PATH
    )

    scaler = joblib.load(
        SCALER_PATH
    )

    # Verify model input
    if model.input_shape[-1] != len(FEATURES):
        raise ValueError(
            "Model feature count does not match expected features.\n"
            f"Expected: {len(FEATURES)}\n"
            f"Model:    {model.input_shape[-1]}"
        )

    # Verify scaler
    if not hasattr(scaler, "feature_names_in_"):
        raise ValueError(
            "Saved scaler does not contain feature names."
        )

    scaler_features = list(
        scaler.feature_names_in_
    )

    if scaler_features != FEATURES:
        raise ValueError(
            "Scaler feature order does not match expected features.\n"
            f"Expected: {FEATURES}\n"
            f"Scaler:   {scaler_features}"
        )

    if scaler.n_features_in_ != len(FEATURES):
        raise ValueError(
            "Scaler feature count does not match expected features."
        )

    return model, scaler


def validate_input(
    previous_sgpa,
    current_sgpa,
    repeated_courses,
    current_year,
    current_semester,
):
    """
    Validate prediction input values.
    """

    # Convert numeric values safely
    try:
        previous_sgpa = float(previous_sgpa)
        current_sgpa = float(current_sgpa)
        repeated_courses = int(repeated_courses)
        current_year = int(current_year)
        current_semester = int(current_semester)
    except (TypeError, ValueError):
        raise ValueError(
            "All prediction inputs must be numeric."
        )

    # Reject NaN / infinity
    numeric_values = [
        previous_sgpa,
        current_sgpa,
    ]

    if not all(
        np.isfinite(value)
        for value in numeric_values
    ):
        raise ValueError(
            "SGPA values must be finite numbers."
        )

    # SGPA validation
    if not 0.0 <= previous_sgpa <= 4.0:
        raise ValueError(
            "Previous_SGPA must be between 0.0 and 4.0."
        )

    if not 0.0 <= current_sgpa <= 4.0:
        raise ValueError(
            "Current_SGPA must be between 0.0 and 4.0."
        )

    # Repeated courses
    if repeated_courses < 0:
        raise ValueError(
            "Repeated_Courses cannot be negative."
        )

    # Year
    if current_year < 1:
        raise ValueError(
            "Current_Year must be at least 1."
        )

    # Semester
    if not 1 <= current_semester <= 8:
        raise ValueError(
            "Current_Semester must be between 1 and 8."
        )

    return (
        previous_sgpa,
        current_sgpa,
        repeated_courses,
        current_year,
        current_semester,
    )


# PREDICTION
def predict_next_sgpa(
    model,
    scaler,
    previous_sgpa,
    current_sgpa,
    repeated_courses,
    current_year,
    current_semester,
):
    """
    Predict the student's next semester SGPA.
    """

    (
        previous_sgpa,
        current_sgpa,
        repeated_courses,
        current_year,
        current_semester,
    ) = validate_input(
        previous_sgpa,
        current_sgpa,
        repeated_courses,
        current_year,
        current_semester,
    )

    # Create input using EXACT training feature names/order
    input_data = pd.DataFrame(
        [
            {
                "Previous_SGPA": previous_sgpa,
                "Current_SGPA": current_sgpa,
                "Repeated_Courses": repeated_courses,
                "Current_Year": current_year,
                "Current_Semester": current_semester,
            }
        ],
        columns=FEATURES,
    )

    # Scale using scaler fitted ONLY on training data
    scaled_input = scaler.transform(
        input_data[FEATURES]
    )

    # Neural Network prediction
    prediction = model.predict(
        scaled_input,
        verbose=0,
    )

    predicted_sgpa = float(
        prediction[0][0]
    )

    # Validate model output
    if not np.isfinite(predicted_sgpa):
        raise ValueError(
            "Neural Network produced an invalid prediction."
        )

    # GPA must be between 0 and 4
    predicted_sgpa = np.clip(
        predicted_sgpa,
        0.0,
        4.0,
    )

    return round(
        float(predicted_sgpa),
        4,
    )


# PREDICTION FROM DICTIONARY
def predict_from_dict(model, scaler, data):
    """
    Predict Next_SGPA from a dictionary.

    Useful later for REST API integration.

    Example:

        data = {
            "Previous_SGPA": 3.20,
            "Current_SGPA": 3.45,
            "Repeated_Courses": 0,
            "Current_Year": 2,
            "Current_Semester": 4
        }
    """

    missing_features = [
        feature
        for feature in FEATURES
        if feature not in data
    ]

    if missing_features:
        raise ValueError(
            f"Missing required features: {missing_features}"
        )

    return predict_next_sgpa(
        model=model,
        scaler=scaler,
        previous_sgpa=data["Previous_SGPA"],
        current_sgpa=data["Current_SGPA"],
        repeated_courses=data["Repeated_Courses"],
        current_year=data["Current_Year"],
        current_semester=data["Current_Semester"],
    )


# COMMAND-LINE TEST
def main():

    print("=" * 70)
    print("NEXT SEMESTER SGPA PREDICTION")
    print("=" * 70)

    print()
    print(f"Model : {MODEL_PATH}")
    print(f"Scaler: {SCALER_PATH}")

    try:

        print()
        print("Loading model and scaler...")

        model, scaler = load_prediction_model()

        print("Model and scaler loaded successfully.")

        print()
        print("=" * 70)
        print("ENTER STUDENT INFORMATION")
        print("=" * 70)

        previous_sgpa = float(
            input("Previous SGPA: ")
        )

        current_sgpa = float(
            input("Current SGPA: ")
        )

        repeated_courses = int(
            input("Repeated Courses: ")
        )

        current_year = int(
            input("Current Year: ")
        )

        current_semester = int(
            input("Current Semester: ")
        )

        predicted_sgpa = predict_next_sgpa(
            model=model,
            scaler=scaler,
            previous_sgpa=previous_sgpa,
            current_sgpa=current_sgpa,
            repeated_courses=repeated_courses,
            current_year=current_year,
            current_semester=current_semester,
        )

        print()
        print("=" * 70)
        print("PREDICTION RESULT")
        print("=" * 70)

        print()
        print(
            f"Predicted Next Semester SGPA: "
            f"{predicted_sgpa:.4f}"
        )

        print()
        print("Input features:")

        print(
            f"Previous_SGPA     : {previous_sgpa:.4f}"
        )

        print(
            f"Current_SGPA      : {current_sgpa:.4f}"
        )

        print(
            f"Repeated_Courses  : {repeated_courses}"
        )

        print(
            f"Current_Year      : {current_year}"
        )

        print(
            f"Current_Semester  : {current_semester}"
        )

        print()
        print("=" * 70)
        print("PREDICTION COMPLETE")
        print("=" * 70)

    except ValueError as error:

        print()
        print("=" * 70)
        print("INPUT ERROR")
        print("=" * 70)
        print(error)


if __name__ == "__main__":
    main()