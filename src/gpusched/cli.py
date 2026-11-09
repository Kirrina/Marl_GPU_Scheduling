"""Small dependency-free CLI for initial scaffold. No fake 'full simulation' run."""
from __future__ import annotations
import argparse
from pathlib import Path
from gpusched.contracts.shared import ExperimentConfig, CONTRACT_VERSION

ROOT=Path(__file__).resolve().parents[2]

def main(argv: list[str] | None=None) -> int:
    parser=argparse.ArgumentParser(description="MARL V1 scaffold (not trained)")
    sub=parser.add_subparsers(dest="cmd",required=True)
    sub.add_parser("status",help="show what is implemented vs TODO")
    todo=sub.add_parser("todo",help="show TODO by owner: A/B/all")
    todo.add_argument("owner",nargs="?",default="all",choices=("A","B","all"))
    opts=parser.parse_args(argv)
    if opts.cmd=="status":
        c=ExperimentConfig()
        print(f"Contract {CONTRACT_VERSION} | clusters={c.environment.num_clusters} | total GPU={c.environment.total_gpus}")
        print("D5 max_defer=5, N=500, alpha=0.05, lambda_queue=1; D6 synthetic=3.0 seconds")
        print("READY: shared dataclasses/validators/hash, pure metrics/cost/rewards, FakeEnvironment mock")
        print("TODO: A1-A6 and B1-B4 full implementations; no real simulator/training/evaluation yet")
        print("PENDING IC0 signatures: exact C2 dimension/order, quantile convention, reward hyperparams")
        return 0
    path=ROOT/'TODO.md'
    content=path.read_text(encoding="utf8")
    if opts.owner == "all":
        print(content)
    else:
        marker=f"## Người {opts.owner} ("
        other="## Người B (" if opts.owner=="A" else "## Milestones:"
        start=content.index(marker)
        end=content.index(other,start)
        print(content[start:end].strip())
    return 0

if __name__=="__main__":
    raise SystemExit(main())
