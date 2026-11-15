"""Summarize bounded service telemetry for an incident commander."""
from statistics import median

from loop import Probe, integer, name, rows

BRIEF = "Investigate an SRE incident using request SLO, deploy timeline and dependency symptoms."
REQUIRED = {"slo", "timeline", "dependencies"}


def build_probes(case):
    service = name(case["service"])
    now = integer(case["now"])
    window = integer(case["window"], maximum=120)
    if window < 1:
        raise ValueError("window must be positive")

    def recent(records):
        selected = []
        for record in rows(records):
            minute = integer(record["minute"])
            if name(record["service"]) == service and 0 <= now - minute < window:
                selected.append((minute, record))
        return selected

    def slo():
        traffic = recent(case["traffic"])
        counts = {}
        for minute, record in traffic:
            total, errors = integer(record["requests"]), integer(record["errors"])
            if errors > total or minute in counts:
                raise ValueError("invalid or duplicate traffic bucket")
            counts[minute] = (total, errors)
        total = sum(item[0] for item in counts.values())
        errors = sum(item[1] for item in counts.values())
        return {"buckets": len(counts), "latest": max(counts, default=None), "expected_buckets": window,
                "requests": total, "errors": errors, "breach": total >= 100 and errors * 100 >= 2 * total}

    def timeline():
        return {"changes": [{"id": name(row["id"]), "minute": minute}
                            for minute, row in sorted(recent(case["changes"]), key=lambda item: item[0])]}

    def dependencies():
        by_dependency = {}
        for _, row in recent(case["dependencies"]):
            by_dependency.setdefault(name(row["dependency"]), []).append(integer(row["p95_ms"], maximum=120_000))
        return {"observed": len(by_dependency),
                "degraded": sorted(key for key, values in by_dependency.items() if median(values) > 350)}

    return [
        Probe("slo", "Calculate error ratio from in-window service requests.", slo),
        Probe("timeline", "Collect deployments affecting the service during the window.", timeline),
        Probe("dependencies", "Summarize in-window dependency latency by name.", dependencies),
        Probe("coverage", "Read the selected service and investigation window.", lambda: {"service": service, "minutes": window}),
    ]


def decide(evidence):
    slo = evidence["slo"]
    changes = evidence["timeline"]["changes"]
    deps = evidence["dependencies"]
    if slo["requests"] < 100 or slo["buckets"] != slo["expected_buckets"] or not deps["observed"]:
        decision, reason = "review", "traffic or dependency telemetry has incomplete coverage"
    elif slo["breach"]:
        clues = []
        if changes:
            clues.append("recent changes")
        if deps["degraded"]:
            clues.append("high dependency latency")
        decision = "page_candidate"
        reason = "error ratio crossed 2%" + (f"; investigate {' and '.join(clues)}" if clues else "")
    else:
        decision, reason = "observe", "error ratio below 2% with complete telemetry"
    return {"decision": decision, "reason": reason, "citations": sorted(REQUIRED)}


def prepare(case):
    return build_probes(case), decide
