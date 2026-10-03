# TRACE-X

Intelligent Cyber Incident Response & Containment — a DAA hackathon MVP.

The prototype **prioritizes incidents** (heap-based priority queue), **traces blast radius** (BFS on the dependency graph), and **computes a minimum-cost containment route** (Dijkstra). Algorithm results are computed at request time; they are not hard-coded.

## Stack

- Backend: Python, Flask (in-memory JSON / dicts, no database)
- Frontend: React + Vite

## Setup

### 1. Backend

```bash
cd backend
python -m pip install -r requirements.txt
python app.py
```

API listens on `http://127.0.0.1:5000`.

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL (default `http://127.0.0.1:5173`). Frontend `/api` calls are proxied to Flask.

## Demo sequence

1. Dashboard loads three incidents (Ransomware / Data Breach / Phishing).
2. Priority queue selects **INC-001** (Critical, score 10) as **NEXT RESPONSE**.
3. Mark **Employee-PC** as compromised.
4. BFS computes the attack blast radius and levels.
5. Critical assets inside the affected set are highlighted (Database, Backup Server, Firewall, SOC).
6. Run Dijkstra from **SOC** to **Employee-PC** for the containment route.
7. In **Incident Reconstruction**, pick the Employee-PC clue to generate the full response plan.

## Algorithms

| Algorithm | File | Used for |
| --- | --- | --- |
| Priority Queue (`heapq` max-heap via negated scores) | `backend/priority_queue.py` | Incident response order |
| BFS | `backend/bfs.py` | Blast radius from a compromised system |
| Dijkstra | `backend/dijkstra.py` | Lowest-cost containment path (undirected travel on weighted links) |

BFS follows **directed** dependency edges (how compromise can spread). Dijkstra uses the **same edges in both directions** so responders can travel a link either way.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/incidents` | List incidents and current queue |
| POST | `/api/incidents` | Create or update an incident (change priority/severity) |
| POST | `/api/incidents/prioritize` | Rebuild heap and return next incident |
| GET | `/api/graph` | Nodes, edges, states |
| POST | `/api/blast-radius` | `{ "start": "Employee-PC" }` |
| POST | `/api/shortest-path` | `{ "source": "SOC", "target": "Employee-PC" }` |
| POST | `/api/compromise` | `{ "system": "Employee-PC" }` — BFS + priority update |
| POST | `/api/reconstruct` | `{ "entry": "Employee-PC", "incident_type": "Ransomware" }` |

## Project layout

```text
TRACE-X/
├── backend/
│   ├── app.py
│   ├── graph.py
│   ├── bfs.py
│   ├── dijkstra.py
│   ├── priority_queue.py
│   ├── incident_manager.py
│   └── data.py
├── frontend/
└── README.md
```

Edit systems and weighted edges in `backend/data.py` (`SYSTEMS` and `DIRECTED_EDGES`).
