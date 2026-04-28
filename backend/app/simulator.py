"""
Graph-based energy simulator for the Digital Twin sensor network.

Layers
------
1. Graph / Topology        – directed parent-child graph of nodes
2. Configuration           – loads and validates inputs
3. Energy Model            – Shaman I / Shaman II energy equations
4. Simulation Engine       – time-stepped battery depletion
5. Output                  – per-node battery-over-time data
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# 1. Graph / Topology Layer
# ---------------------------------------------------------------------------

NODE_TYPE_SHAMAN_I = "Shaman I"
NODE_TYPE_SHAMAN_II = "Shaman II"
NODE_TYPE_COMMAND = "Command Center"
VALID_NODE_TYPES = {NODE_TYPE_SHAMAN_I, NODE_TYPE_SHAMAN_II, NODE_TYPE_COMMAND}


@dataclass
class ShamanIPowerConfig:
    proc_slp: float      # W – processor sleep
    proc_wrk: float      # W – processor working
    radio_tx: float      # W – radio transmit
    radio_rx: float      # W – radio receive
    cam_img: float       # W – camera imaging
    cam_slp: float       # W – camera sleep
    mic_listen: float    # W – mic listening
    mic_slp: float       # W – mic sleep
    # per-event time constants (seconds)
    t_proc: float        # s – time to process one event
    t_radio_tx: float    # s – time to transmit one message
    t_radio_rx: float    # s – time to receive one message
    t_cam_img: float     # s – time for one camera capture


@dataclass
class ShamanIIPowerConfig:
    proc_act: float      # W
    proc_slp: float      # W
    ctrl_act: float      # W
    ctrl_slp: float      # W
    radio_tx: float      # W
    radio_rx: float      # W
    backoff: float       # W
    # per-event time constants
    t_proc: float        # s
    t_radio_tx: float    # s
    t_radio_rx: float    # s
    t_backoff: float     # s
    f_hop: float = 1.0   # frames per hop (protocol overhead)


@dataclass
class Node:
    node_id: str
    node_type: str
    x: float
    y: float
    parent_id: Optional[str]
    child_ids: List[str]
    rank: int
    battery_capacity_wh: float                        # E_i^max
    power_config: Optional[ShamanIPowerConfig | ShamanIIPowerConfig] = None

    def validate(self) -> None:
        if self.node_type not in VALID_NODE_TYPES:
            raise ValueError(f"Node {self.node_id}: invalid type '{self.node_type}'")
        if self.battery_capacity_wh < 0:
            raise ValueError(f"Node {self.node_id}: battery capacity must be >= 0")
        if self.node_type == NODE_TYPE_SHAMAN_I and not isinstance(self.power_config, ShamanIPowerConfig):
            raise ValueError(f"Node {self.node_id}: Shaman I requires ShamanIPowerConfig")
        if self.node_type == NODE_TYPE_SHAMAN_II and not isinstance(self.power_config, ShamanIIPowerConfig):
            raise ValueError(f"Node {self.node_id}: Shaman II requires ShamanIIPowerConfig")


@dataclass
class Graph:
    nodes: Dict[str, Node] = field(default_factory=dict)

    def add_node(self, node: Node) -> None:
        self.nodes[node.node_id] = node

    def validate(self) -> None:
        if not self.nodes:
            return
        for node in self.nodes.values():
            node.validate()
            if node.parent_id and node.parent_id not in self.nodes:
                raise ValueError(
                    f"Node {node.node_id}: parent '{node.parent_id}' not found in graph"
                )
            for child_id in node.child_ids:
                if child_id not in self.nodes:
                    raise ValueError(
                        f"Node {node.node_id}: child '{child_id}' not found in graph"
                    )
        self._check_no_cycles()

    def _check_no_cycles(self) -> None:
        visited: set[str] = set()
        in_stack: set[str] = set()

        def dfs(nid: str) -> None:
            visited.add(nid)
            in_stack.add(nid)
            for child_id in self.nodes[nid].child_ids:
                if child_id not in visited:
                    dfs(child_id)
                elif child_id in in_stack:
                    raise ValueError(
                        f"Cycle detected involving node '{child_id}'"
                    )
            in_stack.discard(nid)

        for nid in self.nodes:
            if nid not in visited:
                dfs(nid)

    def topological_order(self) -> List[str]:
        """Return nodes in topological order (leaves first, command center last)."""
        visited: set[str] = set()
        order: List[str] = []

        def dfs(nid: str) -> None:
            if nid in visited:
                return
            visited.add(nid)
            for child_id in self.nodes[nid].child_ids:
                dfs(child_id)
            order.append(nid)

        for nid in self.nodes:
            dfs(nid)

        order.reverse()
        return order


# ---------------------------------------------------------------------------
# 2. Configuration Layer
# ---------------------------------------------------------------------------

@dataclass
class EventRecord:
    """A single event in the timeline."""
    node_id: str
    time: float       # seconds from simulation start
    # Optional flags – extend as needed
    triggers_camera: bool = False


@dataclass
class SimulationConfig:
    graph: Graph
    events: List[EventRecord]
    total_time: float          # seconds
    time_step: float = 1.0     # seconds per simulation step
    n_retry_default: int = 0   # default retries per forwarding node per step


def build_graph_from_dict(data: dict) -> Graph:
    """
    Construct a Graph from a plain dict.

    Expected format::

        {
          "nodes": [
            {
              "node_id": "n1",
              "node_type": "Shaman I",
              "x": 0.0, "y": 0.0,
              "parent_id": "n2",
              "child_ids": [],
              "rank": 2,
              "battery_capacity_wh": 5.0,
              "power_config": { ... }   # flat dict matching field names
            },
            ...
          ]
        }
    """
    graph = Graph()
    for nd in data.get("nodes", []):
        ntype = nd["node_type"]
        pc: Optional[ShamanIPowerConfig | ShamanIIPowerConfig] = None
        raw_pc = nd.get("power_config")
        if raw_pc:
            if ntype == NODE_TYPE_SHAMAN_I:
                pc = ShamanIPowerConfig(**raw_pc)
            elif ntype == NODE_TYPE_SHAMAN_II:
                pc = ShamanIIPowerConfig(**raw_pc)
        node = Node(
            node_id=nd["node_id"],
            node_type=ntype,
            x=nd.get("x", 0.0),
            y=nd.get("y", 0.0),
            parent_id=nd.get("parent_id"),
            child_ids=nd.get("child_ids", []),
            rank=nd.get("rank", 0),
            battery_capacity_wh=nd["battery_capacity_wh"],
            power_config=pc,
        )
        graph.add_node(node)
    return graph


# ---------------------------------------------------------------------------
# 3. Energy Model Layer
# ---------------------------------------------------------------------------

# Shaman I total energy per step:
#   E^(I) = E_proc + E_radio + E_mic + E_cam
#
#   E_proc  = n_local · P_proc_wrk · t_proc  +  P_proc_slp · T_proc_slp
#   E_radio = n_tx · P_radio_tx · t_radio_tx
#   E_mic   = P_mic_listen · T_mic_listen  +  P_mic_slp · T_mic_slp
#   E_cam   = n_cam · P_cam_img · t_cam_img  +  P_cam_slp · T_cam_slp
def _energy_shaman_i(
    cfg: ShamanIPowerConfig,
    n_local: int,
    n_tx: int,
    n_cam: int,
    T_proc_slp: float,
    T_mic_listen: float,
    T_mic_slp: float,
    T_cam_slp: float,
) -> float:
    """Return total Shaman I energy (Wh) for a simulation step."""
    E_proc = (
        n_local * cfg.proc_wrk * cfg.t_proc
        + cfg.proc_slp * T_proc_slp
    )
    E_radio = n_tx * cfg.radio_tx * cfg.t_radio_tx
    E_mic = cfg.mic_listen * T_mic_listen + cfg.mic_slp * T_mic_slp
    E_cam = (
        n_cam * cfg.cam_img * cfg.t_cam_img
        + cfg.cam_slp * T_cam_slp
    )
    # convert W·s → Wh
    return (E_proc + E_radio + E_mic + E_cam) / 3600.0


# Shaman II total energy per step:
#   E^(II) = E_idle + E_rx + E_proc + E_tx + E_retry
#
#   n_fwd   = n_local + n_rx          (network flow constraint)
#   n_rx    = Σ n_tx  over all children
#
#   E_idle  = (P_proc_slp + P_ctrl_slp + P_radio_rx) · T_idle
#   E_rx    = n_rx · P_radio_rx · t_radio_rx
#   E_proc  = n_fwd · P_proc_act · t_proc
#   E_tx    = n_fwd · P_radio_tx · t_radio_tx · f_hop
#   E_retry = n_retry · (P_radio_tx · t_radio_tx + P_backoff · t_backoff)
def _energy_shaman_ii(
    cfg: ShamanIIPowerConfig,
    n_local: int,
    n_rx: int,
    n_retry: int,
    T_idle: float,
) -> float:
    """Return total Shaman II energy (Wh) for a simulation step."""
    n_fwd = n_local + n_rx

    E_idle = (cfg.proc_slp + cfg.ctrl_slp + cfg.radio_rx) * T_idle
    E_rx = n_rx * cfg.radio_rx * cfg.t_radio_rx
    E_proc = n_fwd * cfg.proc_act * cfg.t_proc
    E_tx = n_fwd * cfg.radio_tx * cfg.t_radio_tx * cfg.f_hop
    E_retry = n_retry * (
        cfg.radio_tx * cfg.t_radio_tx + cfg.backoff * cfg.t_backoff
    )
    return (E_idle + E_rx + E_proc + E_tx + E_retry) / 3600.0


# ---------------------------------------------------------------------------
# 4. Simulation Engine
# ---------------------------------------------------------------------------

@dataclass
class NodeState:
    battery_wh: float
    alive: bool
    death_time: Optional[float]


@dataclass
class NodeOutput:
    node_id: str
    node_type: str
    time_series: List[float]
    battery_energy_series: List[float]
    battery_percent_series: List[float]
    alive_series: List[int]
    death_time: Optional[float]
    total_forwarded: int = 0
    total_retries: int = 0


def run_simulation(cfg: SimulationConfig) -> Dict[str, NodeOutput]:
    """
    Main simulation loop.

    Returns a dict keyed by node_id with per-node output data.
    """
    graph = cfg.graph

    if not graph.nodes:
        return {}

    graph.validate()

    # ---- initialise state ----
    state: Dict[str, NodeState] = {}
    for nid, node in graph.nodes.items():
        alive = node.battery_capacity_wh > 0
        state[nid] = NodeState(
            battery_wh=node.battery_capacity_wh if alive else 0.0,
            alive=alive,
            death_time=0.0 if not alive else None,
        )

    # ---- initialise output collectors ----
    outputs: Dict[str, NodeOutput] = {
        nid: NodeOutput(
            node_id=nid,
            node_type=graph.nodes[nid].node_type,
            time_series=[],
            battery_energy_series=[],
            battery_percent_series=[],
            alive_series=[],
            death_time=state[nid].death_time,
        )
        for nid in graph.nodes
    }

    # ---- group events by time bucket and node ----
    # events_by_node_step[(node_id, step_index)] = list[EventRecord]
    n_steps = math.ceil(cfg.total_time / cfg.time_step)

    def _step_index(t: float) -> int:
        return min(int(t / cfg.time_step), n_steps - 1)

    events_map: Dict[Tuple[str, int], List[EventRecord]] = {}
    for ev in cfg.events:
        key = (ev.node_id, _step_index(ev.time))
        events_map.setdefault(key, []).append(ev)

    topo_order = graph.topological_order()

    # ---- time loop ----
    for step in range(n_steps):
        t_start = step * cfg.time_step
        t_end = t_start + cfg.time_step
        t_mid = (t_start + t_end) / 2.0   # representative time for recording

        # Count transmissions bottom-up so relay nodes see correct n_rx
        # n_tx_this_step[node_id] = number of messages this node transmitted
        n_tx_this_step: Dict[str, int] = {nid: 0 for nid in graph.nodes}

        # Process in topological order (leaves first → roots last)
        for nid in topo_order:
            node = graph.nodes[nid]
            st = state[nid]

            if not st.alive:
                # Record dead-node state
                cap = node.battery_capacity_wh
                outputs[nid].time_series.append(t_mid)
                outputs[nid].battery_energy_series.append(0.0)
                outputs[nid].battery_percent_series.append(0.0)
                outputs[nid].alive_series.append(0)
                continue

            step_events = events_map.get((nid, step), [])
            n_local = len(step_events)
            n_cam = sum(1 for e in step_events if e.triggers_camera)

            if node.node_type == NODE_TYPE_SHAMAN_I:
                cfg_i: ShamanIPowerConfig = node.power_config  # type: ignore[assignment]
                n_tx = n_local  # each local event → one upward transmission
                dt = cfg.time_step
                T_proc_slp = max(0.0, dt - n_local * cfg_i.t_proc)
                T_mic_listen = dt
                T_mic_slp = 0.0
                T_cam_slp = max(0.0, dt - n_cam * cfg_i.t_cam_img)

                energy_used = _energy_shaman_i(
                    cfg_i,
                    n_local=n_local,
                    n_tx=n_tx,
                    n_cam=n_cam,
                    T_proc_slp=T_proc_slp,
                    T_mic_listen=T_mic_listen,
                    T_mic_slp=T_mic_slp,
                    T_cam_slp=T_cam_slp,
                )
                n_tx_this_step[nid] = n_tx if node.parent_id and state.get(node.parent_id, NodeState(0, False, None)).alive else 0

            elif node.node_type == NODE_TYPE_SHAMAN_II:
                cfg_ii: ShamanIIPowerConfig = node.power_config  # type: ignore[assignment]
                n_rx = sum(
                    n_tx_this_step[cid]
                    for cid in node.child_ids
                    if state[cid].alive
                )
                n_retry = cfg.n_retry_default
                dt = cfg.time_step
                active_time = (
                    n_local * cfg_ii.t_proc
                    + n_rx * cfg_ii.t_radio_rx
                    + (n_local + n_rx) * (cfg_ii.t_radio_tx * cfg_ii.f_hop)
                    + n_retry * (cfg_ii.t_radio_tx + cfg_ii.t_backoff)
                )
                T_idle = max(0.0, dt - active_time)

                energy_used = _energy_shaman_ii(
                    cfg_ii,
                    n_local=n_local,
                    n_rx=n_rx,
                    n_retry=n_retry,
                    T_idle=T_idle,
                )
                n_fwd = n_local + n_rx
                n_tx_this_step[nid] = n_fwd if node.parent_id and state.get(node.parent_id, NodeState(0, False, None)).alive else 0
                outputs[nid].total_forwarded += n_fwd
                outputs[nid].total_retries += n_retry

            else:
                # Command Center: no energy model (powered externally)
                energy_used = 0.0

            # ---- update battery ----
            # E_i(t+1) = max(0, E_i(t) − E_consumed)
            # B_i(t)   = E_i(t) / E_i_max · 100
            # a_i(t)   = 1 if E_i(t) > 0 else 0
            # t_death  = first t where E_i(t) ≤ 0
            st.battery_wh = max(0.0, st.battery_wh - energy_used)

            if st.battery_wh <= 0.0 and st.alive:
                st.alive = False
                st.death_time = t_end
                outputs[nid].death_time = t_end

            cap = node.battery_capacity_wh
            pct = (st.battery_wh / cap * 100.0) if cap > 0 else 0.0

            outputs[nid].time_series.append(t_mid)
            outputs[nid].battery_energy_series.append(round(st.battery_wh, 6))
            outputs[nid].battery_percent_series.append(round(pct, 4))
            outputs[nid].alive_series.append(1 if st.alive else 0)

    return outputs


# ---------------------------------------------------------------------------
# 5. Output Layer
# ---------------------------------------------------------------------------

def outputs_to_dict(outputs: Dict[str, NodeOutput]) -> dict:
    """Serialize simulation outputs to a JSON-serialisable dict."""
    result = {}
    for nid, out in outputs.items():
        result[nid] = {
            "node_id": out.node_id,
            "node_type": out.node_type,
            "time_series": out.time_series,
            "battery_energy_series": out.battery_energy_series,
            "battery_percent_series": out.battery_percent_series,
            "alive_series": out.alive_series,
            "death_time": out.death_time,
            "total_forwarded": out.total_forwarded,
            "total_retries": out.total_retries,
        }
    return result


def summary(outputs: Dict[str, NodeOutput]) -> dict:
    """Return optional summary statistics."""
    dead_nodes = {nid: out.death_time for nid, out in outputs.items() if out.death_time is not None}
    first_death_id = min(dead_nodes, key=lambda k: dead_nodes[k]) if dead_nodes else None

    energy_used = {}
    for nid, out in outputs.items():
        if out.battery_energy_series:
            cap = out.battery_energy_series[0]  # first recorded value ≈ initial
            # Re-derive from graph not available here; use delta approach
            pass  # placeholder – full accounting needs initial battery

    nodes_by_forwarded = sorted(
        outputs.items(), key=lambda kv: kv[1].total_forwarded, reverse=True
    )

    return {
        "first_node_to_die": first_death_id,
        "death_times": dead_nodes,
        "nodes_ranked_by_forwarded_load": [nid for nid, _ in nodes_by_forwarded],
        "total_retries_per_node": {nid: out.total_retries for nid, out in outputs.items()},
        "total_forwarded_per_node": {nid: out.total_forwarded for nid, out in outputs.items()},
    }


# ---------------------------------------------------------------------------
# Convenience: run from plain dicts (used by API routes)
# ---------------------------------------------------------------------------

def run_from_dict(payload: dict) -> dict:
    """
    Top-level entry point for the API.

    payload keys
    ------------
    - nodes           : list[dict]  (see build_graph_from_dict)
    - events          : list[dict]  {node_id, time, triggers_camera?}
    - total_time      : float       seconds
    - time_step       : float       seconds  (default 1.0)
    - n_retry_default : int         (default 0)
    """
    graph = build_graph_from_dict({"nodes": payload.get("nodes", [])})

    events = [
        EventRecord(
            node_id=ev["node_id"],
            time=float(ev["time"]),
            triggers_camera=ev.get("triggers_camera", False),
        )
        for ev in payload.get("events", [])
    ]

    cfg = SimulationConfig(
        graph=graph,
        events=events,
        total_time=float(payload["total_time"]),
        time_step=float(payload.get("time_step", 1.0)),
        n_retry_default=int(payload.get("n_retry_default", 0)),
    )

    outputs = run_simulation(cfg)
    return {
        "nodes": outputs_to_dict(outputs),
        "summary": summary(outputs),
    }
