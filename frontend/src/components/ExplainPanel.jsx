export default function ExplainPanel({ explanations }) {
  const blocks = explanations.filter(Boolean);

  if (!blocks.length) {
    return null;
  }

  return (
    <section className="panel explain">
      <div className="panel-head">
        <div>
          <h2>07 // Explainable Decision Panel</h2>
          <p className="hint">
            TRACE-X shows why each response decision was made.
          </p>
        </div>
      </div>

      <div className="explain-grid">
        {blocks.map((block, index) => (
          <article key={`${block.title}-${index}`} className="explain-card">
            <div className="decision-label">
              STEP {index + 1}
            </div>

            <h3>{block.title}</h3>

            <div className="evidence">
              <span className="evidence-title">EVIDENCE</span>

              <ul>
                {(block.lines || []).map((line, lineIndex) => (
                  <li key={`${line}-${lineIndex}`}>{line}</li>
                ))}
              </ul>
            </div>

            <div className="decision-result">
              <span>DECISION</span>
              <p>{block.therefore}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}