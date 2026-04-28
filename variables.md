# Digital Twin Energy Model

---

## 1. System Overview

The system is modeled as a directed graph:

$$
G = (\mathcal{N}, \mathcal{E})
$$

- \( \mathcal{N} ): set of nodes  
- \( \mathcal{E} ): communication links  

Each node:

$$
i \in \mathcal{N}
$$

$$
\text{type}(i) \in \{\text{Shaman I}, \text{Shaman II}, \text{Command Center}\}
$$

**Explanation:**  
Defines all devices in the system and their roles.

---

## 2. Topology Variables

$$
(x_i, y_i)
$$
**→ Coordinates of node \( i \)** (used for layout, distance, and topology construction)

$$
p(i)
$$
**→ Parent node of \( i \)** (the node it sends data to)

$$
\mathcal{C}(i)
$$
**→ Set of children of node \( i \)** (nodes that send data to it)

$$
r_i
$$
**→ Rank of node \( i \)** (number of hops to the command center)

$$
i \rightarrow p(i)
$$
**→ Direction of data flow** (always toward the parent / gateway)

---

## 3. Battery Variables

$$
E_i^{\max}
$$
**→ Maximum battery energy (Wh)** (directly from user input)

$$
E_i(t)
$$
**→ Remaining battery energy at time \( t \)**

$$
B_i(t) = \frac{E_i(t)}{E_i^{\max}} \cdot 100
$$
**→ Battery percentage at time \( t \)**

$$
t_i^{\text{death}} = \min \{ t \mid E_i(t) \le 0 \}
$$
**→ Time when battery is depleted**

$$
a_i(t) =
\begin{cases}
1, & E_i(t) > 0 \\
0, & E_i(t) \le 0
\end{cases}
$$
**→ Node alive indicator (1 = alive, 0 = dead)**

---

## 4. Shaman I Variables (Sensor Node)

### Power Variables (from UI)

$$
P^{(I)}_{\text{proc,slp}}
$$
**→ Power when processor is sleeping**

$$
P^{(I)}_{\text{proc,wrk}}
$$
**→ Power when processor is actively processing events**

$$
P^{(I)}_{\text{radio,tx}}
$$
**→ Power used during radio transmission**

$$
P^{(I)}_{\text{radio,rx}}
$$
**→ Power used during radio receiving (future use)**

$$
P^{(I)}_{\text{cam,img}}
$$
**→ Power when camera captures an image**

$$
P^{(I)}_{\text{cam,slp}}
$$
**→ Power when camera is idle/sleeping**

$$
P^{(I)}_{\text{mic,listen}}
$$
**→ Power when microphone is actively listening**

$$
P^{(I)}_{\text{mic,slp}}
$$
**→ Power when microphone is in sleep mode**



### Time Variables

$$
t^{(I)}_{\text{proc}}
$$
**→ Time to process one detected event**

$$
t^{(I)}_{\text{radio,tx}}
$$
**→ Time required to transmit one message**

$$
t^{(I)}_{\text{radio,rx}}
$$
**→ Time required to receive one message**

$$
t^{(I)}_{\text{cam,img}}
$$
**→ Time to capture/process one image**

$$
T^{(I)}_{\text{proc,slp}}
$$
**→ Total processor idle time**

$$
T^{(I)}_{\text{mic,listen}}
$$
**→ Total microphone listening duration**

$$
T^{(I)}_{\text{mic,slp}}
$$
**→ Total microphone sleep duration**

$$
T^{(I)}_{\text{cam,slp}}
$$
**→ Total camera idle time**



### Event Variables

$$
n^{(I)}_{\text{local}}
$$
**→ Number of events detected locally**

$$
n^{(I)}_{\text{tx}}
$$
**→ Number of transmissions sent to parent node**

$$
n^{(I)}_{\text{cam}}
$$
**→ Number of camera-triggered events**

---

## 5. Shaman II Variables (Relay Node)

### Power Variables

$$
P^{(II)}_{\text{proc,act}}
$$
**→ Power when main processor is actively working**

$$
P^{(II)}_{\text{proc,slp}}
$$
**→ Power when processor is idle**

$$
P^{(II)}_{\text{ctrl,act}}
$$
**→ Power of controller when active**

$$
P^{(II)}_{\text{ctrl,slp}}
$$
**→ Power of controller when idle**

$$
P^{(II)}_{\text{radio,tx}}
$$
**→ Power used for transmitting messages**

$$
P^{(II)}_{\text{radio,rx}}
$$
**→ Power used for receiving messages**

$$
P^{(II)}_{\text{backoff}}
$$
**→ Power consumed while waiting during retry backoff**



### Time Variables

$$
t^{(II)}_{\text{proc}}
$$
**→ Time to process one event**

$$
t^{(II)}_{\text{radio,tx}}
$$
**→ Time to transmit one message**

$$
t^{(II)}_{\text{radio,rx}}
$$
**→ Time to receive one message**

$$
t_{\text{backoff}}
$$
**→ Waiting time before retrying transmission**



### Event Variables

$$
n^{(II)}_{\text{local}}
$$
**→ Events generated locally at Shaman II**

$$
n^{(II)}_{\text{rx}} = \sum_{j \in \mathcal{C}(i)} n^{(j)}_{\text{tx}}
$$
**→ Total events received from all child nodes**

$$
n^{(II)}_{\text{fwd}} = n^{(II)}_{\text{local}} + n^{(II)}_{\text{rx}}
$$
**→ Total events forwarded upward**

$$
n^{(II)}_{\text{retry}}
$$
**→ Number of retransmission attempts due to failure**

---

## 6. Communication Variable

$$
f_{\text{hop}}
$$
**→ Number of frames required per transmission hop (protocol overhead)**

---

## 7. Energy Equations

### General

$$
E = P \cdot t
$$
**→ Energy equals power times duration**

$$
E = n \cdot P \cdot t
$$
**→ For repeated events**



### Shaman I Energy

$$
E^{(I)} = E^{(I)}_{\text{proc}} + E^{(I)}_{\text{radio}} + E^{(I)}_{\text{mic}} + E^{(I)}_{\text{cam}}
$$



#### Processor

$$
E^{(I)}_{\text{proc}} =
n^{(I)}_{\text{local}} P^{(I)}_{\text{proc,wrk}} t^{(I)}_{\text{proc}}
+
P^{(I)}_{\text{proc,slp}} T^{(I)}_{\text{proc,slp}}
$$



#### Radio

$$
E^{(I)}_{\text{radio}} =
n^{(I)}_{\text{tx}} P^{(I)}_{\text{radio,tx}} t^{(I)}_{\text{radio,tx}}
$$



#### Microphone

$$
E^{(I)}_{\text{mic}} =
P^{(I)}_{\text{mic,listen}} T^{(I)}_{\text{mic,listen}}
+
P^{(I)}_{\text{mic,slp}} T^{(I)}_{\text{mic,slp}}
$$



#### Camera

$$
E^{(I)}_{\text{cam}} =
n^{(I)}_{\text{cam}} P^{(I)}_{\text{cam,img}} t^{(I)}_{\text{cam,img}}
+
P^{(I)}_{\text{cam,slp}} T^{(I)}_{\text{cam,slp}}
$$



### Shaman II Energy

$$
E^{(II)} =
E^{(II)}_{\text{idle}} +
E^{(II)}_{\text{rx}} +
E^{(II)}_{\text{proc}} +
E^{(II)}_{\text{tx}} +
E^{(II)}_{\text{retry}}
$$



#### Idle

$$
E^{(II)}_{\text{idle}} =
\left(
P^{(II)}_{\text{proc,slp}} +
P^{(II)}_{\text{ctrl,slp}} +
P^{(II)}_{\text{radio,rx}}
\right) T^{(II)}_{\text{idle}}
$$



#### Receive

$$
E^{(II)}_{\text{rx}} =
n^{(II)}_{\text{rx}} P^{(II)}_{\text{radio,rx}} t^{(II)}_{\text{radio,rx}}
$$



#### Processing

$$
E^{(II)}_{\text{proc}} =
n^{(II)}_{\text{fwd}} P^{(II)}_{\text{proc,act}} t^{(II)}_{\text{proc}}
$$


#### Transmission

$$
E^{(II)}_{\text{tx}} =
n^{(II)}_{\text{fwd}} P^{(II)}_{\text{radio,tx}} t^{(II)}_{\text{radio,tx}} f_{\text{hop}}
$$


#### Retry

$$
E^{(II)}_{\text{retry}} =
n^{(II)}_{\text{retry}} \cdot
\left(
P^{(II)}_{\text{radio,tx}} t^{(II)}_{\text{radio,tx}} +
P^{(II)}_{\text{backoff}} t_{\text{backoff}}
\right)
$$

---

## 8. Network Flow Constraint

$$
n^{(i)}_{\text{fwd}} =
n^{(i)}_{\text{local}} +
\sum_{j \in \mathcal{C}(i)} n^{(j)}_{\text{tx}}
$$

**→ Data accumulates as it moves toward the command center**

---

## 9. Key Insight

$$
r_i \downarrow \Rightarrow n^{(i)}_{\text{fwd}} \uparrow \Rightarrow E^{(i)} \uparrow
$$

**→ Nodes closer to the gateway consume more energy and fail earlier**