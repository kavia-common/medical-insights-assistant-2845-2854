import logging
from typing import List, Dict, Any
import httpx

from ..core.config import get_settings

log = logging.getLogger("app.rag.client")


class VectorDBClient:
    """
    Lightweight HTTP client for vector database RAG queries.
    Expects an API exposed by the 'medical_vector_database' container.

    Assumptions:
    - POST {VECTOR_DB_URL}/query with JSON { "query": str, "top_k": int }
      returns { "results": [ {"text": str, "score": float, "source": str}, ... ] }
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = httpx.AsyncClient(timeout=15.0)

    async def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.settings.VECTOR_DB_API_KEY:
            headers["Authorization"] = f"Bearer {self.settings.VECTOR_DB_API_KEY}"
        return headers

    # PUBLIC_INTERFACE
    async def query(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query the vector database for relevant guideline snippets."""
        url = f"{self.settings.VECTOR_DB_URL.rstrip('/')}/query"
        payload = {"query": query, "top_k": top_k}
        headers = await self._headers()
        log.info("RAG query: %s", query[:200])
        try:
            resp = await self._client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data.get("results", [])
        except Exception as ex:
            log.exception("Vector DB query failed: %s", ex)
            return []

    async def aclose(self) -> None:
        """Close underlying HTTP client."""
        await self._client.aclose()


vector_client = VectorDBClient()
