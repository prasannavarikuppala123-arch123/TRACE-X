import { useCallback, useEffect, useMemo, useState } from "react";
import ActiveIncidents from "./components/ActiveIncidents.jsx";
import AlgorithmActivity from "./components/AlgorithmActivity.jsx";
import ContainmentRoute from "./components/ContainmentRoute.jsx";
import ExplainPanel from "./components/ExplainPanel.jsx";
import PriorityQueuePanel from "./components/PriorityQueuePanel.jsx";
import Reconstruction from "./components/Reconstruction.jsx";
import SystemGraph from "./components/SystemGraph.jsx";

async function api(path, options) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.error || `Request failed: ${path}`);
  }

  return data;
}

export default function App() {
  const [incidents, setIncidents] = useState([]);
  const [queue, setQueue] = useState(null);
  const [graph, setGraph] = useState(null);
  const [blast, setBlast] = useState(null);
  const [route, setRoute] = useState(null);
  const [reconstruction, setReconstruction] = useState(null);
  const [clues, setClues] = useState([]);

  const [startNode, setStartNode] = useState("Employee-PC");
  const [incidentType, setIncidentType] = useState("Ransomware");

  const [source, setSource] = useState("SOC");
  const [target, setTarget] = useState("Employee-PC");

  const [error, setError] = useState("");

  const [detectedIncident, setDetectedIncident] = useState(null);
  const [scoreExplanation, setScoreExplanation] = useState(null);

  const [logs, setLogs] = useState({
    priority: [],
    bfs: [],
    dijkstra: [],
  });

  const systems = useMemo(
    () => (graph?.nodes || []).map((n) => n.id),
    [graph]
  );

  const refreshGraph = useCallback(async () => {
    const g = await api("/api/graph");
    setGraph(g);
  }, []);

  const loadBase = useCallback(async () => {
    const [inc, clueData, g] = await Promise.all([
      api("/api/incidents"),
      api("/api/clues"),
      api("/api/graph"),
    ]);

    setIncidents(inc.incidents);
    setQueue(inc.priority_queue);

    setLogs((prev) => ({
      ...prev,
      priority: inc.priority_queue.steps,
    }));

    setClues(clueData.clues);
    setGraph(g);
  }, []);

  useEffect(() => {
    loadBase().catch((err) => setError(err.message));
  }, [loadBase]);

  async function prioritize() {
    const data = await api("/api/incidents/prioritize", {
      method: "POST",
      body: "{}",
    });

    setQueue(data);

    setLogs((prev) => ({
      ...prev,
      priority: data.steps,
    }));
  }

  async function runBlast() {
    const data = await api("/api/blast-radius", {
      method: "POST",
      body: JSON.stringify({
        start: startNode,
      }),
    });

    setBlast(data);

    setLogs((prev) => ({
      ...prev,
      bfs: data.steps,
    }));

    await refreshGraph();
  }

  async function runDijkstra() {
    const data = await api("/api/shortest-path", {
      method: "POST",
      body: JSON.stringify({
        source,
        target,
      }),
    });

    setRoute(data);

    setLogs((prev) => ({
      ...prev,
      dijkstra: data.steps,
    }));

    await refreshGraph();
  }

  // AUTOMATIC INCIDENT DETECTION + PRIORITY
  async function compromise() {
    try {
      setError("");

      const data = await api("/api/compromise", {
        method: "POST",
        body: JSON.stringify({
          system: startNode,
          incident_type: incidentType,
        }),
      });

      setBlast(data.blast_radius);
      setQueue(data.priority_queue);

      // Detected incident
      setDetectedIncident(data.incident);

      // Automatic score explanation
      setScoreExplanation(data.score_explanation);

      const inc = await api("/api/incidents");
      setIncidents(inc.incidents);

      setLogs((prev) => ({
        ...prev,
        bfs: data.blast_radius.steps,
        priority: data.priority_queue.steps,
      }));

      await refreshGraph();
    } catch (err) {
      setError(err.message);
    }
  }

  async function reconstruct(entry, type) {
    try {
      setError("");

      const data = await api("/api/reconstruct", {
        method: "POST",
        body: JSON.stringify({
          entry,
          incident_type: type,
        }),
      });

      setReconstruction(data);
      setBlast(data.blast_radius);
      setRoute(data.containment);
      setQueue(data.priority_queue);

      setDetectedIncident(data.incident);
      setScoreExplanation(null);

      setStartNode(entry);
      setTarget(entry);

      setLogs({
        priority: data.priority_queue.steps,
        bfs: data.blast_radius.steps,
        dijkstra: data.containment.steps,
      });

      const inc = await api("/api/incidents");
      setIncidents(inc.incidents);

      await refreshGraph();
    } catch (err) {
      setError(err.message);
    }
  }

  const explanations = [
    queue?.explanation,
    blast?.explanation,
    route?.explanation,
  ];

  return (
    <div className="app">

      {/* HEADER */}
      <header className="hero">
        <div>
          <p className="kicker">SOC CONTROL ROOM</p>

          <h1>TRACE-X</h1>

          <p className="tag">
            Intelligent Cyber Incident Response &amp; Containment
          </p>

          <p className="motto">
            Prioritize • Trace • Contain
          </p>
        </div>

        <div className="pipeline">
          <div>
            <strong>PRIORITY QUEUE</strong>
            <span>What first?</span>
          </div>

          <div>
            <strong>BFS</strong>
            <span>What is affected?</span>
          </div>

          <div>
            <strong>DIJKSTRA</strong>
            <span>How do we contain it?</span>
          </div>
        </div>
      </header>

      {/* ERROR */}
      {error && (
        <div className="banner">
          {error} — start Flask on port 5000.
        </div>
      )}

      {/* CONTROLS */}
      <section className="controls">

        <label>
          Compromised / BFS origin

          <select
            value={startNode}
            onChange={(e) => setStartNode(e.target.value)}
          >
            {systems.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </label>

        <label>
          Incident Type

          <select
            value={incidentType}
            onChange={(e) => setIncidentType(e.target.value)}
          >
            <option>Ransomware</option>
            <option>Data Breach</option>
            <option>Malware</option>
            <option>Unauthorized Access</option>
            <option>Phishing</option>
          </select>
        </label>

        <button
          type="button"
          className="danger"
          onClick={compromise}
        >
          Detect Incident &amp; Calculate Priority
        </button>

        <button
          type="button"
          onClick={() =>
            runBlast().catch((e) => setError(e.message))
          }
        >
          Run BFS blast radius
        </button>

        <label>
          Dijkstra source

          <select
            value={source}
            onChange={(e) => setSource(e.target.value)}
          >
            {systems.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </label>

        <label>
          Dijkstra target

          <select
            value={target}
            onChange={(e) => setTarget(e.target.value)}
          >
            {systems.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </label>

        <button
          type="button"
          onClick={() =>
            runDijkstra().catch((e) => setError(e.message))
          }
        >
          Run Dijkstra
        </button>

      </section>

      {/* AUTOMATIC PRIORITY RESULT */}
      {detectedIncident && (
        <section className="panel">

          <div className="panel-head">
            <h2>⚡ AUTOMATIC PRIORITY RESULT</h2>

            <span className="count">
              Automatically calculated
            </span>
          </div>

          <p>
            Incident:{" "}
            <strong>{detectedIncident.incident_type}</strong>
          </p>

          <p>
            Affected System:{" "}
            <strong>{detectedIncident.affected_system}</strong>
          </p>

          <p>
            Priority Score:{" "}
            <strong>
              {detectedIncident.priority_score}/10
            </strong>
          </p>

          <p>
            Severity:{" "}
            <strong>{detectedIncident.severity}</strong>
          </p>

          {scoreExplanation && (
            <div className="score-explanation">

              <h3>WHY THIS SCORE?</h3>

              <ul>
                <li>
                  Base score:{" "}
                  <strong>
                    {scoreExplanation.base_score}
                  </strong>
                </li>

                <li>
                  BFS affected systems:{" "}
                  <strong>
                    {scoreExplanation.affected_systems}
                  </strong>
                </li>

                <li>
                  Critical assets at risk:{" "}
                  <strong>
                    {scoreExplanation.critical_assets?.length
                      ? scoreExplanation.critical_assets.join(", ")
                      : "None"}
                  </strong>
                </li>

                <li>
                  Impact bonus:{" "}
                  <strong>
                    +{scoreExplanation.impact_bonus}
                  </strong>
                </li>
              </ul>

              <p className="therefore">
                {scoreExplanation.reason}
              </p>

            </div>
          )}

        </section>
      )}

      {/* ACTIVE INCIDENTS */}
      <ActiveIncidents incidents={incidents} />

      {/* PRIORITY QUEUE */}
      <PriorityQueuePanel
        queue={queue}
        onRefresh={() =>
          prioritize().catch((e) => setError(e.message))
        }
      />

      {/* SYSTEM GRAPH */}
      <SystemGraph
        graph={graph}
        highlightOrder={blast?.traversal_order || []}
      />

      {/* BFS RESULT */}
      {blast && (
        <section className="panel">

          <div className="panel-head">
            <h2>BFS Blast Radius</h2>

            <span className="count">
              {blast.affected_count} potentially affected
            </span>
          </div>

          <p>
            Compromised origin:{" "}
            <strong>{blast.start}</strong>
          </p>

          <p>
            Traversal order:{" "}
            {blast.traversal_order.join(" → ")}
          </p>

          <div className="levels">
            {Object.entries(blast.levels).map(
              ([level, nodes]) => (
                <div key={level}>
                  <h4>Level {level}</h4>
                  <p>{nodes.join(", ")}</p>
                </div>
              )
            )}
          </div>

        </section>
      )}

      {/* INCIDENT RECONSTRUCTION */}
      <Reconstruction
        systems={systems}
        clues={clues}
        result={reconstruction}
        onReconstruct={(entry, type) =>
          reconstruct(entry, type).catch((e) =>
            setError(e.message)
          )
        }
      />

      {/* CONTAINMENT */}
      <ContainmentRoute route={route} />

      {/* ALGORITHM ACTIVITY */}
      <AlgorithmActivity logs={logs} />

      {/* EXPLANATION */}
      <ExplainPanel explanations={explanations} />

    </div>
  );
}