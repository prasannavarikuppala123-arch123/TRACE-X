"""In-memory incident store wired to PQ, BFS, and Dijkstra."""

from bfs import blast_radius
from data import (
    CRITICAL_ASSETS,
    RECONSTRUCTION_CLUES,
    initial_incidents,
    severity_from_score,
)
from dijkstra import shortest_path
from graph import INFRA_GRAPH
from priority_queue import IncidentPriorityQueue


class IncidentManager:
    def __init__(self):
        self.incidents = initial_incidents()
        self.queue = IncidentPriorityQueue()
        self.compromised = set()
        self.last_blast = None
        self.last_path = None
        self.last_priority = None
        self._counter = 3

    def list_incidents(self):
        return list(self.incidents)

    def upsert_incident(self, payload):
        incident_id = payload.get("incident_id")

        if not incident_id:
            self._counter += 1
            incident_id = f"INC-{self._counter:03d}"

        existing = self._find(incident_id)

        score = int(
            payload.get(
                "priority_score",
                existing["priority_score"] if existing else 5,
            )
        )

        severity = payload.get("severity") or severity_from_score(score)

        record = {
            "incident_id": incident_id,
            "incident_type": payload.get(
                "incident_type",
                existing["incident_type"] if existing else "Unknown",
            ),
            "severity": severity,
            "affected_system": payload.get(
                "affected_system",
                existing["affected_system"] if existing else "Employee-PC",
            ),
            "priority_score": score,
            "status": payload.get(
                "status",
                existing["status"] if existing else "Open",
            ),
        }

        if existing:
            existing.update(record)
            return existing

        self.incidents.append(record)
        return record

    def _find(self, incident_id):
        for incident in self.incidents:
            if incident["incident_id"] == incident_id:
                return incident
        return None

    def _find_by_system(self, system):
        for incident in self.incidents:
            if incident["affected_system"] == system:
                return incident
        return None

    def prioritize(self):
        result = self.queue.prioritize(self.incidents)
        self.last_priority = result
        return result

    def graph_payload(self):
        affected = []
        path = []

        if self.last_blast:
            affected = self.last_blast.get("affected_systems", [])

        if self.last_path:
            path = self.last_path.get("path", [])

        return INFRA_GRAPH.serialize(
            compromised=self.compromised,
            affected=affected,
            path=path,
        )

    # ---------------------------------------------------------
    # AUTOMATIC BASE SCORE
    # ---------------------------------------------------------

    def base_score_from_type(self, incident_type):
        scores = {
            "Ransomware": 7,
            "Data Breach": 6,
            "Malware": 6,
            "Unauthorized Access": 5,
            "Phishing": 3,
        }

        return scores.get(incident_type, 4)

    # ---------------------------------------------------------
    # AUTOMATIC IMPACT SCORE
    # ---------------------------------------------------------

    def compute_impact_score(self, base_score, blast):
        affected = set(blast["affected_systems"]) | {blast["start"]}

        bonus = 0

        critical_hit = [
            name
            for name in CRITICAL_ASSETS
            if name in affected
        ]

        if "Database" in critical_hit:
            bonus += 2

        if "Backup Server" in critical_hit:
            bonus += 1

        if "SOC" in critical_hit or "Firewall" in critical_hit:
            bonus += 1

        # Additional impact for a large blast radius.
        if len(affected) >= 7:
            bonus += 1

        score = min(
            10,
            max(1, int(base_score) + bonus)
        )

        return score, critical_hit, bonus, len(affected)

    # ---------------------------------------------------------
    # INCIDENT DETECTION + AUTOMATIC SCORING
    # ---------------------------------------------------------

    def mark_compromised(self, system, incident_type=None):

        if system not in INFRA_GRAPH.attack_adj:
            raise ValueError(f"Unknown system: {system}")

        # Mark system as compromised.
        self.compromised.add(system)

        # BFS calculates blast radius.
        blast = blast_radius(INFRA_GRAPH, system)
        self.last_blast = blast

        # Critical assets inside blast radius.
        critical_hit = [
            name
            for name in CRITICAL_ASSETS
            if name in blast["affected_systems"] or name == system
        ]

        # Check existing incident.
        incident = self._find_by_system(system)

        # Determine incident type.
        if incident_type is None:
            incident_type = (
                incident["incident_type"]
                if incident
                else "Compromise"
            )

        # Automatic base score.
        base = self.base_score_from_type(incident_type)

        # Automatic impact score.
        score, critical_from_score, bonus, affected_count = (
            self.compute_impact_score(base, blast)
        )

        final_critical_assets = critical_hit or critical_from_score

        # Explanation for judge/demo.
        score_explanation = {
            "base_score": base,
            "affected_systems": affected_count,
            "critical_assets": final_critical_assets,
            "impact_bonus": bonus,
            "final_score": score,
            "reason": (
                f"{incident_type} starts with a base score of {base}. "
                f"BFS identified {affected_count} affected systems. "
                f"Critical assets at risk: "
                f"{', '.join(final_critical_assets) if final_critical_assets else 'None'}. "
                f"Impact bonus: +{bonus}. "
                f"Final automatic priority: {score}/10."
            ),
        }

        # Create or update incident.
        if not incident:
            incident = self.upsert_incident(
                {
                    "incident_type": incident_type,
                    "affected_system": system,
                    "priority_score": score,
                    "severity": severity_from_score(score),
                    "status": "Investigating",
                }
            )
        else:
            incident["incident_type"] = incident_type
            incident["priority_score"] = score
            incident["severity"] = severity_from_score(score)
            incident["status"] = "Investigating"

        # Priority Queue automatically uses the calculated score.
        pq = self.prioritize()

        return {
            "compromised": system,
            "compromised_systems": sorted(self.compromised),
            "blast_radius": blast,
            "critical_assets_at_risk": final_critical_assets,
            "incident": incident,
            "score_explanation": score_explanation,
            "priority_queue": pq,
        }

    def uncompromise(self, system):
        self.compromised.discard(system)

        if self.last_blast and self.last_blast.get("start") == system:
            self.last_blast = None

        return {
            "compromised_systems": sorted(self.compromised)
        }

    # ---------------------------------------------------------
    # INCIDENT RECONSTRUCTION
    # ---------------------------------------------------------

    def reconstruct(self, entry, incident_type="Ransomware"):

        if entry not in INFRA_GRAPH.attack_adj:
            raise ValueError(f"Unknown system: {entry}")

        # BFS
        blast = blast_radius(INFRA_GRAPH, entry)
        self.last_blast = blast
        self.compromised.add(entry)

        affected_set = set(blast["affected_systems"]) | {entry}

        critical_hit = [
            name
            for name in CRITICAL_ASSETS
            if name in affected_set
        ]

        incident = self._find_by_system(entry)

        # Automatic score.
        base = self.base_score_from_type(incident_type)

        score, _, _, _ = self.compute_impact_score(
            base,
            blast,
        )

        incident = self.upsert_incident(
            {
                "incident_id": (
                    incident["incident_id"]
                    if incident
                    else None
                ),
                "incident_type": incident_type,
                "affected_system": entry,
                "priority_score": score,
                "severity": severity_from_score(score),
                "status": "Containment Plan Generated",
            }
        )

        # Priority Queue
        pq = self.prioritize()

        # Dijkstra
        route = shortest_path(
            INFRA_GRAPH,
            "SOC",
            entry,
        )

        self.last_path = route

        plan = {
            "headline": "INCIDENT RECONSTRUCTED",
            "incident": incident_type,
            "entry_point": entry,
            "potential_blast_radius": blast["affected_count"],
            "affected_systems": blast["affected_systems"],
            "critical_asset_at_risk": (
                critical_hit[0]
                if critical_hit
                else "None identified"
            ),
            "critical_assets_at_risk": critical_hit,
            "priority": incident["severity"],
            "priority_score": incident["priority_score"],
            "recommended_containment_route": route["path"],
            "total_cost": route["total_cost"],
            "status": "Containment Plan Generated",
        }

        return {
            "plan": plan,
            "blast_radius": blast,
            "priority_queue": pq,
            "containment": route,
            "incident": incident,
            "clues": RECONSTRUCTION_CLUES,
            "flow": [
                "Incident Detected",
                "Entry Point Identified",
                "Blast Radius Calculated",
                "Critical Asset Identified",
                "Priority Assigned",
                "Containment Route Calculated",
                "Response Plan Generated",
            ],
        }


MANAGER = IncidentManager()