"""Run-related API endpoints."""
from fastapi import APIRouter
from app.models import RunDetail
from app.mock_data import MOCK_RUNS

router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.get("")
def list_runs():
    """List all available simulation runs."""
    return {"runs": MOCK_RUNS}


@router.get("/{run_id}")
def get_run_detail(run_id: int) -> RunDetail:
    """Get detailed information for a specific run."""
    run = next((r for r in MOCK_RUNS if r.id == run_id), None)
    
    if not run:
        # Fallback for invalid run_id
        return RunDetail(
            id=run_id,
            name="Unknown Run",
            model="Unknown",
            hw="Unknown",
            duration="N/A",
            status="unknown",
            metrics={},
        )

    # Generate mock metrics based on status
    base_metrics = {
        "battery": 62,
        "throughput": 12.4,
        "accuracy": 94.2,
        "fpr": 6.8,
        "latency": 48,
        "detections": 127,
    }
    
    # Adjust metrics based on status
    if run.status == "warning":
        base_metrics["congestion"] = 65
        base_metrics["battery"] = 35
        base_metrics["accuracy"] = 88.5
    elif run.status == "fail":
        base_metrics["congestion"] = 92
        base_metrics["battery"] = 15
        base_metrics["accuracy"] = 78.2
    else:  # pass
        base_metrics["congestion"] = 22
    
    return RunDetail(
        id=run.id,
        name=run.name,
        model=run.model,
        hw=run.hw,
        duration=run.duration,
        status=run.status,
        metrics=base_metrics,
    )

