"""Weighted directed infrastructure graph plus bidirectional containment view."""

from data import CRITICAL_ASSETS, DIRECTED_EDGES, SYSTEMS


class CyberGraph:
    def __init__(self, systems=None, edges=None):
        self.systems = list(systems if systems is not None else SYSTEMS)
        self.edges = list(edges if edges is not None else DIRECTED_EDGES)
        self.attack_adj = {node: [] for node in self.systems}
        self.containment_adj = {node: [] for node in self.systems}
        self._build()

    def _build(self):
        self.attack_adj = {node: [] for node in self.systems}
        self.containment_adj = {node: [] for node in self.systems}
        for src, dst, cost in self.edges:
            if src not in self.attack_adj:
                self.attack_adj[src] = []
                self.containment_adj[src] = []
                self.systems.append(src)
            if dst not in self.attack_adj:
                self.attack_adj[dst] = []
                self.containment_adj[dst] = []
                self.systems.append(dst)
            self.attack_adj[src].append((dst, cost))
            self._add_undirected(src, dst, cost)

    def _add_undirected(self, src, dst, cost):
        if not any(n == dst for n, _ in self.containment_adj[src]):
            self.containment_adj[src].append((dst, cost))
        if not any(n == src for n, _ in self.containment_adj[dst]):
            self.containment_adj[dst].append((src, cost))

    def add_edge(self, src, dst, cost):
        self.edges.append((src, dst, cost))
        if src not in self.attack_adj:
            self.attack_adj[src] = []
            self.containment_adj[src] = []
            self.systems.append(src)
        if dst not in self.attack_adj:
            self.attack_adj[dst] = []
            self.containment_adj[dst] = []
            self.systems.append(dst)
        self.attack_adj[src].append((dst, cost))
        self._add_undirected(src, dst, cost)

    def serialize(self, compromised=None, affected=None, inactive=None, path=None):
        compromised = set(compromised or [])
        affected = set(affected or [])
        inactive = set(inactive or [])
        path = path or []
        nodes = []
        for name in self.systems:
            if name in compromised:
                state = "compromised"
            elif name in affected:
                state = "affected"
            elif name in inactive:
                state = "inactive"
            else:
                state = "safe"
            nodes.append(
                {
                    "id": name,
                    "label": name,
                    "state": state,
                    "critical": name in CRITICAL_ASSETS,
                    "on_path": name in path,
                }
            )
        edge_payload = [
            {"source": src, "target": dst, "cost": cost} for src, dst, cost in self.edges
        ]
        return {
            "nodes": nodes,
            "edges": edge_payload,
            "critical_assets": list(CRITICAL_ASSETS),
        }


INFRA_GRAPH = CyberGraph()
