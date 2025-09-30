from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query
from ..services.orchestrator import orchestrator

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/interview/step", summary="Interview step (by ID)", description="Trigger Interview Agent for a given interview.")
# PUBLIC_INTERFACE
async def agent_interview_step(interview_id: str = Query(..., description="Interview ID")) -> Dict[str, Any]:
    """Trigger interview agent to generate next questions."""
    try:
        return await orchestrator.run_interview_step(interview_id)
    except ValueError as ex:
        raise HTTPException(status_code=404, detail=str(ex))


@router.post("/advisor/run", summary="Advisor run (by ID)", description="Trigger Medical Advisor Agent for a given interview.")
# PUBLIC_INTERFACE
async def agent_advisor_run(
    interview_id: str = Query(..., description="Interview ID"), max_items: int = Query(3, ge=1, le=10)
) -> Dict[str, Any]:
    """Trigger advisor agent to generate evidence-based suggestions."""
    try:
        return await orchestrator.run_advisor(interview_id, max_items=max_items)
    except ValueError as ex:
        raise HTTPException(status_code=404, detail=str(ex))


@router.post("/crew/run", summary="Run crew workflow", description="Run a sequential workflow: interview step then advisor.")
# PUBLIC_INTERFACE
async def crew_run(
    interview_id: str = Query(..., description="Interview ID"), max_items: int = Query(3, ge=1, le=10)
) -> Dict[str, Any]:
    """
    Simulate a multi-agent crew workflow by running the interview step followed by advisor step.
    This can be adapted for true CrewAI orchestration.
    """
    await orchestrator.run_interview_step(interview_id)
    return await orchestrator.run_advisor(interview_id, max_items=max_items)
