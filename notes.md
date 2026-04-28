# Notes & Modeling Decisions

## 1. Event-Driven vs Time-Driven

- Prefer event-driven simulation
- Events trigger:
    - processing
    - transmission
    - reception

- Idle power fills gaps between events

---

## 2. Separation of Concerns

Split energy into:
- baseline (continuous)
- event-based (discrete)

---

## 3. Shaman I vs Shaman II

Shaman I:
- only detects + sends
- no receiving
- simpler model

Shaman II:
- receives + processes + forwards
- heavier energy load
- bottleneck near gateway

---

## 4. Communication Types

WiFi:
- short range
- used between Shaman I → II

LoRa:
- long range
- used between Shaman II nodes

---

## 5. frames_per_hop

- NOT a timing variable
- multiplier on transmission cost

---

## 6. Battery Modeling

Track:
- energy remaining
- percent remaining
- death time

Dead nodes:
- stop transmitting
- stop receiving
- removed from simulation flow

---

## 7. Simplifications (MVP)

- Ignore radio sleep (for now)
- No packet loss modeling (yet)
- Fixed transmission times
- Fixed retry count (or simple model)

---

## 8. Future Extensions

- duty cycling (LoRa sleep/wake)
- dynamic routing
- congestion modeling
- packet collisions
- adaptive transmission power