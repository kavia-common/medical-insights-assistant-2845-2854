from typing import List
from fastapi import APIRouter, HTTPException

from ..models.schemas import Patient, PatientCreate, PatientUpdate, OperationStatus
from ..repositories.patients_repo import patients_repo

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post(
    "",
    response_model=Patient,
    summary="Create patient",
    description="Create a new patient record.",
    status_code=201,
)
# PUBLIC_INTERFACE
def create_patient(payload: PatientCreate) -> Patient:
    """Create a patient."""
    try:
        return patients_repo.create(payload)
    except ValueError as ve:
        # Detect MRN duplicate message and return 409 Conflict; otherwise 400 Bad Request
        detail = str(ve)
        if "already exists" in detail and "MRN" in detail:
            raise HTTPException(status_code=409, detail=detail)
        raise HTTPException(status_code=400, detail=detail)


@router.get("", response_model=List[Patient], summary="List patients", description="List all patients.")
# PUBLIC_INTERFACE
def list_patients() -> List[Patient]:
    """List patients."""
    return patients_repo.list()


@router.get("/{patient_id}", response_model=Patient, summary="Get patient", description="Retrieve a patient by ID.")
# PUBLIC_INTERFACE
def get_patient(patient_id: str) -> Patient:
    """Get patient by ID."""
    res = patients_repo.get(patient_id)
    if not res:
        raise HTTPException(status_code=404, detail="Patient not found")
    return res


@router.patch("/{patient_id}", response_model=Patient, summary="Update patient", description="Update patient details.")
# PUBLIC_INTERFACE
def update_patient(patient_id: str, payload: PatientUpdate) -> Patient:
    """Update a patient."""
    res = patients_repo.update(patient_id, payload)
    if not res:
        raise HTTPException(status_code=404, detail="Patient not found")
    return res


@router.delete("/{patient_id}", response_model=OperationStatus, summary="Delete patient", description="Delete a patient.")
# PUBLIC_INTERFACE
def delete_patient(patient_id: str) -> OperationStatus:
    """Delete a patient."""
    ok = patients_repo.delete(patient_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Patient not found")
    return OperationStatus(status="ok", detail="deleted")
