from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Body, Query

from ..models.schemas import Interview, InterviewCreate, OperationStatus
from ..repositories.interviews_repo import interviews_repo
from ..services.orchestrator import orchestrator

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("", response_model=Interview, summary="Create interview", description="Start a new interview session.")
# PUBLIC_INTERFACE
def create_interview(payload: InterviewCreate) -> Interview:
    """Create an interview session for a patient."""
    return interviews_repo.create(payload)


@router.get("", response_model=List[Interview], summary="List interviews", description="List interviews by optional patient.")
# PUBLIC_INTERFACE
def list_interviews(patient_id: str | None = None) -> List[Interview]:
    """List interviews, optionally filtered by patient_id."""
    return interviews_repo.list(patient_id=patient_id)


@router.get("/{interview_id}", response_model=Interview, summary="Get interview", description="Get interview by ID.")
# PUBLIC_INTERFACE
def get_interview(interview_id: str) -> Interview:
    """Get interview."""
    res = interviews_repo.get(interview_id)
    if not res:
        raise HTTPException(status_code=404, detail="Interview not found")
    return res


@router.post("/{interview_id}/turns", response_model=Interview, summary="Add patient turn", description="Append a patient reply to transcript.")
# PUBLIC_INTERFACE
def add_patient_turn(interview_id: str, content: str = Body(..., embed=True)) -> Interview:
    """Append a patient message to transcript."""
    res = interviews_repo.add_turn(interview_id, role="patient", content=content)
    if not res:
        raise HTTPException(status_code=404, detail="Interview not found")
    return res


@router.post("/{interview_id}/run-interview", summary="Run interview step", description="Generate next questions via Interview Agent.")
# PUBLIC_INTERFACE
async def run_interview_step(interview_id: str) -> Dict[str, Any]:
    """Run interview agent step to generate next questions."""
    try:
        return await orchestrator.run_interview_step(interview_id)
    except ValueError as ex:
        raise HTTPException(status_code=404, detail=str(ex))


@router.post("/{interview_id}/run-advisor", summary="Run advisor", description="Generate advisor suggestions using RAG.")
# PUBLIC_INTERFACE
async def run_advisor(interview_id: str, max_items: int = Query(3, ge=1, le=10)) -> Dict[str, Any]:
    """Run advisor agent on transcript."""
    try:
        return await orchestrator.run_advisor(interview_id, max_items=max_items)
    except ValueError as ex:
        raise HTTPException(status_code=404, detail=str(ex))


@router.delete("/{interview_id}", response_model=OperationStatus, summary="Delete interview", description="Remove interview by ID.")
# PUBLIC_INTERFACE
def delete_interview(interview_id: str) -> OperationStatus:
    """Delete an interview."""
    ok = interviews_repo.delete(interview_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Interview not found")
    return OperationStatus(status="ok", detail="deleted")
