# Smart Traffic Management System

**Team वेग 1 (VEIG_1) — Smart India Hackathon 2025**

A reinforcement-learning-based traffic signal control system that dynamically optimizes signal timing in real time, cutting average intersection wait times by over 58% against a fixed-time baseline.

**Demo video:** _coming soon_

---

## Overview

Fixed-interval traffic signals don't account for real-time traffic density, which leads to unnecessary congestion — especially at intersections with uneven or unpredictable traffic flow. This project builds a Double Deep Q-Network (D-DQN) reinforcement learning agent that observes live traffic state and dynamically chooses signal phases to minimize wait time, tested across two network topologies: a single intersection and an urban arterial grid.

The project was built as a Smart India Hackathon 2025 entry by Team वेग 1, was selected for SIH 2025, and was later developed further into a peer-reviewed published research paper.

## Results

- **58.3%** reduction in average waiting time on a single intersection
- **43.8%** speed improvement on a single intersection
- **12.3%** wait-time reduction on an urban arterial grid

These results come from a dual parallel simulation setup — one simulation instance controlled by the RL agent, one by fixed-time logic — run under identical traffic conditions, so the comparison is unbiased.

## What it does

- **D-DQN reinforcement learning agent** — trained to select traffic signal phases based on real-time lane-level traffic state, rather than fixed timers.
- **Dual parallel simulation** — runs an RL-controlled simulation alongside a fixed-time baseline simultaneously, under identical conditions, for a fair real-time comparison.
- **Emergency vehicle detection with signal preemption** — the system detects emergency vehicles and preempts normal signal logic to clear their path.
- **Live monitoring dashboard** — a real-time dashboard streams simulation state over WebSocket so traffic conditions and signal decisions can be observed as they happen.

## Architecture

- **Simulation** — built on SUMO (Simulation of Urban MObility) with the TraCI interface, providing the traffic environment the RL agent trains and operates in.
- **RL agent** — a PyTorch-based D-DQN model observes traffic state and outputs signal phase decisions.
- **Backend** — a FastAPI server bridges the SUMO/TraCI simulation and the RL agent to the frontend, streaming live state over WebSocket.
- **Frontend** — a React dashboard visualizes the simulation and signal decisions in real time.

```
SUMO + TraCI (traffic simulation)
        │
        ▼
  D-DQN Agent (PyTorch)
        │
        ▼
 FastAPI Backend  ──WebSocket──▶  React Dashboard
```

## Tech Stack

| Layer | Technology |
|---|---|
| Simulation | SUMO, TraCI |
| RL / ML | Python, PyTorch |
| Backend | FastAPI, WebSocket |
| Frontend | React |

## Engineering notes

- A D-DQN agent was chosen over hand-tuned heuristics so the system could learn from actual traffic patterns instead of relying on fixed rules that don't generalize across intersections.
- The dual parallel simulation architecture was key to making the results credible — running the RL policy and the fixed-time baseline on identical, synchronized traffic conditions removes the bias that would come from comparing runs at different times or under different traffic loads.
- Emergency vehicle preemption had to be layered on top of the learned policy without conflicting with it — a real-world constraint that a pure RL approach doesn't handle on its own.
- WebSocket streaming was used for the monitoring dashboard instead of polling, so signal decisions and traffic state could be observed with minimal delay.

## Project structure

```
smart_traffic_managements_SIH/
├── backend/         # FastAPI server, WebSocket streaming, RL agent integration
├── frontend/        # React monitoring dashboard
├── sumo_network/    # SUMO network topology and simulation config
├── test_sumo.py     # SUMO/TraCI integration test script
└── FRONTEND_SETUP.md
```

## Background

Built by Team वेग 1 for Smart India Hackathon 2025, where the project was selected at the college level. The idea was later developed into a final-year engineering project and published as peer-reviewed research: *"Adaptive Urban Traffic Signal Optimization Using Reinforcement Learning: A D-DQN Approach"* — International Journal of Innovative Research in Technology (IJIRT), Vol. 12, Issue 11, April 2026.

---

Built by [Sumedh Gaikwad](https://github.com/SumedhGaikwad03) — [Portfolio](https://sumedh-portfolio-cyan.vercel.app/)
