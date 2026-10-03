const TONE = {
  Critical: "critical",
  High: "high",
  Medium: "medium",
  Low: "low",
};

export default function ActiveIncidents({ incidents }) {
  return (
    <section className="panel">
      <div className="panel-head">
        <h2>01 // Active Incidents</h2>
        <span className="count">{incidents.length} live</span>
      </div>

      <div className="incident-grid">
        {incidents.map((inc) => (
          <article
            key={inc.incident_id}
            className={`incident-card ${TONE[inc.severity] || "low"}`}
          >
            <div className="card-top">
              <span className="sev-pill">{inc.severity}</span>
              <span className="mono">{inc.incident_id}</span>
            </div>

            <h3>{inc.incident_type}</h3>

            <p>
              Affected: <strong>{inc.affected_system}</strong>
            </p>

            <p>Status: {inc.status}</p>

            <div className="score-display">
              <span>Priority Score</span>
              <strong>
                ⚡ {inc.priority_score}/10
              </strong>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}