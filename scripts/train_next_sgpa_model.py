"""
Train Next Semester SGPA Prediction Models

Dataset:
data/ml/next_semester_gpa_dataset_clean.csv

Target:
Next_SGPA

Features:
- Previous_SGPA
- Current_SGPA
- Repeated_Courses
- Current_Year
- Current_Semester

Important:
- Student_ID is used ONLY for student-level train/test splitting.
- Student_ID is NOT used as an ML feature.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

SEED = 42

np.random.seed(SEED)
tf.random.set_seed(SEED)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "ml"
    / "next_semester_gpa_dataset_clean.csv"
)

MODEL_DIR = PROJECT_ROOT / "models"
RESULT_DIR = PROJECT_ROOT / "data" / "ml"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

FEATURES = [
    "Previous_SGPA",
    "Current_SGPA",
    "Repeated_Courses",
    "Current_Year",
    "Current_Semester",
]

TARGET = "Next_SGPA"

GROUP_COLUMN = "Student_ID"

def calculate_metrics(y_true, y_pred):
    """
    Calculate regression metrics.
    """

    mae = mean_absolute_error(y_true, y_pred)

    rmse = np.sqrt(
        mean_squared_error(y_true, y_pred)
    )

    r2 = r2_score(y_true, y_pred)

    return mae, rmse, r2


def print_metrics(model_name, y_true, y_pred):
    """
    Print model evaluation metrics.
    """

    mae, rmse, r2 = calculate_metrics(
        y_true,
        y_pred
    )

    print()
    print("=" * 60)
    print(model_name)
    print("=" * 60)

    print(f"MAE  : {mae:.4f}")
    print(f"RMSE : {rmse:.4f}")
    print(f"R²   : {r2:.4f}")

    return mae, rmse, r2


# LOAD DATASET
print("=" * 70)
print("NEXT SEMESTER SGPA MODEL TRAINING")
print("=" * 70)

print()
print("Dataset:")
print(DATASET_PATH)

if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found:\n{DATASET_PATH}"
    )


df = pd.read_csv(DATASET_PATH)

print()
print(f"Dataset rows    : {len(df)}")
print(f"Dataset columns : {len(df.columns)}")
print(f"Unique students : {df[GROUP_COLUMN].nunique()}")

required_columns = FEATURES + [
    TARGET,
    GROUP_COLUMN
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

print()
print("Required columns: PASS")

print()
print("=" * 70)
print("DATA VALIDATION")
print("=" * 70)

print()
print("Missing values:")

missing = df[required_columns].isnull().sum()

print(missing.to_string())

if missing.sum() > 0:
    raise ValueError(
        "Dataset contains missing values."
    )

print()
print("Missing values: PASS")

# Check GPA range
for column in [
    "Previous_SGPA",
    "Current_SGPA",
    "Next_SGPA"
]:

    invalid = (
        (df[column] < 0)
        | (df[column] > 4)
    ).sum()

    if invalid > 0:
        raise ValueError(
            f"{column} contains {invalid} invalid GPA values."
        )

print("GPA ranges: PASS")

# Check target zero
zero_target = (
    df[TARGET] == 0
).sum()

if zero_target > 0:
    raise ValueError(
        f"Dataset contains {zero_target} zero Next_SGPA values."
    )

print("Next_SGPA zero check: PASS")

print()
print("=" * 70)
print("MODEL FEATURES")
print("=" * 70)

for feature in FEATURES:
    print(f"- {feature}")

print()
print(f"Target: {TARGET}")


# STUDENT-LEVEL TRAIN / TEST SPLIT
print()
print("=" * 70)
print("STUDENT-LEVEL TRAIN / TEST SPLIT")
print("=" * 70)

X = df[FEATURES].copy()

y = df[TARGET].copy()

groups = df[GROUP_COLUMN].copy()


splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=SEED
)


train_indices, test_indices = next(
    splitter.split(
        X,
        y,
        groups=groups
    )
)

X_train = X.iloc[train_indices].copy()
X_test = X.iloc[test_indices].copy()
y_train = y.iloc[train_indices].copy()
y_test = y.iloc[test_indices].copy()

train_students = set(
    groups.iloc[train_indices]
)

test_students = set(
    groups.iloc[test_indices]
)

print()
print(f"Training records : {len(X_train)}")
print(f"Testing records  : {len(X_test)}")

print()
print(f"Training students: {len(train_students)}")
print(f"Testing students : {len(test_students)}")

overlap = train_students.intersection(
    test_students
)

print()
print(f"Student overlap  : {len(overlap)}")

if len(overlap) != 0:
    raise RuntimeError(
        "ERROR: Students exist in both training and testing sets."
    )

print()
print("Student-level split: PASS")

print()
print("=" * 70)
print("TARGET DISTRIBUTION")
print("=" * 70)

print()
print("Training Next_SGPA:")
print(y_train.describe())

print()
print("Testing Next_SGPA:")
print(y_test.describe())

# RANDOM FOREST BASELINE
print()
print("=" * 70)
print("RANDOM FOREST BASELINE")
print("=" * 70)

rf_model = RandomForestRegressor(
    n_estimators=300,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=SEED,
    n_jobs=-1
)

print()
print("Training Random Forest...")

rf_model.fit(
    X_train,
    y_train
)

rf_predictions = rf_model.predict(
    X_test
)

rf_mae, rf_rmse, rf_r2 = print_metrics(
    "RANDOM FOREST RESULTS",
    y_test,
    rf_predictions
)

# FEATURE SCALING FOR NEURAL NETWORK
print()
print("=" * 70)
print("FEATURE SCALING")
print("=" * 70)

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(
    X_train
)

X_test_scaled = scaler.transform(
    X_test
)

print()
print("StandardScaler fitted using training data only.")

print("Feature scaling: PASS")

# NEURAL NETWORK
print()
print("=" * 70)
print("NEURAL NETWORK")
print("=" * 70)

print()
print("Building Neural Network...")

model = keras.Sequential(
    [
        layers.Input(
            shape=(len(FEATURES),)
        ),

        layers.Dense(
            64,
            activation="relu"
        ),

        layers.Dropout(
            0.20
        ),

        layers.Dense(
            32,
            activation="relu"
        ),

        layers.Dropout(
            0.10
        ),

        layers.Dense(
            16,
            activation="relu"
        ),

        layers.Dense(
            1,
            activation="linear"
        )
    ]
)

model.compile(
    optimizer=keras.optimizers.Adam(
        learning_rate=0.001
    ),
    loss="mse",
    metrics=[
        keras.metrics.MeanAbsoluteError(
            name="mae"
        )
    ]
)

print()
print("Neural Network architecture:")

model.summary()

# EARLY STOPPING
early_stopping = keras.callbacks.EarlyStopping(
    monitor="val_loss",
    patience=20,
    restore_best_weights=True
)

# TRAIN NEURAL NETWORK
print()
print("Training Neural Network...")

history = model.fit(
    X_train_scaled,
    y_train,
    validation_split=0.20,
    epochs=200,
    batch_size=32,
    callbacks=[
        early_stopping
    ],
    verbose=1
)

# NEURAL NETWORK PREDICTION
nn_predictions = model.predict(
    X_test_scaled,
    verbose=0
).flatten()

# Keep predictions inside valid GPA range.
nn_predictions = np.clip(
    nn_predictions,
    0.0,
    4.0
)

nn_mae, nn_rmse, nn_r2 = print_metrics(
    "NEURAL NETWORK RESULTS",
    y_test,
    nn_predictions
)

# MODEL COMPARISON
print()
print("=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

comparison = pd.DataFrame(
    {
        "Model": [
            "Random Forest",
            "Neural Network"
        ],

        "MAE": [
            rf_mae,
            nn_mae
        ],

        "RMSE": [
            rf_rmse,
            nn_rmse
        ],

        "R2": [
            rf_r2,
            nn_r2
        ]
    }
)


print()
print(
    comparison.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)

# DETERMINE BEST MODEL
if nn_rmse < rf_rmse:

    best_model = "Neural Network"

else:

    best_model = "Random Forest"


print()
print(f"Best model based on RMSE: {best_model}")

# SAVE TEST PREDICTIONS
print()
print("=" * 70)
print("SAVING TEST PREDICTIONS")
print("=" * 70)

predictions_df = df.iloc[
    test_indices
].copy()

predictions_df[
    "Predicted_Next_SGPA_RF"
] = rf_predictions

predictions_df[
    "Predicted_Next_SGPA_NN"
] = nn_predictions

predictions_df[
    "NN_Error"
] = (
    predictions_df["Next_SGPA"]
    - predictions_df["Predicted_Next_SGPA_NN"]
)

predictions_df[
    "RF_Error"
] = (
    predictions_df["Next_SGPA"]
    - predictions_df["Predicted_Next_SGPA_RF"]
)

predictions_path = (
    RESULT_DIR
    / "next_sgpa_test_predictions.csv"
)

predictions_df.to_csv(
    predictions_path,
    index=False
)

print()
print(
    f"Saved predictions to:\n{predictions_path}"
)

# SAVE NEURAL NETWORK
nn_model_path = (
    MODEL_DIR
    / "next_sgpa_neural_network.keras"
)

model.save(
    nn_model_path
)

print()
print(
    f"Saved Neural Network to:\n{nn_model_path}"
)

# SAVE SCALER
import joblib

scaler_path = (
    MODEL_DIR
    / "next_sgpa_scaler.pkl"
)

joblib.dump(
    scaler,
    scaler_path
)

print()
print(
    f"Saved scaler to:\n{scaler_path}"
)

# SAVE RANDOM FOREST
rf_model_path = (
    MODEL_DIR
    / "next_sgpa_random_forest.pkl"
)

joblib.dump(
    rf_model,
    rf_model_path
)

print()
print(
    f"Saved Random Forest to:\n{rf_model_path}"
)

# SAVE FEATURE LIST
feature_info_path = (
    MODEL_DIR
    / "next_sgpa_features.txt"
)

with open(
    feature_info_path,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "Next Semester SGPA Prediction Features\n"
    )

    file.write(
        "======================================\n\n"
    )

    for feature in FEATURES:

        file.write(
            f"{feature}\n"
        )

    file.write(
        f"\nTarget:\n{TARGET}\n"
    )


print()
print(
    f"Saved feature information to:\n{feature_info_path}"
)

# SAVE TRAINING HISTORY
history_df = pd.DataFrame(
    history.history
)

history_path = (
    RESULT_DIR
    / "next_sgpa_training_history.csv"
)

history_df.to_csv(
    history_path,
    index=False
)

print()
print(
    f"Saved training history to:\n{history_path}"
)

# SAVE MODEL COMPARISON
comparison_path = (
    RESULT_DIR
    / "next_sgpa_model_comparison.csv"
)


comparison.to_csv(
    comparison_path,
    index=False
)


print()
print(
    f"Saved model comparison to:\n{comparison_path}"
)

# FINAL SUMMARY
print()
print("=" * 70)
print("TRAINING COMPLETE")
print("=" * 70)

print()
print(f"Dataset records       : {len(df)}")
print(f"Unique students       : {df[GROUP_COLUMN].nunique()}")

print()
print(f"Training records      : {len(X_train)}")
print(f"Testing records       : {len(X_test)}")

print()
print(f"Random Forest MAE     : {rf_mae:.4f}")
print(f"Random Forest RMSE    : {rf_rmse:.4f}")
print(f"Random Forest R²      : {rf_r2:.4f}")

print()
print(f"Neural Network MAE    : {nn_mae:.4f}")
print(f"Neural Network RMSE   : {nn_rmse:.4f}")
print(f"Neural Network R²     : {nn_r2:.4f}")

print()
print(f"Best model            : {best_model}")

print()
print("Generated files:")
print(f"- {nn_model_path}")
print(f"- {rf_model_path}")
print(f"- {scaler_path}")
print(f"- {predictions_path}")
print(f"- {history_path}")
print(f"- {comparison_path}")
print(f"- {feature_info_path}")

print()
print("=" * 70)