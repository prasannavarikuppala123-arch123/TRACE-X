export default function ContainmentRoute({ route }) {
  const path = route?.path || [];

  return (
    <section className="panel containment">
      <div className="panel-head">
        <div>
          <h2>05 // Containment Route</h2>
          <p className="hint">
            Dijkstra finds the minimum-cost route to contain the incident.
          </p>
        </div>
      </div>

      {!path.length && (
        <div className="empty-state">
          <span>🛡️</span>
          <p>
            Run Dijkstra to calculate the safest minimum-cost containment path.
          </p>
        </div>
      )}

      {!!path.length && (
        <>
          <div className="route-heading">
            <span>🛡️ SELECTED CONTAINMENT PATH</span>
            <strong>DIJKSTRA</strong>
          </div>

          <ol className="route">
            {path.map((node, i) => (
              <li key={`${node}-${i}`}>
                <span className="role">
                  {i === 0
                    ? "SOURCE"
                    : i === path.length - 1
                      ? "TARGET"
                      : "SYSTEM"}
                </span>

                <strong>{node}</strong>

                {i < path.length - 1 && (
                  <span className="route-arrow">↓</span>
                )}
              </li>
            ))}
          </ol>

          <div className="metrics">
            <div>
              <span>Total Cost</span>
              <strong>{route.total_cost}</strong>
            </div>

            <div>
              <span>Nodes Visited</span>
              <strong>{route.visited_nodes?.length ?? 0}</strong>
            </div>

            <div>
              <span>Algorithm</span>
              <strong>✓ Dijkstra</strong>
            </div>
          </div>

          <div className="route-result">
            ✓ Minimum-cost containment route selected
          </div>
        </>
      )}
    </section>
  );
}