"""C1 stable JSON serialization/hash. No job runtime exposed in C2 DecisionPoint."""
from __future__ import annotations
from dataclasses import asdict
from .shared import EventLogRecord, EventType
from .validation import validate_event
from pathlib import Path
from hashlib import sha256
import json
from typing import Any
from .shared import WorkloadFile, WorkloadHeader, WorkloadJob, CONTRACT_VERSION
from .validation import validate_workload


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def payload_for_hash(header: dict, jobs: list[dict]) -> dict:
    """Hash all immutable workload content EXCEPT header.content_hash to avoid circular hash."""
    h = {k: v for k, v in header.items() if k != "content_hash"}
    return {"header": h, "jobs": jobs}


def workload_hash(header: dict, jobs: list[dict]) -> str:
    return sha256(canonical_json(payload_for_hash(header, jobs)).encode("utf8")).hexdigest()


def write_workload(path: str | Path, workload: WorkloadFile) -> str:
    """Return content hash after writing; validates ordering, source, counts and finite fields."""
    validate_workload(workload)
    hdr = asdict(workload.header)
    jobs = [asdict(j) for j in workload.jobs]
    hdr["content_hash"] = workload_hash(hdr, jobs)
    if workload.header.content_hash not in ("", hdr["content_hash"]):
        raise ValueError("WorkloadHeader.content_hash differs from computed digest")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"header":hdr,"jobs":jobs}, indent=2, ensure_ascii=False)+"\n", encoding="utf8")
    return hdr["content_hash"]


def read_workload(path: str | Path) -> WorkloadFile:
    raw = json.loads(Path(path).read_text(encoding="utf8"))
    actual = workload_hash(raw["header"],raw["jobs"])
    if raw["header"].get("content_hash") != actual:
        raise ValueError("C1 content hash mismatch")
    loaded = WorkloadFile(header=WorkloadHeader(**raw["header"]),
                          jobs=tuple(WorkloadJob(**j) for j in raw["jobs"]))
    validate_workload(loaded)
    return loaded


def write_event_log(path: str | Path, events: list[EventLogRecord]) -> None:
    """C3 JSONL writer for A; all events finite, nondecreasing simulated time."""
    path=Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    prior=float("-inf")
    with path.open("w",encoding="utf8") as stream:
        for event in events:
            validate_event(event)
            if event.time < prior:
                raise ValueError("C3 events must be chronological")
            stream.write(canonical_json(asdict(event))+"\n")
            prior=event.time


def read_event_log(path: str | Path) -> tuple[EventLogRecord,...]:
    """C3 JSONL reader for B; no imports from A-side simulator internals."""
    events=[]
    for line in Path(path).read_text(encoding="utf8").splitlines():
        if not line.strip():
            continue
        record=json.loads(line)
        record["event_type"]=EventType(record["event_type"])
        if record.get("queue_len_by_gpu") is not None:
            record["queue_len_by_gpu"]=tuple(record["queue_len_by_gpu"])
        event=EventLogRecord(**record)
        validate_event(event)
        if events and event.time < events[-1].time:
            raise ValueError("C3 events must be chronological")
        events.append(event)
    return tuple(events)
