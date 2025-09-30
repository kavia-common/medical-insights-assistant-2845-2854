from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PatientBase(BaseModel):
    """Base patient fields."""
    first_name: str = Field(..., description="Patient first name")
    last_name: str = Field(..., description="Patient last name")
    age: Optional[int] = Field(None, ge=0, description="Age in years")
    sex: Optional[str] = Field(None, description="Sex/Gender of patient")
    mrn: Optional[str] = Field(None, description="Medical Record Number")


class PatientCreate(PatientBase):
    """Schema for creating a patient."""


class PatientUpdate(BaseModel):
    """Schema for updating patient details."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0)
    sex: Optional[str] = None
    mrn: Optional[str] = None


class Patient(PatientBase):
    """Full patient record."""
    id: str = Field(..., description="Unique patient identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class InterviewCreate(BaseModel):
    """Payload to start a new interview for a patient."""
    patient_id: str = Field(..., description="Associated patient ID")
    chief_complaint: Optional[str] = Field(None, description="Chief complaint")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


class Interview(InterviewCreate):
    """Interview record."""
    id: str = Field(..., description="Interview session ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    transcript: List[Dict[str, Any]] = Field(default_factory=list, description="Q&A transcript entries")


class ChatTurn(BaseModel):
    """Single turn in interview chat."""
    role: str = Field(..., description="agent|patient|advisor")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp UTC")


class AdvisorRequest(BaseModel):
    """Request for advisor recommendations."""
    interview_id: str = Field(..., description="Interview ID to analyze")
    max_items: int = Field(3, ge=1, le=10, description="Max number of suggestions")


class AdvisorSuggestion(BaseModel):
    """Advisor suggestion result."""
    title: str = Field(..., description="Suggestion title")
    rationale: str = Field(..., description="Why this suggestion")
    citations: List[str] = Field(default_factory=list, description="References/citations")
    confidence: float = Field(0.5, ge=0, le=1, description="Confidence score 0..1")


class FileWriteRequest(BaseModel):
    """Request model for writing a file."""
    relative_path: str = Field(..., description="Path under base folder")
    content: str = Field(..., description="Text content to write")


class FileReadResponse(BaseModel):
    """Response model for reading a file."""
    relative_path: str
    content: str


class OperationStatus(BaseModel):
    """Generic status wrapper."""
    status: str = Field(..., description="ok|error")
    detail: Optional[str] = Field(None, description="Additional info")
