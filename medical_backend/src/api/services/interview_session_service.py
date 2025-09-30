import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..services.agents import patient_interview_agent
from ..repositories.interview_files_repo import interview_files_repo

log = logging.getLogger("app.interview.session")


class InterviewSession:
    """
    Represents a single agent-driven interview session for a patient.

    Maintains an in-memory transcript of alternating turns:
    - role: 'agent' or 'patient'
    - content: text
    - timestamp: ISO string
    """
    def __init__(self, patient_id: str, chief_complaint: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        self.patient_id = patient_id
        self.chief_complaint = (chief_complaint or "").strip()
        self.context = context or {}
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at
        self.completed = False
        self.transcript: List[Dict[str, Any]] = []

    def append_turn(self, role: str, content: str) -> None:
        """Append a turn and update timestamp."""
        self.transcript.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        )
        self.updated_at = datetime.utcnow()

    def to_text(self) -> str:
        """Return a readable transcript suitable for saving to a .txt file."""
        lines: List[str] = []
        header = [
            "Patient Interview Transcript",
            f"Patient ID: {self.patient_id}",
            f"Chief Complaint: {self.chief_complaint}",
            f"Created: {self.created_at.isoformat()}Z",
            f"Updated: {self.updated_at.isoformat()}Z",
            "-" * 60,
        ]
        lines.extend(header)
        for t in self.transcript:
            role = t.get("role", "agent").upper()
            ts = t.get("timestamp", "")
            content = t.get("content", "")
            lines.append(f"[{ts}] {role}: {content}")
        return "\n".join(lines)


class InterviewSessionService:
    """
    Manages agent-driven interview sessions in-memory.

    Lifecycle:
    - start_session(patient_id, chief_complaint?, context?) -> creates session if not present and returns first question(s)
    - submit_answer(patient_id, answer) -> appends patient answer and returns next question(s)
    - end_session(patient_id) -> marks complete, writes transcript to OneDrive/Interview/{patient_id}.txt, clears session
    """
    def __init__(self):
        # In-memory sessions keyed by patient_id
        self._sessions: Dict[str, InterviewSession] = {}

    # PUBLIC_INTERFACE
    async def start_session(self, patient_id: str, chief_complaint: Optional[str], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Start an interview session for the patient, returning initial agent question(s)."""
        if patient_id in self._sessions and not self._sessions[patient_id].completed:
            # If session exists and still running, return a warning but continue by generating next questions
            log.info("Session already active for patient_id=%s; generating next questions", patient_id)
            session = self._sessions[patient_id]
        else:
            session = InterviewSession(patient_id=patient_id, chief_complaint=chief_complaint, context=context)
            self._sessions[patient_id] = session
            log.info("Started new interview session for patient_id=%s", patient_id)

        # Generate first/next questions based on current transcript
        questions = await patient_interview_agent.next_questions(session.chief_complaint, session.transcript)
        # Record agent questions as a single agent turn (can also split into multiple turns)
        for q in questions:
            session.append_turn("agent", q)

        return {
            "patient_id": patient_id,
            "completed": session.completed,
            "questions": questions,
            "transcript": session.transcript,
        }

    # PUBLIC_INTERFACE
    async def submit_answer(self, patient_id: str, answer: str) -> Dict[str, Any]:
        """Submit a patient's answer and return the next agent question(s)."""
        session = self._sessions.get(patient_id)
        if not session or session.completed:
            raise ValueError("No active session for this patient.")

        # Append patient turn
        session.append_turn("patient", answer or "")

        # Generate follow-up question(s)
        questions = await patient_interview_agent.next_questions(session.chief_complaint, session.transcript)
        if not questions:
            # If no more questions, advise session to be ended by caller
            log.info("No additional questions generated for patient_id=%s", patient_id)
        else:
            for q in questions:
                session.append_turn("agent", q)

        return {
            "patient_id": patient_id,
            "completed": session.completed,
            "questions": questions,
            "transcript": session.transcript,
        }

    # PUBLIC_INTERFACE
    async def end_session(self, patient_id: str) -> Dict[str, Any]:
        """End the session, write transcript to OneDrive as {patient_id}.txt, and return status."""
        session = self._sessions.get(patient_id)
        if not session:
            raise ValueError("No session found for this patient.")

        if session.completed:
            log.info("Session already completed for patient_id=%s", patient_id)

        session.completed = True
        # Render to text and write to OneDrive Interview/{patient_id}.txt
        text = session.to_text()
        rel_path = interview_files_repo.write_text(patient_id, text)
        log.info("Wrote interview transcript to OneDrive: %s", rel_path)

        # Optionally, clear from memory after completion to avoid leaks
        del self._sessions[patient_id]

        return {"status": "ok", "detail": f"transcript_written:{rel_path}", "patient_id": patient_id}


interview_session_service = InterviewSessionService()
