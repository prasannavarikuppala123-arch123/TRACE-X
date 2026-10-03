"""In-memory sample incidents and infrastructure graph for TRACE-X."""

CRITICAL_ASSETS = ["Database", "Backup Server", "SOC", "Firewall"]

SYSTEMS = [
    "Employee-PC",
    "VPN",
    "Web Server",
    "Application Server",
    "Database",
    "File Server",
    "Backup Server",
    "Mail Server",
    "Firewall",
    "Internal Network",
    "SOC",
]

# Directed attack/dependency edges: (source, target, containment_cost)
DIRECTED_EDGES = [
    ("Employee-PC", "VPN", 2),
    ("Employee-PC", "Mail Server", 1),
    ("VPN", "Internal Network", 3),
    ("Internal Network", "Application Server", 2),
    ("Internal Network", "File Server", 2),
    ("Internal Network", "Firewall", 2),
    ("Application Server", "Database", 2),
    ("Database", "Backup Server", 3),
    ("Web Server", "Application Server", 2),
    ("Web Server", "Firewall", 3),
    ("SOC", "Firewall", 1),
    ("Firewall", "VPN", 2),
    ("Firewall", "Database", 4),
    ("Mail Server", "Internal Network", 4),
]


def severity_from_score(score):
    if score >= 8:
        return "Critical"
    if score >= 5:
        return "High"
    if score >= 3:
        return "Medium"
    return "Low"


def initial_incidents():
    return [
        {
            "incident_id": "INC-001",
            "incident_type": "Ransomware",
            "severity": "Critical",
            "affected_system": "Employee-PC",
            "priority_score": 10,
            "status": "Open",
        },
        {
            "incident_id": "INC-002",
            "incident_type": "Data Breach",
            "severity": "High",
            "affected_system": "Database",
            "priority_score": 8,
            "status": "Open",
        },
        {
            "incident_id": "INC-003",
            "incident_type": "Phishing",
            "severity": "Medium",
            "affected_system": "Mail Server",
            "priority_score": 4,
            "status": "Open",
        },
    ]


RECONSTRUCTION_CLUES = [
    {
        "id": "clue-1",
        "icon": "🚨",
        "text": "Suspicious login detected on Employee-PC",
        "suggests": "Employee-PC",
    },
    {
        "id": "clue-2",
        "icon": "🔐",
        "text": "Unusual VPN connection detected",
        "suggests": "VPN",
    },
    {
        "id": "clue-3",
        "icon": "🗄️",
        "text": "Database accessed unexpectedly",
        "suggests": "Database",
    },
    {
        "id": "clue-4",
        "icon": "📁",
        "text": "Unusual file activity detected",
        "suggests": "File Server",
    },
]
