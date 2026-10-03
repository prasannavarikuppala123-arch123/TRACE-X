"""Breadth-first search implemented from scratch for blast-radius analysis."""

from collections import deque


def blast_radius(graph, start):
    if start not in graph.attack_adj:
        raise ValueError(f"Unknown system: {start}")

    visited = {start}
    order = [start]
    levels = {0: [start]}
    parent = {start: None}
    steps = [f"Visiting {start}... (level 0, origin)"]
    queue = deque([(start, 0)])

    while queue:
        node, depth = queue.popleft()
        for neighbor, _cost in graph.attack_adj.get(node, []):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            parent[neighbor] = node
            nxt = depth + 1
            levels.setdefault(nxt, []).append(neighbor)
            order.append(neighbor)
            steps.append(f"Visiting {neighbor}... (reached from {node}, level {nxt})")
            queue.append((neighbor, nxt))

    affected = [n for n in order if n != start]
    explanation_lines = []
    for node in order[1:]:
        pred = parent[node]
        explanation_lines.append(f"{pred} is connected to {node}.")

    if explanation_lines:
        therefore = "Therefore these systems are potentially reachable from the compromised origin."
    else:
        therefore = "No outbound dependency edges were found from the origin."

    return {
        "start": start,
        "traversal_order": order,
        "levels": {str(k): v for k, v in sorted(levels.items())},
        "affected_systems": affected,
        "affected_count": len(affected),
        "parent": parent,
        "steps": steps,
        "explanation": {
            "title": "WHY ARE THESE SYSTEMS AT RISK?",
            "lines": explanation_lines,
            "therefore": therefore,
        },
    }
