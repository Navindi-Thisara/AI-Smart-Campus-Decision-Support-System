"""
Predict Next Semester SGPA

Loads the trained Neural Network and scaler and predicts the next semester SGPA for a student.

Model:
    models/next_sgpa_neural_network.keras

Scaler:
    models/next_sgpa_scaler.pkl
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import tensorflow as tf

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = PROJECT_ROOT / "models" / "next_sgpa_neural_network.keras"
SCALER_PATH = PROJECT_ROOT / "models" / "next_sgpa_scaler.pkl"

FEATURES = [
    "Previous_SGPA",
    "Current_SGPA",
    "Repeated_Courses",
    "Current_Year",
    "Current_Semester",
]

# LOAD MODEL
def load_prediction_model():
    """Load trained Neural Network and scaler."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Neural Network model not found:\n{MODEL_PATH}"
        )

    if not SCALER_PATH.exists():
        raise FileNotFoundError(
            f"Scaler not found:\n{SCALER_PATH}"
        )

    print("Loading Neural Network...")
    model = tf.keras.models.load_model(MODEL_PATH)

    print("Loading feature scaler...")
    scaler = joblib.load(SCALER_PATH)

    return model, scaler


def validate_input(
    previous_sgpa,
    current_sgpa,
    repeated_courses,
    current_year,
    current_semester,
):
    """Validate prediction input values."""

    if not 0.0 <= previous_sgpa <= 4.0:
        raise ValueError(
            "Previous_SGPA must be between 0.0 and 4.0."
        )

    if not 0.0 <= current_sgpa <= 4.0:
        raise ValueError(
            "Current_SGPA must be between 0.0 and 4.0."
        )

    if repeated_courses < 0:
        raise ValueError(
            "Repeated_Courses cannot be negative."
        )

    if current_year < 1:
        raise ValueError(
            "Current_Year must be at least 1."
        )

    if current_semester < 1:
        raise ValueError(
            "Current_Semester must be at least 1."
        )

    if current_semester > 8:
        raise ValueError(
            "Current_Semester must be between 1 and 8."
        )


def predict_next_sgpa(
    model,
    scaler,
    previous_sgpa,
    current_sgpa,
    repeated_courses,
    current_year,
    current_semester,
):
    """Predict next semester SGPA."""

    validate_input(
        previous_sgpa,
        current_sgpa,
        repeated_courses,
        current_year,
        current_semester,
    )

    # Create input dataframe in exactly the same
    # feature order used during training
    input_data = pd.DataFrame(
        [
            {
                "Previous_SGPA": previous_sgpa,
                "Current_SGPA": current_sgpa,
                "Repeated_Courses": repeated_courses,
                "Current_Year": current_year,
                "Current_Semester": current_semester,
            }
        ]
    )

    # Scale using the scaler fitted during training.
    scaled_input = scaler.transform(input_data[FEATURES])

    # Neural Network prediction
    prediction = model.predict(
        scaled_input,
        verbose=0,
    )

    predicted_sgpa = float(prediction[0][0])

    # Keep prediction within valid GPA range
    predicted_sgpa = max(0.0, min(4.0, predicted_sgpa))

    return round(predicted_sgpa, 4)


# COMMAND-LINE TEST
def main():

    print("=" * 70)
    print("NEXT SEMESTER SGPA PREDICTION")
    print("=" * 70)

    print()
    print("Project root:")
    print(PROJECT_ROOT)

    print()
    print("Model:")
    print(MODEL_PATH)

    print()
    print("Scaler:")
    print(SCALER_PATH)

    print()
    model, scaler = load_prediction_model()

    print()
    print("=" * 70)
    print("ENTER STUDENT INFORMATION")
    print("=" * 70)

    try:

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

        print(
            f"Predicted Next Semester SGPA: {predicted_sgpa:.4f}"
        )

        print()
        print("=" * 70)
        print("PREDICTION COMPLETE")
        print("=" * 70)

    except ValueError as e:

        print()
        print("ERROR:")
        print(e)


if __name__ == "__main__":
    main()