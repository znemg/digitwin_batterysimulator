# Graph-Based Python Simulation Program Command File

## Objective
Build a graph-based Python simulation program that models energy consumption and battery depletion across a Digital Twin sensor network using the finalized variables and equations from this project. The program should represent the system as a directed parent-child graph, simulate node-level activity over time, and generate battery-over-time outputs for each node.

## Purpose of the Program
The purpose of the program is to:

- simulate how energy is consumed by each node in the network over time
- model how local detections, message passing, forwarding, and retries affect battery drain
- capture the effect of graph structure on load accumulation, especially for relay nodes closer to the command center
- produce clean, structured battery-versus-time outputs that can be used later by the frontend for visualization
- identify node death times and possible energy bottlenecks in the network

The program is not meant to build the visualization itself. Its responsibility is to compute the data that the visualization will use.

## Program Structure
The program should be organized into clear components.

### 1. Graph / Topology Layer
Responsible for representing the network as a directed graph.

Each node should store:
- node id
- node type (`Shaman I`, `Shaman II`, or `Command Center`)
- coordinates
- parent id
- child ids
- rank
- battery capacity
- component power configuration

Each edge should represent a parent-child communication relationship.

### 2. Configuration Layer
Responsible for reading and normalizing user inputs from the simulator.

This layer should:
- load node-level power configuration values
- load battery capacities
- load topology information
- load event timeline data
- convert inputs into the internal variable format used by the simulation

### 3. Energy Model Layer
Responsible for applying the finalized equations for:
- Shaman I energy use
- Shaman II energy use
- receive/transmit costs
- retry costs
- battery updates

This layer should compute energy consumption from both:
- continuous activity states
- event-triggered actions

### 4. Simulation Engine
Responsible for iterating through time or events.

At each step, the engine should:
- process local detections
- propagate transmissions to parents
- update receive and forwarding counts
- compute energy consumed
- update remaining battery energy
- mark dead nodes
- record outputs

### 5. Output Layer
Responsible for exporting results in structured form.

The program should generate per-node outputs such as:
- time values
- remaining battery energy
- battery percentage
- node alive/dead state
- node death time

The output should be easy to export as JSON or CSV.

## Input
The program should accept the following inputs.

### A. Topology Input
Graph structure from the simulator:
- node ids
- node types
- coordinates
- parent-child connections
- ranks

### B. Power Configuration Input
Per-node component power values from the simulator UI.

For Shaman I, examples include:
- processor sleep
- processor working
- radio transmit
- radio receive
- camera image
- camera sleep
- mic listen
- mic sleep
- battery capacity

For Shaman II, use the configuration fields provided by its own UI.

### C. Event Input
Structured event timeline derived from uploaded media files.

Each event should include enough information for the simulation to determine:
- which node generated the event
- when the event occurred
- whether it causes processing, transmission, forwarding, or retry behavior

### D. Simulation Parameters
- total simulation time or run duration
- number of trials or runs
- timing assumptions not directly entered in the UI
- protocol constants such as frames per hop

## Output
The program should output simulation-ready data, not plots.

For each node, the output should include:
- `node_id`
- `node_type`
- `time_series`
- `battery_energy_series`
- `battery_percent_series`
- `alive_series`
- `death_time`

Optional summary outputs:
- first node to die
- nodes ranked by energy usage
- total forwarded load per node
- total retries per node

## Boundary Cases
The program should explicitly handle the following cases.

### 1. Empty Graph
If there are no nodes, return an empty output with a clear message.

### 2. Isolated Node
If a node has no parent or no valid communication path to the command center, the program should still simulate its local energy use but should mark that its data cannot propagate through the network.

### 3. Dead Node at Start
If a node starts with zero or negative battery capacity, mark it as dead immediately and exclude it from future communication.

### 4. Missing Power Fields
If required power configuration fields are missing, the program should raise a clear validation error instead of silently assuming values.

### 5. Missing Event Data
If a node has no events, the program should still simulate baseline or idle energy use over the run.

### 6. Parent Dies Before Child
If a parent node dies, child nodes may still consume local energy, but forwarding behavior should stop or be marked as failed because the communication path is broken.

### 7. Circular Graph Error
The graph must remain a directed acyclic routing structure toward the command center. If a cycle is detected, the program should stop and raise an error.

### 8. Multiple Children on One Relay
The program must correctly accumulate forwarding load from all children onto the relay node.

### 9. Battery Crossing Zero Mid-Step
If energy becomes negative during a step, clamp the remaining battery to zero and record the death time at that step.

### 10. Retry Explosion
If retry counts become extremely large, the program should still remain numerically stable and may optionally warn that the configuration is unrealistic.

## Scope Boundaries
The program should not:
- build frontend visualizations
- perform database writes
- infer AI events directly from raw audio/video
- optimize the network layout automatically
- model every real-world radio detail unless explicitly added later

For the MVP, the focus is:
- graph-based structure
- validated energy accounting
- battery-over-time outputs
- correct parent-child flow behavior

## Success Criteria
The program is successful if it:
- accepts graph and configuration inputs cleanly
- applies the finalized equations consistently
- tracks battery depletion for every node
- respects parent-child graph structure
- handles node death and broken paths correctly
- produces clean output data ready for downstream visualization and analysis

