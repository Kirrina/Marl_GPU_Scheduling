# Contract golden fixtures (IC0)

`golden_cases.json`: exactly six scenario groups matching attached assignment §6;
scenario #6 corrects the impossible expectation of nonzero ΔF for a 4-GPU job
on 4-GPU empty node by adding job1/2 sign checks.

`C1-workload.mock.json`: programmatically generated SHA-256 verified C1 sample.
`C3-event-log.mock.jsonl`: valid structural example ONLY, not a production trace.

A signs expected fields/calculator results; B independently re-computes and
reviews; any change -> both review + contract_version bump.
