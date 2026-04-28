"""
seed.py — Populate the DB with the same data currently in mock_data.py.
Run once: python -m app.seed
The UI will render identically — data just comes from DB now.
"""
import math
from datetime import date as Date
from app.database import SessionLocal, init_db
from app.db_models import (
    RunRow, RunMetricsRow, DetectionByTypeRow, LatencyByRankRow,
    AccuracyConfidenceCurveRow, NetworkNodeRow, NodeEventRow,
    NodeChildRow, NetworkEdgeRow, RerouteEventRow,
)

def _metrics_for_status(status: str) -> dict:
    base = {
        "accuracy": 94.2, "fpr": 6.8, "latency_ms": 48,
        "detection_count": 127, "battery_health": 62.0,
        "throughput": 12.4, "congestion": 22, "conf_threshold": 0.65,
    }
    if status == "warning":
        base.update({"accuracy": 88.5, "battery_health": 35.0, "congestion": 65})
    elif status == "fail":
        base.update({"accuracy": 78.2, "battery_health": 15.0, "congestion": 92})
    return base


def _detection_counts_for_status(status: str) -> list[dict]:
    """Slightly vary detection counts by status so each run looks different."""
    if status == "pass":
        return [
            {"event_type": "Bird",     "count": 42},
            {"event_type": "Gunshot",  "count": 28},
            {"event_type": "Chainsaw", "count": 22},
            {"event_type": "Voice",    "count": 20},
            {"event_type": "Vehicle",  "count": 15},
        ]
    elif status == "warning":
        return [
            {"event_type": "Bird",     "count": 30},
            {"event_type": "Gunshot",  "count": 18},
            {"event_type": "Chainsaw", "count": 28},
            {"event_type": "Voice",    "count": 14},
            {"event_type": "Vehicle",  "count": 10},
        ]
    else:  # fail
        return [
            {"event_type": "Bird",     "count": 15},
            {"event_type": "Gunshot",  "count": 9},
            {"event_type": "Chainsaw", "count": 35},
            {"event_type": "Voice",    "count": 8},
            {"event_type": "Vehicle",  "count": 6},
        ]


def _latency_by_rank_for_status(status: str) -> list[dict]:
    if status == "pass":
        return [{"rank": 1, "latency_ms": 38}, {"rank": 2, "latency_ms": 95}, {"rank": 3, "latency_ms": 142}]
    elif status == "warning":
        return [{"rank": 1, "latency_ms": 55}, {"rank": 2, "latency_ms": 120}, {"rank": 3, "latency_ms": 198}]
    else:
        return [{"rank": 1, "latency_ms": 80}, {"rank": 2, "latency_ms": 165}, {"rank": 3, "latency_ms": 260}]


def _acc_curve(status: str) -> list[dict]:
    """Generate accuracy/FPR curve points from threshold 0.30 to 0.95."""
    rows = []
    acc_peak = {"pass": 97.0, "warning": 92.0, "fail": 82.0}[status]
    for i in range(14):
        t = round(0.30 + i * 0.05, 2)
        acc = acc_peak * (1 - 0.3 * max(0, t - 0.65))
        fpr = max(0, 18.0 * math.exp(-4 * t) + 1.5)
        rows.append({"threshold": t, "accuracy": round(acc, 1), "fpr": round(fpr, 1)})
    return rows



RAW_NODES = [
    dict(node_id="CMD", label="Command Center", role="command", pos_x=0.50, pos_y=0.10,
         battery=100, drain=0.1, traffic=95, health="good", packets_in=4820, packets_out=312,
         retries=24, collisions=8, ai_det=127, parent_node_id=None,
         power_radio=15, power_processor=5, power_mic=0,
         events=["System boot", "All nodes online", "12 reroutes"], children=[]),
    dict(node_id="R1", label="Shaman II-1", role="relay", pos_x=0.28, pos_y=0.30,
         battery=23, drain=3.2, traffic=89, health="critical", packets_in=2640, packets_out=2580,
         retries=186, collisions=42, ai_det=0, parent_node_id=None,
         power_radio=55, power_processor=30, power_mic=15,
         events=["High relay load", "Battery warning"], children=["S1","S2","S3","S4"]),
    dict(node_id="R2", label="Shaman II-2", role="relay", pos_x=0.72, pos_y=0.28,
         battery=34, drain=2.8, traffic=82, health="warning", packets_in=2180, packets_out=2120,
         retries=148, collisions=35, ai_det=0, parent_node_id=None,
         power_radio=50, power_processor=32, power_mic=18,
         events=["Relay congestion", "Packet loss spike"], children=["S5","S6","S7"]),
    dict(node_id="R3", label="Shaman II-3", role="relay", pos_x=0.50, pos_y=0.48,
         battery=61, drain=1.4, traffic=45, health="good", packets_in=980, packets_out=940,
         retries=52, collisions=11, ai_det=0, parent_node_id=None,
         power_radio=40, power_processor=35, power_mic=25,
         events=["Normal operation"], children=["S8","S9","S10"]),
    dict(node_id="R4", label="Shaman II-4", role="relay", pos_x=0.16, pos_y=0.55,
         battery=55, drain=1.6, traffic=52, health="warning", packets_in=1120, packets_out=1080,
         retries=68, collisions=15, ai_det=0, parent_node_id=None,
         power_radio=45, power_processor=33, power_mic=22,
         events=["Moderate load"], children=["S11"]),
    dict(node_id="S1",  label="Shaman I-01", role="sensor", pos_x=0.10, pos_y=0.36,
         battery=72, drain=0.8, traffic=15, health="good", packets_in=42, packets_out=280,
         retries=12, collisions=3, ai_det=18, parent_node_id="R1",
         power_radio=30, power_processor=25, power_mic=45,
         events=["8 gunshot","6 bird"], children=[]),
    dict(node_id="S2",  label="Shaman I-02", role="sensor", pos_x=0.14, pos_y=0.20,
         battery=68, drain=0.9, traffic=18, health="good", packets_in=38, packets_out=310,
         retries=15, collisions=4, ai_det=22, parent_node_id="R1",
         power_radio=28, power_processor=27, power_mic=45,
         events=["12 bird","6 chainsaw"], children=[]),
    dict(node_id="S3",  label="Shaman I-03", role="sensor", pos_x=0.08, pos_y=0.50,
         battery=45, drain=1.1, traffic=22, health="warning", packets_in=52, packets_out=340,
         retries=28, collisions=8, ai_det=14, parent_node_id="R1",
         power_radio=35, power_processor=22, power_mic=43,
         events=["High retries","9 bird"], children=[]),
    dict(node_id="S4",  label="Shaman I-04", role="sensor", pos_x=0.22, pos_y=0.42,
         battery=78, drain=0.7, traffic=12, health="good", packets_in=36, packets_out=260,
         retries=8, collisions=2, ai_det=11, parent_node_id="R1",
         power_radio=26, power_processor=24, power_mic=50,
         events=["Normal","7 bird"], children=[]),
    dict(node_id="S5",  label="Shaman I-05", role="sensor", pos_x=0.86, pos_y=0.17,
         battery=70, drain=0.8, traffic=16, health="good", packets_in=40, packets_out=290,
         retries=14, collisions=3, ai_det=19, parent_node_id="R2",
         power_radio=30, power_processor=25, power_mic=45,
         events=["10 bird","5 gunshot"], children=[]),
    dict(node_id="S6",  label="Shaman I-06", role="sensor", pos_x=0.88, pos_y=0.38,
         battery=64, drain=0.9, traffic=20, health="good", packets_in=48, packets_out=320,
         retries=18, collisions=5, ai_det=16, parent_node_id="R2",
         power_radio=32, power_processor=23, power_mic=45,
         events=["8 bird","5 voice"], children=[]),
    dict(node_id="S7",  label="Shaman I-07", role="sensor", pos_x=0.78, pos_y=0.44,
         battery=58, drain=1.0, traffic=24, health="warning", packets_in=55, packets_out=350,
         retries=22, collisions=7, ai_det=13, parent_node_id="R2",
         power_radio=34, power_processor=24, power_mic=42,
         events=["Moderate retries","8 bird"], children=[]),
    dict(node_id="S8",  label="Shaman I-08", role="sensor", pos_x=0.38, pos_y=0.65,
         battery=80, drain=0.6, traffic=10, health="good", packets_in=30, packets_out=240,
         retries=6, collisions=1, ai_det=8, parent_node_id="R3",
         power_radio=25, power_processor=25, power_mic=50,
         events=["Low traffic","5 bird"], children=[]),
    dict(node_id="S9",  label="Shaman I-09", role="sensor", pos_x=0.56, pos_y=0.66,
         battery=75, drain=0.7, traffic=14, health="good", packets_in=35, packets_out=270,
         retries=10, collisions=2, ai_det=10, parent_node_id="R3",
         power_radio=28, power_processor=24, power_mic=48,
         events=["Normal","6 bird"], children=[]),
    dict(node_id="S10", label="Shaman I-10", role="sensor", pos_x=0.62, pos_y=0.56,
         battery=82, drain=0.6, traffic=9,  health="good", packets_in=28, packets_out=230,
         retries=5, collisions=1, ai_det=6, parent_node_id="R3",
         power_radio=24, power_processor=26, power_mic=50,
         events=["Low load","4 bird"], children=[]),
    dict(node_id="S11", label="Shaman I-11", role="sensor", pos_x=0.24, pos_y=0.70,
         battery=42, drain=1.2, traffic=28, health="warning", packets_in=60, packets_out=380,
         retries=32, collisions=10, ai_det=20, parent_node_id="R4",
         power_radio=36, power_processor=22, power_mic=42,
         events=["High detection"], children=[]),
]

RAW_EDGES = [
    dict(from_node="CMD", to_node="R1",  congestion=88, packet_loss=6.2, retries=86,  collisions=22, avg_delay=68, reroutes=4, latency=52),
    dict(from_node="CMD", to_node="R2",  congestion=80, packet_loss=5.1, retries=72,  collisions=18, avg_delay=55, reroutes=3, latency=48),
    dict(from_node="CMD", to_node="R3",  congestion=35, packet_loss=1.8, retries=22,  collisions=5,  avg_delay=28, reroutes=1, latency=32),
    dict(from_node="R1",  to_node="S1",  congestion=42, packet_loss=2.4, retries=18,  collisions=5,  avg_delay=32, reroutes=1, latency=28),
    dict(from_node="R1",  to_node="S2",  congestion=48, packet_loss=2.8, retries=22,  collisions=6,  avg_delay=35, reroutes=1, latency=30),
    dict(from_node="R1",  to_node="S3",  congestion=55, packet_loss=3.5, retries=30,  collisions=9,  avg_delay=42, reroutes=2, latency=38),
    dict(from_node="R1",  to_node="S4",  congestion=38, packet_loss=1.9, retries=14,  collisions=3,  avg_delay=25, reroutes=0, latency=22),
    dict(from_node="R1",  to_node="R4",  congestion=52, packet_loss=3.0, retries=28,  collisions=7,  avg_delay=38, reroutes=2, latency=35),
    dict(from_node="R2",  to_node="S5",  congestion=44, packet_loss=2.5, retries=20,  collisions=5,  avg_delay=30, reroutes=1, latency=26),
    dict(from_node="R2",  to_node="S6",  congestion=50, packet_loss=3.0, retries=24,  collisions=6,  avg_delay=36, reroutes=1, latency=32),
    dict(from_node="R2",  to_node="S7",  congestion=58, packet_loss=3.8, retries=28,  collisions=8,  avg_delay=44, reroutes=2, latency=40),
    dict(from_node="R3",  to_node="S8",  congestion=18, packet_loss=0.8, retries=6,   collisions=1,  avg_delay=15, reroutes=0, latency=14),
    dict(from_node="R3",  to_node="S9",  congestion=22, packet_loss=1.0, retries=8,   collisions=2,  avg_delay=18, reroutes=0, latency=16),
    dict(from_node="R3",  to_node="S10", congestion=15, packet_loss=0.6, retries=4,   collisions=1,  avg_delay=12, reroutes=0, latency=12),
    dict(from_node="R4",  to_node="S11", congestion=60, packet_loss=4.2, retries=34,  collisions=10, avg_delay=48, reroutes=3, latency=42),
    dict(from_node="R4",  to_node="S3",  congestion=30, packet_loss=1.5, retries=12,  collisions=3,  avg_delay=22, reroutes=1, latency=20),
    dict(from_node="R3",  to_node="R2",  congestion=28, packet_loss=1.2, retries=10,  collisions=2,  avg_delay=20, reroutes=0, latency=18),
    dict(from_node="R3",  to_node="R1",  congestion=32, packet_loss=1.6, retries=14,  collisions=3,  avg_delay=24, reroutes=1, latency=22),
]

RAW_REROUTES = [
    dict(from_node="S3",  to_node="R4"),
    dict(from_node="S7",  to_node="R3"),
    dict(from_node="S11", to_node="R3"),
]

RAW_RUNS = [
    dict(id=1,  name="Forest_Night_01",    date="2025-02-17", scenario="Tropical Night",  shamani="Radxa Zero", shamanii="Radxa Zero", duration="24h", status="pass"),
    dict(id=2,  name="Forest_Dawn_03",     date="2025-02-16", scenario="Dawn Chorus",     shamani="ESP32",      shamanii="Radxa Zero", duration="12h", status="warning"),
    dict(id=3,  name="Urban_Park_07",      date="2025-02-15", scenario="Urban Noise",     shamani="Radxa Zero", shamanii="Radxa Zero", duration="8h",  status="pass"),
    dict(id=4,  name="Wetland_Rain_02",    date="2025-02-14", scenario="Wetland Rain",    shamani="ESP32",      shamanii="Radxa Zero", duration="24h", status="fail"),
    dict(id=5,  name="Mountain_Clear_05",  date="2025-02-13", scenario="Mountain Clear",  shamani="Radxa Zero", shamanii="Radxa Zero", duration="16h", status="pass"),
    dict(id=6,  name="Forest_Storm_04",    date="2025-02-12", scenario="Storm Event",     shamani="ESP32",      shamanii="Radxa Zero", duration="6h",  status="warning"),
    dict(id=7,  name="Coastal_Night_01",   date="2025-02-11", scenario="Coastal Night",   shamani="Radxa Zero", shamanii="Radxa Zero", duration="24h", status="pass"),
    dict(id=8,  name="Desert_Day_02",      date="2025-02-10", scenario="Desert Sparse",   shamani="ESP32",      shamanii="Radxa Zero", duration="12h", status="pass"),
    dict(id=9,  name="Jungle_Dense_06",    date="2025-02-09", scenario="Dense Canopy",    shamani="Radxa Zero", shamanii="Radxa Zero", duration="24h", status="warning"),
    dict(id=10, name="River_Valley_03",    date="2025-02-08", scenario="River Valley",    shamani="ESP32",      shamanii="Radxa Zero", duration="8h",  status="pass"),
]

def seed():
    init_db()
    db = SessionLocal()
    try:
        # Skip if already seeded
        if db.query(RunRow).count() > 0:
            print("DB already seeded — skipping.")
            return
        
        for r in RAW_RUNS:
            run_date = r["date"]
            if isinstance(run_date, str):
                run_date = Date.fromisoformat(run_date)
            run = RunRow(
                id=r["id"], name=r["name"], date=run_date, scenario=r["scenario"], shamani=r["shamani"], shamanii=r["shamanii"], duration=r["duration"], status=r["status"],
            )
            db.add(run)
            db.flush()  # get run.id

            # Metrics
            m = _metrics_for_status(r["status"])
            db.add(RunMetricsRow(run_id=run.id, **m))

            # Detections by type
            for det in _detection_counts_for_status(r["status"]):
                db.add(DetectionByTypeRow(run_id=run.id, **det))

            # Latency by rank
            for lr in _latency_by_rank_for_status(r["status"]):
                db.add(LatencyByRankRow(run_id=run.id, **lr))

            # Accuracy/confidence curve
            for pt in _acc_curve(r["status"]):
                db.add(AccuracyConfidenceCurveRow(run_id=run.id, **pt))

            # Nodes (same topology for every run — realistic for MVP)
            for n in RAW_NODES:
                node = NetworkNodeRow(
                    run_id=run.id,
                    node_id=n["node_id"], label=n["label"], role=n["role"],
                    pos_x=n["pos_x"], pos_y=n["pos_y"],
                    battery=n["battery"], drain=n["drain"], traffic=n["traffic"],
                    health=n["health"], packets_in=n["packets_in"], packets_out=n["packets_out"],
                    retries=n["retries"], collisions=n["collisions"], ai_det=n["ai_det"],
                    parent_node_id=n["parent_node_id"],
                    power_radio=n["power_radio"], power_processor=n["power_processor"],
                    power_mic=n["power_mic"],
                )
                db.add(node)
                for ev in n["events"]:
                    db.add(NodeEventRow(run_id=run.id, node_id=n["node_id"], event_text=ev))
                for child in n["children"]:
                    db.add(NodeChildRow(run_id=run.id, parent_node_id=n["node_id"], child_node_id=child))

            # Edges
            for e in RAW_EDGES:
                db.add(NetworkEdgeRow(run_id=run.id, **e))

            # Reroutes
            for rr in RAW_REROUTES:
                db.add(RerouteEventRow(run_id=run.id, **rr))

        db.commit()
        print(f"Seeded {len(RAW_RUNS)} runs with full topology and metrics.")
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Physics-based seed data — computed by simulator.py
# ---------------------------------------------------------------------------

# Shared power configs (W) for all simulated runs
_SIM_II_CFG = dict(
    proc_act=0.50, proc_slp=0.04, ctrl_act=0.30, ctrl_slp=0.02,
    radio_tx=0.42, radio_rx=0.22, backoff=0.10,
    t_proc=0.012, t_radio_tx=0.025, t_radio_rx=0.012, t_backoff=0.05, f_hop=1.0,
)
_SIM_I_CFG = dict(
    proc_slp=0.001, proc_wrk=0.050, radio_tx=0.300, radio_rx=0.150,
    cam_img=0.200, cam_slp=0.001, mic_listen=0.012, mic_slp=0.001,
    t_proc=0.010, t_radio_tx=0.020, t_radio_rx=0.010, t_cam_img=0.050,
)

# Same topology for all simulated runs (mirrors RAW_NODES structure)
_SIM_TOPOLOGY = [
    dict(node_id="CMD", node_type="Command Center", x=0.50, y=0.10, parent_id=None,  child_ids=["R1","R2","R3"],          rank=0, battery_capacity_wh=9999,   power_config=None),
    dict(node_id="R1",  node_type="Shaman II",      x=0.28, y=0.30, parent_id="CMD", child_ids=["S1","S2","S3","S4","R4"],rank=1, battery_capacity_wh=10.0,   power_config=_SIM_II_CFG),
    dict(node_id="R2",  node_type="Shaman II",      x=0.72, y=0.28, parent_id="CMD", child_ids=["S5","S6","S7"],          rank=1, battery_capacity_wh=10.0,   power_config=_SIM_II_CFG),
    dict(node_id="R3",  node_type="Shaman II",      x=0.50, y=0.48, parent_id="CMD", child_ids=["S8","S9","S10"],         rank=1, battery_capacity_wh=10.0,   power_config=_SIM_II_CFG),
    dict(node_id="R4",  node_type="Shaman II",      x=0.16, y=0.55, parent_id="R1",  child_ids=["S11"],                   rank=2, battery_capacity_wh=10.0,   power_config=_SIM_II_CFG),
    dict(node_id="S1",  node_type="Shaman I",       x=0.10, y=0.36, parent_id="R1",  child_ids=[],                        rank=2, battery_capacity_wh=5.0,    power_config=_SIM_I_CFG),
    dict(node_id="S2",  node_type="Shaman I",       x=0.14, y=0.20, parent_id="R1",  child_ids=[],                        rank=2, battery_capacity_wh=5.0,    power_config=_SIM_I_CFG),
    dict(node_id="S3",  node_type="Shaman I",       x=0.08, y=0.50, parent_id="R1",  child_ids=[],                        rank=2, battery_capacity_wh=5.0,    power_config=_SIM_I_CFG),
    dict(node_id="S4",  node_type="Shaman I",       x=0.22, y=0.42, parent_id="R1",  child_ids=[],                        rank=2, battery_capacity_wh=5.0,    power_config=_SIM_I_CFG),
    dict(node_id="S5",  node_type="Shaman I",       x=0.86, y=0.17, parent_id="R2",  child_ids=[],                        rank=2, battery_capacity_wh=5.0,    power_config=_SIM_I_CFG),
    dict(node_id="S6",  node_type="Shaman I",       x=0.88, y=0.38, parent_id="R2",  child_ids=[],                        rank=2, battery_capacity_wh=5.0,    power_config=_SIM_I_CFG),
    dict(node_id="S7",  node_type="Shaman I",       x=0.78, y=0.44, parent_id="R2",  child_ids=[],                        rank=2, battery_capacity_wh=5.0,    power_config=_SIM_I_CFG),
    dict(node_id="S8",  node_type="Shaman I",       x=0.38, y=0.65, parent_id="R3",  child_ids=[],                        rank=2, battery_capacity_wh=5.0,    power_config=_SIM_I_CFG),
    dict(node_id="S9",  node_type="Shaman I",       x=0.56, y=0.66, parent_id="R3",  child_ids=[],                        rank=2, battery_capacity_wh=5.0,    power_config=_SIM_I_CFG),
    dict(node_id="S10", node_type="Shaman I",       x=0.62, y=0.56, parent_id="R3",  child_ids=[],                        rank=2, battery_capacity_wh=5.0,    power_config=_SIM_I_CFG),
    dict(node_id="S11", node_type="Shaman I",       x=0.24, y=0.70, parent_id="R4",  child_ids=[],                        rank=3, battery_capacity_wh=5.0,    power_config=_SIM_I_CFG),
]

# Node label / role mapping for DB (mirrors RAW_NODES)
_SIM_NODE_META = {
    "CMD": dict(label="Command Center",  role="command", parent_node_id=None,  children=[], events=["System boot","All nodes online","12 reroutes"]),
    "R1":  dict(label="Shaman II-1",     role="relay",   parent_node_id=None,  children=["S1","S2","S3","S4"], events=["High relay load","Battery warning"]),
    "R2":  dict(label="Shaman II-2",     role="relay",   parent_node_id=None,  children=["S5","S6","S7"],      events=["Relay congestion","Packet loss spike"]),
    "R3":  dict(label="Shaman II-3",     role="relay",   parent_node_id=None,  children=["S8","S9","S10"],     events=["Normal operation"]),
    "R4":  dict(label="Shaman II-4",     role="relay",   parent_node_id="R1",  children=["S11"],               events=["Moderate load"]),
    "S1":  dict(label="Shaman I-01",     role="sensor",  parent_node_id="R1",  children=[], events=["8 gunshot","6 bird"]),
    "S2":  dict(label="Shaman I-02",     role="sensor",  parent_node_id="R1",  children=[], events=["12 bird","6 chainsaw"]),
    "S3":  dict(label="Shaman I-03",     role="sensor",  parent_node_id="R1",  children=[], events=["High retries","9 bird"]),
    "S4":  dict(label="Shaman I-04",     role="sensor",  parent_node_id="R1",  children=[], events=["Normal","7 bird"]),
    "S5":  dict(label="Shaman I-05",     role="sensor",  parent_node_id="R2",  children=[], events=["10 bird","5 gunshot"]),
    "S6":  dict(label="Shaman I-06",     role="sensor",  parent_node_id="R2",  children=[], events=["8 bird","5 voice"]),
    "S7":  dict(label="Shaman I-07",     role="sensor",  parent_node_id="R2",  children=[], events=["Moderate retries","8 bird"]),
    "S8":  dict(label="Shaman I-08",     role="sensor",  parent_node_id="R3",  children=[], events=["Low traffic","5 bird"]),
    "S9":  dict(label="Shaman I-09",     role="sensor",  parent_node_id="R3",  children=[], events=["Normal","6 bird"]),
    "S10": dict(label="Shaman I-10",     role="sensor",  parent_node_id="R3",  children=[], events=["Low load","4 bird"]),
    "S11": dict(label="Shaman I-11",     role="sensor",  parent_node_id="R4",  children=[], events=["High detection"]),
}

# Per-scenario event profiles: (node_id, hour_offset, triggers_camera)
# More events → more drain → lower final battery
_SCENARIO_EVENTS = {
    "pass": [
        ("S1", 2.0, False), ("S1", 5.0, False), ("S1", 9.0, False),
        ("S1",14.0, False), ("S1",18.0, False), ("S1",22.0, False),
        ("S2", 1.0, False), ("S2", 3.5, False), ("S2", 6.0, False),
        ("S2",10.0, False), ("S2",14.0, False), ("S2",17.5, False),
        ("S2",21.0, False),
        ("S3", 3.0, True),  ("S3", 8.0, True),  ("S3",13.0, True),
        ("S3",18.0, True),  ("S3",22.0, True),
        ("S4", 4.0, False), ("S4", 9.0, False), ("S4",15.0, False),
        ("S4",20.0, False),
        ("S5", 2.5, False), ("S5", 5.5, False), ("S5", 9.0, False),
        ("S5",12.0, False), ("S5",16.0, False), ("S5",20.0, False),
        ("S6", 3.0, False), ("S6", 7.0, False), ("S6",11.0, False),
        ("S6",15.5, False), ("S6",19.0, False),
        ("S7", 4.0, False), ("S7", 9.5, False), ("S7",15.0, False),
        ("S7",20.5, False),
        ("S8", 5.0, False), ("S8",11.0, False), ("S8",18.0, False),
        ("S9", 6.0, False), ("S9",13.0, False), ("S9",20.0, False),
        ("S10",7.0, False), ("S10",15.0, False),
        ("S11",1.5, True),  ("S11",3.0, True),  ("S11",4.5, False),
        ("S11",6.0, True),  ("S11",8.0, False), ("S11",10.0,True),
        ("S11",12.0,False), ("S11",14.0,True),  ("S11",16.0,False),
        ("S11",18.0,True),  ("S11",20.0,False), ("S11",22.0,True),
    ],
    "warning": [   # more activity → more drain
        ("S1", 1.5, False), ("S1", 3.0, False), ("S1", 5.0, True),
        ("S1", 7.5, False), ("S1",10.0, True),  ("S1",13.0, False),
        ("S1",16.0, True),  ("S1",19.0, False), ("S1",22.0, True),
        ("S2", 1.0, False), ("S2", 2.5, True),  ("S2", 4.5, False),
        ("S2", 6.5, True),  ("S2", 9.0, False), ("S2",12.0, True),
        ("S2",15.0, False), ("S2",18.0, True),  ("S2",21.0, False),
        ("S3", 2.0, True),  ("S3", 4.0, True),  ("S3", 6.0, True),
        ("S3", 8.5, True),  ("S3",11.0, True),  ("S3",13.5, True),
        ("S3",16.0, True),  ("S3",19.0, True),  ("S3",22.0, True),
        ("S4", 2.0, False), ("S4", 5.0, True),  ("S4", 9.0, False),
        ("S4",13.0, True),  ("S4",17.0, False), ("S4",21.0, True),
        ("S5", 1.5, False), ("S5", 3.5, True),  ("S5", 6.0, False),
        ("S5", 8.5, True),  ("S5",11.5, False), ("S5",14.0, True),
        ("S5",17.0, False), ("S5",20.0, True),  ("S5",23.0, False),
        ("S6", 2.0, False), ("S6", 4.5, True),  ("S6", 7.5, False),
        ("S6",10.5, True),  ("S6",13.5, False), ("S6",16.5, True),
        ("S6",19.5, False), ("S6",22.5, True),
        ("S7", 2.5, True),  ("S7", 5.5, True),  ("S7", 9.0, True),
        ("S7",12.5, True),  ("S7",16.0, True),  ("S7",20.0, True),
        ("S8", 3.0, False), ("S8", 7.0, True),  ("S8",12.0, False),
        ("S8",17.0, True),  ("S8",22.0, False),
        ("S9", 3.5, False), ("S9", 8.0, True),  ("S9",13.0, False),
        ("S9",18.0, True),  ("S9",22.5, False),
        ("S10",4.0, False), ("S10",9.0, True),  ("S10",14.0, False),
        ("S10",19.0,True),  ("S10",23.0,False),
        ("S11",0.5, True),  ("S11",1.5, True),  ("S11",2.5, True),
        ("S11",3.5, True),  ("S11",4.5, True),  ("S11",5.5, True),
        ("S11",6.5, True),  ("S11",7.5, True),  ("S11",8.5, True),
        ("S11",9.5, True),  ("S11",10.5,True),  ("S11",11.5,True),
        ("S11",12.5,True),  ("S11",13.5,True),  ("S11",14.5,True),
        ("S11",15.5,True),  ("S11",16.5,True),  ("S11",17.5,True),
        ("S11",18.5,True),  ("S11",19.5,True),
    ],
    "fail": [      # maximum activity → maximum drain, some nodes die
        ("S1", 0.5, True),  ("S1", 1.0, True),  ("S1", 1.5, True),
        ("S1", 2.0, True),  ("S1", 2.5, True),  ("S1", 3.0, True),
        ("S1", 3.5, True),  ("S1", 4.0, True),  ("S1", 4.5, True),
        ("S1", 5.0, True),  ("S1", 5.5, True),  ("S1", 6.0, True),
        ("S2", 0.5, True),  ("S2", 1.0, True),  ("S2", 1.5, True),
        ("S2", 2.0, True),  ("S2", 2.5, True),  ("S2", 3.0, True),
        ("S2", 3.5, True),  ("S2", 4.0, True),  ("S2", 4.5, True),
        ("S2", 5.0, True),  ("S2", 5.5, True),  ("S2", 6.0, True),
        ("S3", 0.5, True),  ("S3", 1.0, True),  ("S3", 1.5, True),
        ("S3", 2.0, True),  ("S3", 2.5, True),  ("S3", 3.0, True),
        ("S3", 3.5, True),  ("S3", 4.0, True),  ("S3", 4.5, True),
        ("S3", 5.0, True),  ("S3", 5.5, True),  ("S3", 6.0, True),
        ("S4", 0.5, True),  ("S4", 1.0, True),  ("S4", 1.5, True),
        ("S4", 2.0, True),  ("S4", 2.5, True),  ("S4", 3.0, True),
        ("S4", 3.5, True),  ("S4", 4.0, True),  ("S4", 4.5, True),
        ("S4", 5.0, True),  ("S4", 5.5, True),  ("S4", 6.0, True),
        ("S5", 0.5, True),  ("S5", 1.5, True),  ("S5", 2.5, True),
        ("S5", 3.5, True),  ("S5", 4.5, True),  ("S5", 5.5, True),
        ("S5", 6.5, True),  ("S5", 7.5, True),  ("S5", 8.5, True),
        ("S5", 9.5, True),  ("S5",10.5, True),  ("S5",11.5, True),
        ("S6", 0.5, True),  ("S6", 1.5, True),  ("S6", 2.5, True),
        ("S6", 3.5, True),  ("S6", 4.5, True),  ("S6", 5.5, True),
        ("S6", 6.5, True),  ("S6", 7.5, True),  ("S6", 8.5, True),
        ("S6", 9.5, True),  ("S6",10.5, True),  ("S6",11.5, True),
        ("S7", 1.0, True),  ("S7", 2.5, True),  ("S7", 4.0, True),
        ("S7", 5.5, True),  ("S7", 7.0, True),  ("S7", 8.5, True),
        ("S7",10.0, True),  ("S7",11.5, True),  ("S7",13.0, True),
        ("S7",14.5, True),  ("S7",16.0, True),  ("S7",17.5, True),
        ("S8", 1.0, True),  ("S8", 3.0, True),  ("S8", 5.0, True),
        ("S8", 7.0, True),  ("S8", 9.0, True),  ("S8",11.0, True),
        ("S9", 1.5, True),  ("S9", 4.0, True),  ("S9", 6.5, True),
        ("S9", 9.0, True),  ("S9",11.5, True),
        ("S10",2.0, True),  ("S10",5.0, True),  ("S10",8.0, True),
        ("S10",11.0,True),
        ("S11",0.5, True),  ("S11",1.0, True),  ("S11",1.5, True),
        ("S11",2.0, True),  ("S11",2.5, True),  ("S11",3.0, True),
        ("S11",3.5, True),  ("S11",4.0, True),  ("S11",4.5, True),
        ("S11",5.0, True),  ("S11",5.5, True),  ("S11",6.0, True),
        ("S11",6.5, True),  ("S11",7.0, True),  ("S11",7.5, True),
        ("S11",8.0, True),  ("S11",8.5, True),  ("S11",9.0, True),
        ("S11",9.5, True),  ("S11",10.0,True),  ("S11",10.5,True),
        ("S11",11.0,True),  ("S11",11.5,True),  ("S11",12.0,True),
    ],
}

SIM_RUNS = [
    dict(id=11, name="Sim_Forest_Night_01",   date="2025-03-10", scenario="Tropical Night", shamani="Radxa Zero", shamanii="Radxa Zero", duration="24h", status="pass"),
    dict(id=12, name="Sim_Forest_Dawn_03",    date="2025-03-09", scenario="Dawn Chorus",    shamani="ESP32",      shamanii="Radxa Zero", duration="24h", status="warning"),
    dict(id=13, name="Sim_Wetland_Rain_02",   date="2025-03-08", scenario="Wetland Rain",   shamani="ESP32",      shamanii="Radxa Zero", duration="24h", status="fail"),
]

SIM_EDGES = RAW_EDGES  # same topology


def _build_sim_events(scenario_status: str, duration_h: float) -> list:
    raw = _SCENARIO_EVENTS[scenario_status]
    return [
        {"node_id": nid, "time": h * 3600.0, "triggers_camera": cam}
        for nid, h, cam in raw
        if h < duration_h
    ]


def _run_physics_sim(status: str, duration_h: float) -> dict:
    """Run the energy simulator and return per-node output dict."""
    from app.simulator import run_from_dict
    n_retry = {"pass": 2, "warning": 4, "fail": 8}[status]
    payload = {
        "nodes":      _SIM_TOPOLOGY,
        "events":     _build_sim_events(status, duration_h),
        "total_time": duration_h * 3600.0,
        "time_step":  3600.0,
        "n_retry_default": n_retry,
    }
    return run_from_dict(payload)["nodes"]


def _health_from_pct(pct: float) -> str:
    if pct > 50: return "good"
    if pct > 20: return "warning"
    return "critical"


def _sim_metrics(sim_nodes: dict, status: str) -> dict:
    """Derive run-level metrics from simulator output."""
    batteries = [
        nd["battery_percent_series"][-1]
        for nd in sim_nodes.values()
        if nd["battery_percent_series"] and nd["node_type"] != "Command Center"
    ]
    avg_battery = round(sum(batteries) / len(batteries), 2) if batteries else 100.0
    total_retries = sum(nd["total_retries"] for nd in sim_nodes.values())
    congestion = min(99, round(total_retries / max(len(sim_nodes), 1) * 2))
    base = _metrics_for_status(status)
    base["battery_health"] = avg_battery
    base["congestion"] = congestion
    return base


def seed_simulated():
    """Seed physics-based runs (IDs 11–13). Safe to call alongside seed()."""
    from app.simulator import run_from_dict  # noqa: F401 — ensure importable
    init_db()
    db = SessionLocal()
    try:
        existing_ids = {r.id for r in db.query(RunRow.id).all()}

        for r in SIM_RUNS:
            if r["id"] in existing_ids:
                continue

            duration_h = float(r["duration"].replace("h", ""))
            sim_nodes = _run_physics_sim(r["status"], duration_h)

            run_date = Date.fromisoformat(r["date"])
            run = RunRow(
                id=r["id"], name=r["name"], date=run_date,
                scenario=r["scenario"], shamani=r["shamani"],
                shamanii=r["shamanii"], duration=r["duration"], status=r["status"],
            )
            db.add(run)
            db.flush()

            # Metrics derived from simulation
            m = _sim_metrics(sim_nodes, r["status"])
            db.add(RunMetricsRow(run_id=run.id, **m))

            for det in _detection_counts_for_status(r["status"]):
                db.add(DetectionByTypeRow(run_id=run.id, **det))
            for lr in _latency_by_rank_for_status(r["status"]):
                db.add(LatencyByRankRow(run_id=run.id, **lr))
            for pt in _acc_curve(r["status"]):
                db.add(AccuracyConfidenceCurveRow(run_id=run.id, **pt))

            # Nodes — values from simulator
            for topo_node in _SIM_TOPOLOGY:
                nid = topo_node["node_id"]
                sim = sim_nodes.get(nid, {})
                meta = _SIM_NODE_META[nid]

                pct_series = sim.get("battery_percent_series", [])
                energy_series = sim.get("battery_energy_series", [])
                final_pct = pct_series[-1] if pct_series else 100.0
                steps = len(energy_series)
                drain = round(
                    (energy_series[0] - energy_series[-1]) / max(steps, 1), 6
                ) if steps > 1 else 0.0

                timeseries = {
                    "time_series":            sim.get("time_series", []),
                    "battery_energy_series":  energy_series,
                    "battery_percent_series": pct_series,
                    "alive_series":           sim.get("alive_series", []),
                    "death_time":             sim.get("death_time"),
                } if pct_series else None

                # traffic ~ forwarded messages; retries from simulator
                total_fwd     = sim.get("total_forwarded", 0)
                total_retries = sim.get("total_retries", 0)
                traffic = min(99, round(total_fwd * 2 + total_retries))

                # power breakdown (mW integers): derive from config watts
                pc = topo_node["power_config"] or {}
                power_radio     = round((pc.get("radio_tx", 0) + pc.get("radio_rx", 0)) * 500)
                power_processor = round(pc.get("proc_wrk", pc.get("proc_act", 0)) * 500)
                power_mic       = round(pc.get("mic_listen", 0) * 500)

                db_node = NetworkNodeRow(
                    run_id=run.id,
                    node_id=nid,
                    label=meta["label"],
                    role=meta["role"],
                    pos_x=topo_node["x"],
                    pos_y=topo_node["y"],
                    battery=max(0, min(100, round(final_pct))),
                    drain=round(drain * 1000, 4),   # convert Wh/step → mWh for display
                    traffic=max(0, traffic),
                    health=_health_from_pct(final_pct),
                    packets_in=total_fwd,
                    packets_out=total_fwd,
                    retries=total_retries,
                    collisions=max(0, round(total_retries * 0.2)),
                    ai_det=len([e for e in _build_sim_events(r["status"], duration_h) if e["node_id"] == nid]),
                    parent_node_id=meta["parent_node_id"],
                    power_radio=max(1, power_radio),
                    power_processor=max(1, power_processor),
                    power_mic=max(0, power_mic),
                    battery_timeseries=timeseries,
                )
                db.add(db_node)

                for ev in meta["events"]:
                    db.add(NodeEventRow(run_id=run.id, node_id=nid, event_text=ev))
                for child in meta["children"]:
                    db.add(NodeChildRow(run_id=run.id, parent_node_id=nid, child_node_id=child))

            for e in SIM_EDGES:
                db.add(NetworkEdgeRow(run_id=run.id, **e))
            for rr in RAW_REROUTES:
                db.add(RerouteEventRow(run_id=run.id, **rr))

        db.commit()
        print(f"Seeded {len(SIM_RUNS)} physics-based runs (IDs 11–13).")
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    seed_simulated()