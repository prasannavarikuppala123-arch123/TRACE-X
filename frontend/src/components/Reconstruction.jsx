const FLOW = [
  { icon: "🚨", label: "Incident Detected" },
  { icon: "🔎", label: "Entry Point Identified" },
  { icon: "🕸️", label: "Blast Radius Calculated" },
  { icon: "⚠️", label: "Critical Asset Identified" },
  { icon: "⚡", label: "Priority Score Calculated" },
  { icon: "🛡️", label: "Containment Route Calculated" },
  { icon: "✅", label: "Response Plan Generated" },
];

export default function Reconstruction({ systems, clues, result, onReconstruct }) {
  const plan = result?.plan;

  return (
    <section className="panel reconstruct">
      <div className="panel-head">
        <h2>04 // Incident Reconstruction</h2>
      </div>
      <div className="clue-row">
        {(clues || []).map((clue) => (
          <button
            key={clue.id}
            type="button"
            className="clue"
            onClick={() => onReconstruct(clue.suggests, "Ransomware")}
          >
            {clue.icon} {clue.text}
          </button>
        ))}
      </div>
     <p className="hint">
  Select a detected incident entry point. TRACE-X reconstructs the attack path
  and automatically runs BFS → Priority Queue → Dijkstra.
</p>
      <div className="entry-row">
        {(systems || []).map((sys) => (
          <button key={sys} type="button" className="chip" onClick={() => onReconstruct(sys, "Ransomware")}>
            {sys}
          </button>
        ))}
      </div>
      <ol className="flow">
        {FLOW.map((step) => (
          <li key={step.label} className={plan ? "done" : ""}>
            <span>{step.icon}</span>
            {step.label}
          </li>
        ))}
      </ol>
      {plan && (
        <div className="plan-box">
          <h3>{plan.headline}</h3>
          <dl>
            <dt>Incident</dt>
            <dd>{plan.incident}</dd>
            <dt>Entry Point</dt>
            <dd>{plan.entry_point}</dd>
            <dt>Potential Blast Radius</dt>
            <dd>{plan.potential_blast_radius} systems</dd>
            <dt>Critical Asset at Risk</dt>
            <dd>{plan.critical_asset_at_risk}</dd>
            <dt>Priority Score</dt>
<dd>
  ⚡ {plan.priority_score}/10 — {plan.priority}
</dd>
            <dt>Recommended Containment Route</dt>
            <dd>{(plan.recommended_containment_route || []).join(" → ") || "Unreachable"}</dd>
            <dt>Status</dt>
            <dd>{plan.status}</dd>
          </dl>
        </div>
      )}
    </section>
  );
}
