const LAYOUT = {
  SOC: { x: 8, y: 18 },
  Firewall: { x: 24, y: 18 },
  VPN: { x: 42, y: 18 },
  "Internal Network": { x: 62, y: 18 },
  "Web Server": { x: 80, y: 8 },
  "Application Server": { x: 80, y: 28 },
  Database: { x: 94, y: 22 },
  "Employee-PC": { x: 42, y: 52 },
  "Mail Server": { x: 58, y: 58 },
  "File Server": { x: 80, y: 52 },
  "Backup Server": { x: 94, y: 48 },
};

export default function SystemGraph({ graph, highlightOrder = [] }) {
  const nodes = graph?.nodes || [];
  const edges = graph?.edges || [];
  const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));
  const highlightIndex = Object.fromEntries(highlightOrder.map((id, i) => [id, i]));

  return (
    <section className="panel graph-panel">
     <div className="panel-head">
  <div>
    <h2>03 // System Dependency Graph</h2>
    <p className="hint">
      Infrastructure represented as a weighted graph for BFS impact analysis
      and Dijkstra containment routing.
    </p>
  </div>

  <div className="legend">
          <span><i className="dot compromised" /> Compromised</span>
          <span><i className="dot affected" /> Potentially affected</span>
          <span><i className="dot safe" /> Safe</span>
          <span><i className="dot inactive" /> Inactive</span>
        </div>
      </div>
      <svg viewBox="0 0 100 70" className="infra-svg" role="img" aria-label="Infrastructure graph">
        {edges.map((edge) => {
          const a = LAYOUT[edge.source];
          const b = LAYOUT[edge.target];
          if (!a || !b) return null;
          const onPath = byId[edge.source]?.on_path && byId[edge.target]?.on_path;
          return (
            <g key={`${edge.source}-${edge.target}`}>
              <line
                x1={a.x}
                y1={a.y}
                x2={b.x}
                y2={b.y}
                className={onPath ? "edge path" : "edge"}
              />
              <text x={(a.x + b.x) / 2} y={(a.y + b.y) / 2 - 1.6} className="edge-cost">
                {edge.cost}
              </text>
            </g>
          );
        })}
        {nodes.map((node) => {
          const pos = LAYOUT[node.id] || { x: 50, y: 35 };
          const idx = highlightIndex[node.id];
          return (
            <g key={node.id} className={`node-group ${node.state} ${node.on_path ? "on-path" : ""}`}>
              <circle cx={pos.x} cy={pos.y} r={node.critical ? 4.2 : 3.6} />
              <text x={pos.x} y={pos.y + 7} textAnchor="middle" className="node-label">
                {node.id}
                {node.critical ? " ★" : ""}
              </text>
              {idx !== undefined && (
                <text x={pos.x} y={pos.y + 0.8} textAnchor="middle" className="visit-idx">
                  {idx}
                </text>
              )}
            </g>
          );
        })}
      </svg>
    </section>
  );
}
