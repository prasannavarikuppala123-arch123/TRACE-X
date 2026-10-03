"""Dijkstra's shortest path implemented from scratch (min-heap + relaxation)."""

import heapq


def shortest_path(graph, source, target):
    if source not in graph.containment_adj:
        raise ValueError(f"Unknown source system: {source}")
    if target not in graph.containment_adj:
        raise ValueError(f"Unknown target system: {target}")

    dist = {node: float("inf") for node in graph.containment_adj}
    prev = {node: None for node in graph.containment_adj}
    dist[source] = 0
    heap = [(0, source)]
    visited_order = []
    visited = set()
    steps = [f"Initialize distances. Source {source} cost = 0."]

    while heap:
        cost, node = heapq.heappop(heap)
        if node in visited:
            continue
        visited.add(node)
        visited_order.append(node)
        steps.append(f"Current node: {node}. Current cost: {cost}.")

        if node == target:
            steps.append(f"{target} reached.")
            break

        for neighbor, weight in graph.containment_adj.get(node, []):
            if neighbor in visited:
                continue
            candidate = cost + weight
            if candidate < dist[neighbor]:
                dist[neighbor] = candidate
                prev[neighbor] = node
                heapq.heappush(heap, (candidate, neighbor))
                steps.append(
                    f"Updating {neighbor} cost to {candidate} via {node} (edge weight {weight})."
                )

    if dist[target] == float("inf"):
        return {
            "source": source,
            "target": target,
            "path": [],
            "total_cost": None,
            "visited_nodes": visited_order,
            "steps": steps + [f"No containment route from {source} to {target}."],
            "reachable": False,
            "explanation": {
                "title": "WHY THIS CONTAINMENT ROUTE?",
                "lines": [f"No path exists between {source} and {target} on the weighted graph."],
                "therefore": "Dijkstra could not produce a finite-cost route.",
            },
        }

    path = []
    cursor = target
    while cursor is not None:
        path.append(cursor)
        cursor = prev[cursor]
    path.reverse()

    hop_costs = []
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        weight = next(w for n, w in graph.containment_adj[a] if n == b)
        hop_costs.append({"from": a, "to": b, "cost": weight})

    explanation_lines = [
        f"Edge {h['from']} → {h['to']} costs {h['cost']}." for h in hop_costs
    ]
    explanation_lines.append(f"Sum of edge weights = {dist[target]}.")

    return {
        "source": source,
        "target": target,
        "path": path,
        "total_cost": dist[target],
        "visited_nodes": visited_order,
        "hop_costs": hop_costs,
        "steps": steps,
        "reachable": True,
        "algorithm": "Dijkstra",
        "explanation": {
            "title": "WHY THIS CONTAINMENT ROUTE?",
            "lines": explanation_lines,
            "therefore": "Route selected because it has the lowest total response cost.",
        },
    }
