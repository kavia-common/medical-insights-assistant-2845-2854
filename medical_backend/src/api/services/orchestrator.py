import logging
from typing import Dict, Any

from ..repositories.interviews_repo import interviews_repo
from .agents import patient_interview_agent, medical_advisor_agent

log = logging.getLogger("app.orchestrator")


class MedicalOrchestrator:
    """
    Orchestrates the agent workflow:
    1) Interview: generates questions and appends to transcript.
    2) Advisor: analyzes transcript using RAG and provides suggestions.
    """

    # PUBLIC_INTERFACE
    async def run_interview_step(self, interview_id: str) -> Dict[str, Any]:
        """Generate next interview questions and store as 'agent' turns."""
        interview = interviews_repo.get(interview_id)
        if not interview:
            raise ValueError("Interview not found")
        cc = interview.chief_complaint or ""
        questions = await patient_interview_agent.next_questions(cc, interview.transcript)
        for q in questions:
            interviews_repo.add_turn(interview_id, role="agent", content=q)
        log.info("Interview step completed. interview_id=%s added=%d", interview_id, len(questions))
        return {"interview_id": interview_id, "questions": questions}

    # PUBLIC_INTERFACE
    async def run_advisor(self, interview_id: str, max_items: int = 3) -> Dict[str, Any]:
        """Aggregate transcript text and request advisor suggestions via RAG."""
        interview = interviews_repo.get(interview_id)
        if not interview:
            raise ValueError("Interview not found")
        transcript_text = "\n".join([f"{t['role']}: {t['content']}" for t in interview.transcript])
        suggestions = await medical_advisor_agent.advise(transcript_text, max_items=max_items)
        # Record advisor summary into transcript
        for s in suggestions:
            content = f"{s['title']} - {s['rationale']} (confidence: {s['confidence']:.2f})"
            interviews_repo.add_turn(interview_id, role="advisor", content=content)
        log.info("Advisor step completed. interview_id=%s items=%d", interview_id, len(suggestions))
        return {"interview_id": interview_id, "suggestions": suggestions}


orchestrator = MedicalOrchestrator()
