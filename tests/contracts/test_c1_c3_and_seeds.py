import json
from pathlib import Path
import pytest
from gpusched.contracts.shared import (
    WorkloadHeader, WorkloadJob, WorkloadFile, CONTRACT_VERSION,
    EventType, EventLogRecord,
)
from gpusched.contracts.io import read_workload, write_workload, read_event_log, write_event_log
from gpusched.contracts.validation import validate_event
from gpusched.workload.synthetic import derive_subseed,arrival_rate_for_load


def test_workload_hash_roundtrip_and_tampering(tmp_path):
    file=WorkloadFile(WorkloadHeader("s0","synthetic",2026,""),
       (WorkloadJob("j1",0.0,1,1,4,3.0,"synthetic"),
        WorkloadJob("j2",0.2,4,8,16,3.0,"synthetic")))
    path=tmp_path/"test.json"
    digest=write_workload(path,file)
    assert read_workload(path).header.content_hash==digest
    data=json.loads(path.read_text())
    data["jobs"][1]["duration"]=4
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError,match="hash mismatch"):
        read_workload(path)


def test_subseed_labels_are_stable_and_distinct():
    assert derive_subseed(2026,"cpu")==derive_subseed(2026,"cpu")
    assert derive_subseed(2026,"cpu")!=derive_subseed(2026,"ram")
    assert arrival_rate_for_load(0.75,48,7)==pytest.approx(36/7)


def test_mock_c3_event_log_is_schema_valid():
    path=Path(__file__).resolve().parents[2]/"fixtures/C3-event-log.mock.jsonl"
    for line in path.read_text().splitlines():
        raw=json.loads(line)
        raw["event_type"]=EventType(raw["event_type"])
        if "queue_len_by_gpu" in raw:
            raw["queue_len_by_gpu"]=tuple(raw["queue_len_by_gpu"])
        validate_event(EventLogRecord(**raw))


def test_event_log_jsonl_roundtrip(tmp_path):
    events=(EventLogRecord(0.,EventType.ARRIVAL,"j",queue_len=1,
                           queue_len_by_gpu=(1,0,0)),
            EventLogRecord(3.,EventType.COMPLETE,"j",cluster_id=0,node_id=0,
                           gpu_free_after=4))
    path=tmp_path/"log.jsonl"
    write_event_log(path,list(events))
    assert read_event_log(path)==events
