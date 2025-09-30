import logging
from datetime import datetime
from typing import Dict, List, Optional
import uuid

from ..models.schemas import Interview, InterviewCreate, ChatTurn

log = logging.getLogger("app.repo.interviews")


class InterviewsRepository:
    """
    In-memory repository for interview sessions and transcripts.
    """
    def __init__(self) -> None:
        self._items: Dict[str, Interview] = {}

    # PUBLIC_INTERFACE
    def create(self, data: InterviewCreate) -> Interview:
        """Create a new interview session."""
        now = datetime.utcnow()
        iid = str(uuid.uuid4())
        interview = Interview(
            id=iid,
            patient_id=data.patient_id,
            chief_complaint=data.chief_complaint,
            context=data.context or {},
            created_at=now,
            updated_at=now,
            transcript=[],
        )
        self._items[iid] = interview
        log.info("Created interview id=%s patient_id=%s", iid, data.patient_id)
        return interview

    # PUBLIC_INTERFACE
    def get(self, iid: str) -> Optional[Interview]:
        """Get interview by id."""
        return self._items.get(iid)

    # PUBLIC_INTERFACE
    def list(self, patient_id: Optional[str] = None) -> List[Interview]:
        """List interviews optionally filtered by patient."""
        values = list(self._items.values())
        if patient_id:
            return [x for x in values if x.patient_id == patient_id]
        return values

    # PUBLIC_INTERFACE
    def add_turn(self, iid: str, role: str, content: str) -> Optional[Interview]:
        """Append a turn to interview transcript."""
        interview = self._items.get(iid)
        if not interview:
            return None
        turn = ChatTurn(role=role, content=content)
        interview.transcript.append(turn.model_dump())
        interview.updated_at = datetime.utcnow()
        log.info("Interview id=%s appended role=%s", iid, role)
        return interview

    # PUBLIC_INTERFACE
    def delete(self, iid: str) -> bool:
        """Delete interview by id."""
        if iid in self._items:
            del self._items[iid]
            log.info("Deleted interview id=%s", iid)
            return True
        return False


interviews_repo = InterviewsRepository()
