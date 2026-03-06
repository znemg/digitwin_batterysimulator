"""AI assistant endpoints."""
from fastapi import APIRouter
from app.models import ChatQuery, ChatResponse

router = APIRouter(prefix="/api/ai", tags=["ai"])

# Mock responses for common queries
RESPONSE_MAP = {
    "battery": "R1 is at 23% battery — it's draining 3.2× faster than leaf sensors due to high relay traffic. Expect ~4.1 hours until critical threshold.",
    "gunshot": "Detected 28 gunshot events during the run; 26 were true positives with >0.90 confidence.",
    "bottleneck": "Nodes R1 and R2 handle 78% of total traffic. This creates a critical single-point-of-failure. Consider adding a relay node.",
    "false_positive": "The 6.8% false positive rate is slightly above the 5% target. Most false positives were chainsaw detections during high-wind periods.",
}

DEFAULT_RESPONSE = "That's a great question. Based on the run logs, the simulation completed within expected parameters. Could you be more specific?"


@router.get("/summary")
def get_summary():
    """Get AI-generated summary of the loaded run."""
    return {
        "title": "Run Summary",
        "content": "Forest_Night_01 completed a 24-hour simulation achieving 94.2% detection accuracy. Primary concern: network bottleneck at relay nodes R1 and R2.",
    }


@router.post("/chat", response_model=ChatResponse)
def chat(query: ChatQuery) -> ChatResponse:
    """Chat endpoint for run-specific questions."""
    q_lower = query.q.lower()
    
    for keyword, response in RESPONSE_MAP.items():
        if keyword in q_lower:
            return ChatResponse(answer=response)
    
    return ChatResponse(answer=DEFAULT_RESPONSE)
