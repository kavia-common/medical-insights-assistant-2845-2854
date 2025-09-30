from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Path, Body

from ..services.interview_session_service import interview_session_service

router = APIRouter(prefix="/interview-session", tags=["interviews"])


class StartSessionRequest(BaseModel):
    """Request body for starting an interview session."""
    chief_complaint: Optional[str] = Field(None, description="Chief complaint to seed interview.")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context for the agent.")


class AnswerRequest(BaseModel):
    """Request body for submitting an answer."""
    answer: str = Field(..., description="Patient's natural language response.")


@router.post(
    "/{patient_id}/start",
    summary="Start patient interview session",
    description="Begin an agent-driven interview session. Returns initial questions by the agent.",
)
# PUBLIC_INTERFACE
async def start_session(
    patient_id: str = Path(..., description="Target patient id"),
    payload: StartSessionRequest = Body(default_factory=StartSessionRequest),
) -> Dict[str, Any]:
    """Start an interview session and receive initial questions."""
    try:
        res = await interview_session_service.start_session(
            patient_id=patient_id,
            chief_complaint=payload.chief_complaint,
            context=payload.context,
        )
        return res
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Failed to start session: {ex}")


@router.post(
    "/{patient_id}/answer",
    summary="Submit answer and get next question(s)",
    description="Submit the patient's answer to the last question and receive the agent's next question(s).",
)
# PUBLIC_INTERFACE
async def submit_answer(
    patient_id: str = Path(..., description="Target patient id"),
    payload: AnswerRequest = Body(...),
) -> Dict[str, Any]:
    """Submit an answer and get adaptive follow-up question(s)."""
    try:
        res = await interview_session_service.submit_answer(patient_id, payload.answer)
        return res
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Failed to process answer: {ex}")


@router.post(
    "/{patient_id}/end",
    summary="End interview and save transcript",
    description="End the interview session and write the full transcript to OneDrive as Interview/{patient_id}.txt.",
)
# PUBLIC_INTERFACE
async def end_session(
    patient_id: str = Path(..., description="Target patient id"),
) -> Dict[str, Any]:
    """End the session and persist transcript to OneDrive."""
    try:
        res = await interview_session_service.end_session(patient_id)
        return res
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Failed to end session: {ex}")
