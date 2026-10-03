"""Max-priority queue for incidents, implemented with heapq."""

import heapq


class IncidentPriorityQueue:
    def __init__(self):
        self._heap = []
        self._seq = 0

    def clear(self):
        self._heap = []
        self._seq = 0

    def push(self, incident):
        score = int(incident["priority_score"])
        # heapq is a min-heap; negate score so the largest priority comes first.
        heapq.heappush(self._heap, (-score, self._seq, incident["incident_id"], incident))
        self._seq += 1

    def rebuild(self, incidents):
        self.clear()
        steps = ["Rebuilding priority queue from active incidents..."]
        for incident in incidents:
            self.push(incident)
            steps.append(
                f"Inserted {incident['incident_id']} with priority {incident['priority_score']}."
            )
        return steps

    def is_empty(self):
        return not self._heap

    def peek(self):
        if not self._heap:
            return None
        return self._heap[0][3]

    def pop(self):
        if not self._heap:
            return None
        return heapq.heappop(self._heap)[3]

    def ordered(self):
        clone = list(self._heap)
        ordered = []
        while clone:
            _neg, _seq, _iid, incident = heapq.heappop(clone)
            ordered.append(incident)
        return ordered

    def prioritize(self, incidents):
        insert_steps = self.rebuild(incidents)
        ordered = self.ordered()
        selected = ordered[0] if ordered else None
        steps = insert_steps + ["Selecting highest-priority incident..."]
        if selected:
            steps.append(f"{selected['incident_id']} selected.")
            steps.append(f"Priority = {selected['priority_score']}")
        else:
            steps.append("Queue is empty.")

        explanation = {
            "title": "WHY WAS THIS INCIDENT SELECTED?",
            "lines": [],
            "therefore": "No incidents are queued.",
        }
        if selected:
            explanation["lines"] = [
                f"Severity: {selected['severity']}",
                f"Priority Score: {selected['priority_score']}",
                f"Affected System: {selected['affected_system']}",
            ]
            explanation["therefore"] = (
                f"{selected['incident_id']} was selected first by Priority Queue "
                f"because it has the highest priority_score ({selected['priority_score']})."
            )

        return {
            "prioritized": ordered,
            "priority_scores": [
                {"incident_id": i["incident_id"], "priority_score": i["priority_score"]}
                for i in ordered
            ],
            "selected_next": selected,
            "steps": steps,
            "explanation": explanation,
        }
