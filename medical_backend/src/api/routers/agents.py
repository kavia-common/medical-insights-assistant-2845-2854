from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query
from ..services.orchestrator import orchestrator
from ..repositories.interview_files_repo import interview_files_repo

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post(
    "/advisor/run",
    summary="Advisor run (by patient_id)",
    description="Trigger Medical Advisor Agent using interview text stored at OneDrive/Interview/{patient_id}.txt.",
)
# PUBLIC_INTERFACE
async def agent_advisor_run(
    patient_id: str = Query(..., description="Patient ID (file name without extension)"),
    max_items: int = Query(3, ge=1, le=10),
) -> Dict[str, Any]:
    """Run advisor on file-based interview text."""
    if not interview_files_repo.exists(patient_id):
        raise HTTPException(status_code=404, detail="Interview file not found")
    try:
        text = interview_files_repo.read_text(patient_id)
        return await orchestrator.run_advisor_on_text(patient_id, text, max_items=max_items)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Advisor failed: {ex}")


@router.post(
    "/crew/run",
    summary="Run crew workflow (file-based)",
    description="Placeholder for a multi-step workflow driven by file-based interview text. Currently runs advisor only.",
)
# PUBLIC_INTERFACE
async def crew_run(
    patient_id: str = Query(..., description="Patient ID (file name without extension)"),
    max_items: int = Query(3, ge=1, le=10),
) -> Dict[str, Any]:
    """Run a simple crew workflow using file-based interview text (advisor only at present)."""
    if not interview_files_repo.exists(patient_id):
        raise HTTPException(status_code=404, detail="Interview file not found")
    text = interview_files_repo.read_text(patient_id)
    return await orchestrator.run_advisor_on_text(patient_id, text, max_items=max_items)
