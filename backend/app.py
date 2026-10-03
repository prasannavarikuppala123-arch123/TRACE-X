"""TRACE-X Flask API — incident priority, blast radius, and containment routes."""

from flask import Flask, jsonify, request
from flask_cors import CORS

from bfs import blast_radius
from data import RECONSTRUCTION_CLUES
from dijkstra import shortest_path
from graph import INFRA_GRAPH
from incident_manager import MANAGER

app = Flask(__name__)
CORS(app)


def error(message, status=400):
    return jsonify({"error": message}), status


@app.get("/api/incidents")
def get_incidents():
    pq = MANAGER.prioritize()
    return jsonify(
        {
            "incidents": MANAGER.list_incidents(),
            "priority_queue": pq,
            "compromised_systems": sorted(MANAGER.compromised),
        }
    )


@app.post("/api/incidents")
def post_incidents():
    payload = request.get_json(silent=True) or {}
    if "affected_system" not in payload and "incident_id" not in payload:
        return error("Provide incident_id or affected_system")
    incident = MANAGER.upsert_incident(payload)
    pq = MANAGER.prioritize()
    return jsonify({"incident": incident, "priority_queue": pq})


@app.post("/api/incidents/prioritize")
def post_prioritize():
    return jsonify(MANAGER.prioritize())


@app.get("/api/graph")
def get_graph():
    return jsonify(MANAGER.graph_payload())


@app.post("/api/blast-radius")
def post_blast_radius():
    payload = request.get_json(silent=True) or {}
    start = payload.get("start")
    if not start:
        return error("Missing start system")
    try:
        result = blast_radius(INFRA_GRAPH, start)
    except ValueError as exc:
        return error(str(exc))
    MANAGER.last_blast = result
    return jsonify(result)


@app.post("/api/shortest-path")
def post_shortest_path():
    payload = request.get_json(silent=True) or {}
    source = payload.get("source")
    target = payload.get("target")
    if not source or not target:
        return error("Missing source or target")
    try:
        result = shortest_path(INFRA_GRAPH, source, target)
    except ValueError as exc:
        return error(str(exc))
    MANAGER.last_path = result
    return jsonify(result)


@app.post("/api/compromise")
def post_compromise():
    payload = request.get_json(silent=True) or {}
    system = payload.get("system") or payload.get("start")
    if not system:
        return error("Missing system")
    if payload.get("clear"):
        return jsonify(MANAGER.uncompromise(system))
    try:
        result = MANAGER.mark_compromised(system, payload.get("incident_type"))
    except ValueError as exc:
        return error(str(exc))
    return jsonify(result)


@app.post("/api/reconstruct")
def post_reconstruct():
    payload = request.get_json(silent=True) or {}
    entry = payload.get("entry") or payload.get("start")
    incident_type = payload.get("incident_type", "Ransomware")
    if not entry:
        return error("Missing entry system")
    try:
        result = MANAGER.reconstruct(entry, incident_type)
    except ValueError as exc:
        return error(str(exc))
    return jsonify(result)


@app.get("/api/clues")
def get_clues():
    return jsonify({"clues": RECONSTRUCTION_CLUES})


if __name__ == "__main__":
    app.run(debug=True, port=5000, host="127.0.0.1")
