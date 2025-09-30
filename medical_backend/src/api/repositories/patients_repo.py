import logging
from datetime import datetime
from typing import Dict, List, Optional
import uuid

from ..models.schemas import Patient, PatientCreate, PatientUpdate

log = logging.getLogger("app.repo.patients")


class PatientsRepository:
    """
    Simple in-memory repository for patients (replaceable with DB later).
    """
    def __init__(self) -> None:
        self._items: Dict[str, Patient] = {}

    # PUBLIC_INTERFACE
    def create(self, data: PatientCreate) -> Patient:
        """Create a new patient record."""
        now = datetime.utcnow()
        pid = str(uuid.uuid4())
        item = Patient(id=pid, created_at=now, updated_at=now, **data.model_fields_set, **data.model_dump())
        self._items[pid] = item
        log.info("Created patient id=%s name=%s %s", pid, data.first_name, data.last_name)
        return item

    # PUBLIC_INTERFACE
    def get(self, pid: str) -> Optional[Patient]:
        """Get a patient by id."""
        return self._items.get(pid)

    # PUBLIC_INTERFACE
    def list(self) -> List[Patient]:
        """List all patients."""
        return list(self._items.values())

    # PUBLIC_INTERFACE
    def update(self, pid: str, changes: PatientUpdate) -> Optional[Patient]:
        """Update an existing patient."""
        item = self._items.get(pid)
        if not item:
            return None
        updates = changes.model_dump(exclude_none=True)
        updated = item.model_copy(update={**updates, "updated_at": datetime.utcnow()})
        self._items[pid] = updated
        log.info("Updated patient id=%s", pid)
        return updated

    # PUBLIC_INTERFACE
    def delete(self, pid: str) -> bool:
        """Delete patient by id."""
        if pid in self._items:
            del self._items[pid]
            log.info("Deleted patient id=%s", pid)
            return True
        return False


# Singleton repo instance for app lifetime (simple)
patients_repo = PatientsRepository()
