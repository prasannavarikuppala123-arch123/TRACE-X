const MEDALS = ["🥇", "🥈", "🥉"];

export default function PriorityQueuePanel({ queue, onRefresh }) {
  const items = queue?.prioritized || [];
  const next = queue?.selected_next;

  return (
    <section className="panel">
      <div className="panel-head">
        <h2>02 // Priority Queue</h2>
        <button type="button" className="ghost" onClick={onRefresh}>
          Recalculate heap
        </button>
      </div>
      {next && (
        <div className="next-response">
          <span>NEXT RESPONSE</span>
          <strong>
            {next.incident_id} — {next.incident_type} — {next.severity} — {next.priority_score}
          </strong>
        </div>
      )}
      <ol className="queue-list">
        {items.map((inc, i) => (
          <li key={inc.incident_id}>
            <span className="medal">{MEDALS[i] || `${i + 1}.`}</span>
            <span>
              {inc.incident_id} — {inc.severity} — {inc.priority_score}
            </span>
            <span className="muted">{inc.incident_type}</span>
          </li>
        ))}
      </ol>
    </section>
  );
}
