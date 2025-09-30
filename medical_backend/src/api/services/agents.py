import logging
from typing import List, Dict, Any

from .vector_client import vector_client

log = logging.getLogger("app.agents")


class PatientInterviewAgent:
    """
    Patient Interview Agent:
    - Generates structured questions based on chief complaint and prior transcript.
    - This is a minimal rule-based scaffold; can be replaced by CrewAI integration.
    """

    # PUBLIC_INTERFACE
    async def next_questions(self, chief_complaint: str, transcript: List[Dict[str, Any]]) -> List[str]:
        """Generate next set of patient questions."""
        log.info("InterviewAgent generating questions. CC='%s' turns=%d", chief_complaint, len(transcript))
        asked = " ".join([t.get("content", "").lower() for t in transcript if t.get("role") == "agent"])
        questions: List[str] = []
        if "duration" not in asked:
            questions.append("How long have you been experiencing this issue?")
        if "severity" not in asked:
            questions.append("How severe are your symptoms on a scale from 1 to 10?")
        if "triggers" not in asked:
            questions.append("Have you noticed any triggers or patterns that make it better or worse?")
        if chief_complaint:
            questions.append(f"Can you describe more details about: {chief_complaint}?")
        if not questions:
            questions.append("Do you have any other symptoms or concerns you'd like to share?")
        return questions


class MedicalAdvisorAgent:
    """
    Medical Advisor Agent with RAG:
    - Uses vector database to retrieve guideline snippets and generate suggestions.
    """

    # PUBLIC_INTERFACE
    async def advise(self, interview_text: str, max_items: int = 3) -> List[Dict[str, Any]]:
        """Return structured suggestions with rationale and citations."""
        log.info("AdvisorAgent analyzing interview. length=%d", len(interview_text))
        results = await vector_client.query(interview_text, top_k=max(5, max_items * 2))
        suggestions: List[Dict[str, Any]] = []
        for idx, item in enumerate(results[:max_items]):
            title = f"Suggestion #{idx+1}"
            rationale = f"Based on retrieved evidence: {item.get('text','')[:300]}..."
            citations = [item.get("source", "guideline")]
            confidence = float(item.get("score", 0.5))
            suggestions.append(
                {
                    "title": title,
                    "rationale": rationale,
                    "citations": citations,
                    "confidence": min(max(confidence, 0.0), 1.0),
                }
            )
        if not suggestions:
            suggestions.append(
                {
                    "title": "No strong evidence found",
                    "rationale": "The RAG system did not return relevant matches. Consider broadening the query.",
                    "citations": [],
                    "confidence": 0.2,
                }
            )
        return suggestions


patient_interview_agent = PatientInterviewAgent()
medical_advisor_agent = MedicalAdvisorAgent()
