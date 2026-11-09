# MARL GPU Scheduling V1 — Contract-first INITIAL repository

> **Đây là repo khởi tạo để 2 người BẮT ĐẦU implement, KHÔNG phải hệ thống MARL đã chạy xong.**
> Nguồn ưu tiên: [`docs/assignment-source.txt`](docs/assignment-source.txt), bản phân chia
> A1–A6/B1–B4 do nhóm cung cấp. Kiến trúc nền:
> [`docs/technical-spec-original.md`](docs/technical-spec-original.md), cộng ba quyết định mới.

## 0. Ý tưởng đường cắt

```text
B (chủ động): WORKLOAD B1 -> C1 WorkloadFile -> A (thụ động): EventSimulator A1-A4
B: [Management/Cluster Actor+Critic B2, Trainer B3]
        -- run_until_next_decision() --> A
        <-- C2 DecisionPoint ----------- A
        -- C2 SchedulingAction --------> A
        <-- C2 PlacementResult (facts) - A
B: reward from facts, not from simulator; shadow clone for bootstrapping
A: C3 Event Log -----------------------> B: Evaluator B4

Shared only: C0 Config + C1 Workload + C2 Decision + C3 EventLog
```

**B tuyệt đối không import `gpusched.sim`, `gpusched.baselines`, `gpusched.calibration`.
A tuyệt đối không import `gpusched.learning`, `gpusched.workload`, `gpusched.eval`.**
Interface chung nằm DUY NHẤT ở [`src/gpusched/contracts/shared.py`](src/gpusched/contracts/shared.py).

## 1. Cài và kiểm tra

Python >=3.11. Để tạo môi trường phát triển (chưa cần torch):

```bash
python -m venv .venv
source .venv/bin/activate            # PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
make contracts                         # C0-C3 schemas + 6 golden fixtures
make boundaries                        # cấm import chéo A/B
make check                             # test hiện có + pending/skipped TODO
python -m gpusched status
python -m gpusched todo A              # or B
```

B cài thêm Torch khi bắt đầu B2/B3: `python -m pip install -e ".[learning]"`.
**Không chạy `python -m gpusched train` hay `simulate` vì chưa được implement.**

## 2. Tra đầu việc theo file (đọc file TODO + docstring trước khi code)

| ID | Người A — Environment | Test |
|---|---|---|
| A1 | `src/gpusched/sim/models.py` — Job/Node/Cluster, atomic alloc/release | TST01-02 |
| A2 | `src/gpusched/sim/events.py` — event heap/time/release/log/clone | TST12, TST14 shadow clone |
| A3 | `src/gpusched/sim/queue.py`, `sim/events.py` — queue sweep, Gate, lock, mask, actions | TST03,05,06,09,10,11,19 |
| A4 | `src/gpusched/sim/cost.py`, `sim/observations.py` — EMA/F/L/C/DecisionPoint | TST04,07,08 |
| A5 | `src/gpusched/baselines/policies.py` — đúng 4 baseline | TST16 |
| A6 | `src/gpusched/calibration/random_valid.py` — calibration train only | TST07/IC2 |

| ID | Người B — Learning/Workload/Eval | Test |
|---|---|---|
| B1 | `src/gpusched/workload/{synthetic,philly}.py` — Poisson, CPU/RAM D3, duration D6, Philly | TST18 |
| B2 | `src/gpusched/learning/networks.py` — 4 encoders, 2 policies, 2 critics | TST15 |
| B3 | `src/gpusched/learning/{rewards,rollout,shadow,trainer,checkpoint}.py` | TST13,14,20 |
| B4 | `src/gpusched/eval/{metrics,evaluator}.py` — C3→plots, common p_eval | TST17 |

## 3. Những thứ đã chốt (không tự đổi)

- Gate globally feasible nhưng Management được chọn *bất kỳ* cluster K; Cluster sẽ Allocate/Forward hợp lệ.
- Một job đúng một node; GPU demand {1,2,4}, CPU/RAM hard constraints; 4 baseline duy nhất.
- D5: `max_defer=5`, `episode_jobs_N=500`, `alpha_ema=0.05`, `lambda_queue=1`;
  D6: synthetic (kể cả fill) `duration=3.0s`; Philly dùng end-start thực tế.
- **Integration #1:** A tính cost, C2 facts; B tính reward (không import/reimplement A cost).
- **Integration #2:** tại rollout boundary B dùng A `clone()` để shadow lookahead với
  policy cũ; update cả hai policy sau khi discard shadow; terminal bootstrap 0.
- **Integration #3:** A log số node đủ GPU và số bị CPU/RAM block, B vẽ ratio;
  *diagnostic only*, không thay reward/observation/masks.
- D4: Philly schema và số lượng thực tế chưa kiểm chứng; không tuyên bố kết quả thật.

**Chưa có ký riêng:** layout đề nghị node_features[4], cluster_stats[10], quy tắc
sub-seed, quy ước percentile 95, lựa chọn giá trị các hyperparameter TUNE.
V1 starter hiện dùng layout được đưa ra trong bảng phân công làm **DRAFT CONTRACT**.
Xem [`docs/NEEDS-SIGNOFF.md`](docs/NEEDS-SIGNOFF.md).

## 4. Mốc tích hợp

| Mốc | Điều kiện đạt (không phải đã hoàn thành) |
|---|---|
| IC0 | C0-C3 fixed schema, Mock A/B + 6 golden fixtures; contract tests xanh |
| IC1 | A real simulator + 4 baselines log C3; B networks forward DecisionPoint thật |
| IC2 | 1 episode end-to-end, shadow test, two buffers, reward consistent |
| IC3 | MARL vượt Random Valid ở workload dễ trước tuning lớn |

### Cách làm với Claude Code

`/implement-a A1`, `/implement-b B2`, `/ic0-contracts`, `/golden-tests`,
`/review-integration`, `/todo-owner A`. Các instruction chi tiết ở `.claude/`.

## 5. Git workflow

```bash
git init
git add .
git commit -m "chore: initial contract-first v1 skeleton"
git switch -c feat/a1-resource-core   # Người A; B mở feat/b1-workload
```

Không được thay đổi `src/gpusched/contracts/shared.py` hoặc `contracts/*.md` một phía.
Thay bằng PR có cả hai người review và tăng `CONTRACT_VERSION` khi breaking.

## 6. Trạng thái hiện tại

Đã làm: dataclass/interface chung; các pure helpers EMA/F/reward/blocked ratio;
C1 hash/validator; ScriptedScheduler mock của A, FakeEnvironment mock của B;
6 golden fixtures; boundary checker; test contracts. **Chưa làm:** event simulator,
resource mutation, queue, four baseline policies, load calibration, synthetic/Philly
full generator, networks, A2C trainer, evaluator. TODO và test được đánh dấu rõ.
