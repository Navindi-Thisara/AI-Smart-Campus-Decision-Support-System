"""
FastAPI service for Next Semester SGPA prediction.
"""

from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SCRIPTS_DIR = PROJECT_ROOT / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


# IMPORT MODEL PREDICTION FUNCTIONS
from predict_next_sgpa import (  # noqa: E402
    load_prediction_model,
    predict_next_sgpa,
    FEATURES,
)

# FASTAPI APPLICATION
app = FastAPI(
    title="Smart Campus Next Semester SGPA Prediction API",
    description=(
        "API for predicting a student's next semester SGPA "
        "using the validated Neural Network model."
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

    MODEL, SCALER = load_prediction_model()

except Exception as error:

    MODEL = None
    SCALER = None
    MODEL_LOAD_ERROR = str(error)

else:

    MODEL_LOAD_ERROR = None


# REQUEST MODEL
class SGPARequest(BaseModel):

    Previous_SGPA: float = Field(
        ...,
        ge=0.0,
        le=4.0,
        description="Previous semester SGPA",
    )

    Current_SGPA: float = Field(
        ...,
        ge=0.0,
        le=4.0,
        description="Current semester SGPA",
    )

    Repeated_Courses: int = Field(
        ...,
        ge=0,
        description="Number of repeated courses",
    )

    Current_Year: int = Field(
        ...,
        ge=1,
        description="Current academic year",
    )

    Current_Semester: int = Field(
        ...,
        ge=1,
        le=8,
        description="Current semester",
    )


# RESPONSE MODEL
class SGPAResponse(BaseModel):

    Predicted_Next_SGPA: float


# ROOT ENDPOINT

@app.get("/")
def root():

    return {
        "service": "Smart Campus Next Semester SGPA Prediction API",
        "status": "running",
        "model_loaded": MODEL is not None,
        "features": FEATURES,
    }


# HEALTH CHECK
@app.get("/health")
def health():

    if MODEL is None or SCALER is None:

        return {
            "status": "unhealthy",
            "model_loaded": False,
            "error": MODEL_LOAD_ERROR,
        }

    return {
        "status": "healthy",
        "model_loaded": True,
        "scaler_loaded": True,
        "features": FEATURES,
    }


# PREDICT NEXT SGPA
@app.post(
    "/predict-next-sgpa",
    response_model=SGPAResponse,
)
def predict(request: SGPARequest):

    if MODEL is None or SCALER is None:

        raise HTTPException(
            status_code=503,
            detail=(
                "Prediction model is not available. "
                f"Error: {MODEL_LOAD_ERROR}"
            ),
        )

    try:

        predicted_sgpa = predict_next_sgpa(
            model=MODEL,
            scaler=SCALER,
            previous_sgpa=request.Previous_SGPA,
            current_sgpa=request.Current_SGPA,
            repeated_courses=request.Repeated_Courses,
            current_year=request.Current_Year,
            current_semester=request.Current_Semester,
        )

        return SGPAResponse(
            Predicted_Next_SGPA=predicted_sgpa
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {error}",
        )