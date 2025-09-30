from typing import Dict
from fastapi import APIRouter, HTTPException, Body, Path

from ..models.schemas import OperationStatus
from ..repositories.interview_files_repo import interview_files_repo
from ..services.orchestrator import orchestrator

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post(
    "/{patient_id}",
    response_model=OperationStatus,
    summary="Save interview text",
    description="Save the provided interview text directly to OneDrive as {patient_id}.txt under the Interview folder.",
)
# PUBLIC_INTERFACE
def save_interview_text(
    patient_id: str = Path(..., description="Patient ID used as filename"),
    content: str = Body(..., embed=True, description="Full interview text to store"),
) -> OperationStatus:
    """Save interview text to OneDrive using patient_id as filename."""
    try:
        rel = interview_files_repo.write_text(patient_id, content)
        return OperationStatus(status="ok", detail=f"wrote:{rel}")
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Failed to write interview: {ex}")


@router.get(
    "/{patient_id}",
    summary="Get interview text",
    description="Fetch interview text from OneDrive for the given patient_id.",
)
# PUBLIC_INTERFACE
def get_interview_text(patient_id: str = Path(..., description="Patient ID (filename without extension)")) -> Dict[str, str]:
    """Read interview text from OneDrive using patient_id as filename."""
    try:
        if not interview_files_repo.exists(patient_id):
            raise HTTPException(status_code=404, detail="Interview file not found")
        text = interview_files_repo.read_text(patient_id)
        return {"patient_id": patient_id, "content": text}
    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Failed to read interview: {ex}")


@router.delete(
    "/{patient_id}",
    response_model=OperationStatus,
    summary="Delete interview text",
    description="Delete interview text file in OneDrive for the given patient_id.",
)
# PUBLIC_INTERFACE
def delete_interview_text(patient_id: str = Path(..., description="Patient ID (filename without extension)")) -> OperationStatus:
    """Delete interview text file for a patient."""
    try:
        ok = interview_files_repo.delete(patient_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Interview file not found")
        return OperationStatus(status="ok", detail="deleted")
    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Failed to delete interview: {ex}")


@router.post(
    "/{patient_id}/run-advisor",
    summary="Run advisor on interview text",
    description="Run Medical Advisor Agent using interview text loaded from OneDrive for the given patient_id.",
)
# PUBLIC_INTERFACE
async def run_advisor_on_file(
    patient_id: str = Path(..., description="Patient ID (filename without extension)"),
    max_items: int = 3,
) -> Dict[str, object]:
    """
    Run advisor agent directly on the interview text file.
    This reuses the advisor service and bypasses the old in-memory transcript.
    """
    if not interview_files_repo.exists(patient_id):
        raise HTTPException(status_code=404, detail="Interview file not found")

    try:
        text = interview_files_repo.read_text(patient_id)
        return await orchestrator.run_advisor_on_text(patient_id, text, max_items=max_items)
    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Advisor failed: {ex}")
