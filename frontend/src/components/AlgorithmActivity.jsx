const ALGORITHMS = [
  {
    key: "priority",
    title: "Priority Queue",
    icon: "⚡",
    question: "What should we handle first?",
    description: "Selects the highest-priority incident using a max-priority heap.",
    empty: "Waiting for priority operations...",
  },
  {
    key: "bfs",
    title: "BFS",
    icon: "🕸️",
    question: "What is affected?",
    description: "Explores connected systems level-by-level to determine the blast radius.",
    empty: "Waiting for BFS traversal...",
  },
  {
    key: "dijkstra",
    title: "Dijkstra",
    icon: "🛡️",
    question: "How do we contain it?",
    description: "Finds the minimum-cost containment route through the infrastructure graph.",
    empty: "Waiting for shortest-path calculation...",
  },
];

export default function AlgorithmActivity({ logs }) {
  return (
    <section className="panel activity">
      <div className="panel-head">
        <div>
          <h2>06 // Algorithm Activity</h2>
          <p className="hint">
            TRACE-X exposes the decisions made by each DAA algorithm.
          </p>
        </div>
      </div>

      <div className="log-grid">
        {ALGORITHMS.map((algorithm) => {
          const entries = logs?.[algorithm.key];

          return (
            <article className="algorithm-card" key={algorithm.key}>
              <div className="algorithm-title">
                <span className="algorithm-icon">{algorithm.icon}</span>
                <div>
                  <h3>{algorithm.title}</h3>
                  <span className="algorithm-question">
                    {algorithm.question}
                  </span>
                </div>
              </div>

              <p className="algorithm-description">
                {algorithm.description}
              </p>

              <div className="algorithm-flow">
                <span>INPUT</span>
                <span>→</span>
                <strong>{algorithm.title}</strong>
                <span>→</span>
                <span>DECISION</span>
              </div>

              <div className="algorithm-log">
                <pre>
                  {(entries?.length ? entries : [algorithm.empty]).join("\n")}
                </pre>
              </div>

              {entries?.length > 0 && (
                <div className="execution-status">
                  ✓ Algorithm executed
                </div>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}