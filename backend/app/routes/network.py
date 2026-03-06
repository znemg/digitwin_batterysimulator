"""Network map API endpoints."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.models import NetworkMap
from app.mock_data import MOCK_NODES, MOCK_EDGES, MOCK_REROUTES

router = APIRouter(prefix="/api", tags=["network"])


@router.get("/netmap")
def get_netmap():
    """Get current network topology and status."""
    netmap = NetworkMap(nodes=MOCK_NODES, edges=MOCK_EDGES, reroutes=MOCK_REROUTES)
    return JSONResponse(content=netmap.model_dump(by_alias=True))
