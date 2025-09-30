import logging
from typing import Dict, Any

from .agents import medical_advisor_agent

log = logging.getLogger("app.orchestrator")


class MedicalOrchestrator:
    """
    Orchestrates the agent workflow.

    Legacy methods using in-memory interviews are retained for compatibility,
    but the new file-based flow should prefer run_advisor_on_text().
    """

    # PUBLIC_INTERFACE
    async def run_interview_step(self, interview_id: str) -> Dict[str, Any]:
        """
        Deprecated: In-memory interview question generation.
        Kept for backward compatibility if any callers still use it.
        """
        raise ValueError("Interview flow is now file-based; run_interview_step is deprecated.")

    # PUBLIC_INTERFACE
    async def run_advisor(self, interview_id: str, max_items: int = 3) -> Dict[str, Any]:
        """
        Deprecated: In-memory transcript advisor.
        Kept for backward compatibility if any callers still use it.
        """
        raise ValueError("Interview flow is now file-based; run_advisor is deprecated.")

    # PUBLIC_INTERFACE
    async def run_advisor_on_text(self, patient_id: str, interview_text: str, max_items: int = 3) -> Dict[str, Any]:
        """Analyze the given interview text using RAG and return suggestions."""
        suggestions = await medical_advisor_agent.advise(interview_text, max_items=max_items)
        log.info("Advisor step completed. patient_id=%s items=%d", patient_id, len(suggestions))
        return {"patient_id": patient_id, "suggestions": suggestions}


orchestrator = MedicalOrchestrator()
