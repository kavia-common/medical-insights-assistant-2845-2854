import logging
from datetime import datetime
from typing import Dict, List, Optional
import uuid

from ..models.schemas import Patient, PatientCreate, PatientUpdate

log = logging.getLogger("app.repo.patients")


def _normalize_mrn(mrn: str) -> tuple[str, Optional[int]]:
    """
    Normalize MRN for comparison.

    Returns a tuple of:
    - original string
    - integer value if MRN is numeric (leading zeros trimmed), otherwise None

    This allows matching '0001' with '1' while keeping alphanumeric MRNs exact.
    """
    s = (mrn or "").strip()
    if s.isdigit():
        try:
            return s, int(s)
        except Exception:
            return s, None
    return s, None


class PatientsRepository:
    """
    Simple in-memory repository for patients (replaceable with DB later).
    """
    def __init__(self) -> None:
        self._items: Dict[str, Patient] = {}

    def _mrn_conflicts(self, mrn: str) -> bool:
        """
        Check if given MRN would conflict with an existing one using normalization rules.
        Numeric MRNs are compared by integer value (padding-insensitive).
        Non-numeric MRNs are compared by exact string.
        """
        src_raw, src_int = _normalize_mrn(mrn)
        for p in self._items.values():
            if not p.mrn:
                continue
            dst_raw, dst_int = _normalize_mrn(p.mrn)
            if src_int is not None and dst_int is not None:
                if src_int == dst_int:
                    return True
            else:
                if src_raw == dst_raw:
                    return True
        return False

    # PUBLIC_INTERFACE
    def create(self, data: PatientCreate) -> Patient:
        """Create a new patient record."""
        now = datetime.utcnow()
        pid = str(uuid.uuid4())

        # Duplicate MRN guard if provided (padding-insensitive for numeric MRNs)
        payload = data.model_dump(exclude_none=True)
        mrn = payload.get("mrn")
        if mrn:
            if self._mrn_conflicts(mrn):
                raise ValueError(f"MRN '{mrn}' already exists")

        # Construct Patient safely from payload
        item = Patient(
            id=pid,
            created_at=now,
            updated_at=now,
            **payload,
        )
        self._items[pid] = item
        log.info("Created patient id=%s name=%s %s", pid, data.first_name, data.last_name)
        return item

    # PUBLIC_INTERFACE
    def get(self, pid: str) -> Optional[Patient]:
        """Get a patient by id."""
        return self._items.get(pid)

    # PUBLIC_INTERFACE
    def get_by_mrn(self, mrn: str) -> Optional[Patient]:
        """
        Get a patient by MRN with normalization.
        - If MRN is numeric, match by integer value, ignoring leading zeros.
        - If MRN is alphanumeric, match by exact string.
        """
        query_raw, query_int = _normalize_mrn(mrn)
        for p in self._items.values():
            if not p.mrn:
                continue
            raw, as_int = _normalize_mrn(p.mrn)
            if query_int is not None and as_int is not None:
                if query_int == as_int:
                    return p
            else:
                if raw == query_raw:
                    return p
        return None

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

        # If MRN is being changed, enforce uniqueness with normalization logic.
        new_mrn = updates.get("mrn")
        if new_mrn:
            # Temporarily remove current item from consideration to allow setting to same MRN
            # with different padding (e.g., 0001 -> 1) without raising conflict.
            current = item.mrn
            conflict = False
            if current != new_mrn:
                # Check against others
                for pid_other, p in self._items.items():
                    if pid_other == pid:
                        continue
                    if not p.mrn:
                        continue
                    q_raw, q_int = _normalize_mrn(new_mrn)
                    r_raw, r_int = _normalize_mrn(p.mrn)
                    if q_int is not None and r_int is not None:
                        if q_int == r_int:
                            conflict = True
                            break
                    else:
                        if q_raw == r_raw:
                            conflict = True
                            break
            if conflict:
                raise ValueError(f"MRN '{new_mrn}' already exists")

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
