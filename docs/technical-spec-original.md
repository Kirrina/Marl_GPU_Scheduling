# MARL GPU Scheduling — Technical Specification V1

**Trạng thái:** V1 design baseline — K1–K10, B1–B6, N1–N5 đã thống nhất; R1–R5 lưu cho V2+.  
**Ngày tổng hợp:** 09/11/2026  
**Mục đích:** Hợp đồng kỹ thuật cho bước hiện thực simulator → policies → training → evaluation.  
**Nguồn:** Các quyết định người dùng xác nhận trong chuỗi review; đối chiếu bản phản biện *Review Technical Design Specification V1* và proposal MARL GPU scheduling.  
**Quy ước:** **FIXED** = quy tắc V1 đã chốt; **TUNE** = giá trị cấu hình thử nghiệm chưa khóa; **DEFER** = ngoài V1.

## 1. Executive specification

| ID | Thành phần | Đặc tả V1 | Trạng thái |
|---|---|---|---|
| S01 | Bài toán | GPU-centric hierarchical MARL scheduling, cấp phát nguyên GPU độc quyền, mỗi job trên đúng một physical node | FIXED |
| S02 | Objective chính | Giảm workload-aware GPU fragmentation | FIXED |
| S03 | Objective phụ | Giảm GPU load imbalance giữa cluster, với trọng số nhỏ hơn | FIXED |
| S04 | Hard constraints | Đủ GPU, CPU, RAM ở cùng node; GPU không chia sẻ, không split một job | FIXED |
| S05 | Topology | Các cluster kết nối logic đầy đủ để Forward; node/cluster đồng nhất trong V1 | FIXED |
| S06 | Cấu hình tham chiếu | 3 clusters × 4 nodes × 4 GPUs/node = 48 GPU; CPU 16 cores và RAM 64 GB/node là giá trị xuất phát | TUNE |
| S07 | GPU demand | $G_J\in\mathcal D_G=\{1,2,4\}$ | FIXED |
| S08 | Scheduler | Management Controller Gate + Management A2C + Shared Cluster A2C + Execution Manager | FIXED |
| S09 | Training | CTDE value critics; separate Management/Cluster policies, two reward streams and two on-policy buffers | FIXED |
| S10 | Simulator | Single-environment discrete-event, đơn vị thời gian giây | FIXED |
| S11 | Evaluation baselines | Chỉ Random Valid, First Fit, Best Fit, RR Cluster + Best Fit (cùng queue policy) | FIXED |
| S12 | Kubernetes | Mục tiêu tích hợp/demo sau khi simulator và policy V1 chạy được; không phải phụ thuộc bắt buộc cho lõi RL | Phạm vi delivery |

## 2. Dữ liệu, trạng thái và ràng buộc

| ID | Đối tượng | Trường/Quy tắc | Bất biến |
|---|---|---|---|
| D01 | Node | `cluster_id, node_id, gpu_capacity, gpu_free, cpu_capacity, cpu_free, ram_capacity, ram_free, running_jobs` | Tất cả free trong `[0,capacity]` |
| D02 | Job | `job_id, arrival_time, gpu_req, cpu_req, ram_req, duration, status, defer_count, retry_count` | `gpu_req in {1,2,4}`, `duration>0` |
| D03 | Eligibility | $eligible(i,n,J)\Leftrightarrow G_{free}\ge G_J \land CPU_{free}\ge CPU_J \land RAM_{free}\ge RAM_J$ | Chỉ có thể Allocate vào eligible node |
| D04 | Job placement | Một job chiếm tài nguyên trên **một** node cho đến completion | Allocate/release chính xác một lần |
| D05 | Queue | FCFS theo thứ tự **được xét**, có tail Requeue; không phải strict head-of-line FCFS trước `PRIORITY_LOCK` | Không duplicate job trong queue |
| D06 | Forward state | `current_cluster, initial_cluster, visited_cluster_ids, forward_count` reset mỗi scheduling attempt | Không quay lại visited; $forward\_count\le K-1$ |
| D07 | Execution Manager | Với job được Allocate ở $t_a$, release ở $t_a+T_J$ | Chỉ engine biết `duration`; không thêm duration/remaining-time cho RL observation |
| D08 | Time ordering | Tại cùng timestamp: xử lý completions → arrivals → một queue sweep | Không retry spin vô hạn cùng timestamp |
| D09 | Queue snapshot | Một sweep chỉ xét các job có trong snapshot đầu sweep, tối đa một lần/job; có thể allocate **nhiều** job khác nhau trong sweep | Requeued job không được xét lại trong sweep |

### 2.1 Workloads

| ID | Loại | Quy tắc | Ghi chú |
|---|---|---|---|
| W01 | Synthetic | Poisson arrival với tốc độ $\lambda_a$; GPU demand thuộc `{1,2,4}`; duration đơn giản có thể đặt hằng số $x$ | Hằng số $x$ là cấu hình thử nghiệm, **không** áp dụng lên Philly trace |
| W02 | Microsoft Philly | Chỉ lấy job GPU demand đúng 1/2/4, single-node, có timestamps hợp lệ, ưu tiên một successful attempt; giữ `submitted_time` làm arrival tương đối, $T_J=end-start$ | Lọc chứ không clamp job GPU >4; ghi tỷ lệ lọc và cách diễn giải attempt |
| W03 | Philly CPU/RAM | CPU/RAM demand của từng job có thể cần sinh/ánh xạ bổ sung theo một phân bố được công bố | Không tuyên bố đây là CPU/RAM nguyên gốc nếu trace job log không có |
| W04 | Alibaba PAI | Cho phép dùng **chỉ sau** preprocessing tương thích V1; GPU fraction / task-instance không được tự ý làm tròn | Không bắt buộc để V1 đầu tiên chạy được |
| W05 | Arrival scaling | Với trace: $t'_J=(t_J-t_0)/s$, $s>0$; giữ nguyên duration từ trace | $s\ne1$ phải ghi rõ là trace-derived time scaling |
| W06 | Offered GPU load | $\rho_{offered}=\lambda_a\mathbb E[G_JT_J]/G_{total}$; cấu hình thử 40%, 65%, 85% | Offered load khác utilization thực tế; không retune riêng theo từng scheduler |
| W07 | Test parity | Mọi scheduler chạy cùng arrival, demand, duration, initial resource, controller/queue semantics | Dùng cùng workload seed; random-policy seeds riêng và báo độ dao động |

## 3. Cost, workload profile và reward

### 3.1 Distribution update và fragmentation

| ID | Ký hiệu | Định nghĩa/Quy tắc |
|---|---|---|
| F01 | $p_d(t)$ | Online arrival EMA: $p_d(t+1)=(1-\alpha)p_d(t)+\alpha\mathbf1(G_{new}=d)$, chỉ cập nhật khi **job mới đến**, không cập nhật Requeue |
| F02 | $p^Q_d$ | Phân bố GPU demand trong waiting queue, **loại job đang xét**; nếu queue trống, fallback $p$ |
| F03 | $\tilde p_d$ | $(p_d+\lambda_Q p^Q_d)/(1+\lambda_Q)$; chụp snapshot cố định trước/sau một attempt |
| F04 | $F(r)$ | $r\sum_{d\in\{1,2,4\}}\tilde p_d\mathbf1(d>r)$ với $r\in\{0,1,2,3,4\}$ |
| F05 | $\Delta F_{i,n}$ | $F(G_{free,i,n}-G_J)-F(G_{free,i,n})$ |
| F06 | $F_{max}$ | $\max_{r\in\{0,1,2,3,4\}}F(r)$ (cùng snapshot) |
| F07 | $\widehat{\Delta F}$ | $\Delta F/\max(F_{max},\varepsilon_F)$ |
| F08 | $L(s)$ | $K^{-1}\sum_i(u_i-\bar u)^2$; $u_i$ là GPU utilization cluster |
| F09 | $\widehat{\Delta L}$ | $\operatorname{clip}((L_{after}-L_{before})/L_{scale},-1,1)$ |
| F10 | $L_{scale}$ | Calibration **một lần** từ $Q_{0.95}(|\Delta L|)$ trên training workload chạy Random Valid; $\max(\cdot,\varepsilon_L)$; cố định trong val/test |
| F11 | Placement cost | $C_{i,n}=(1-w)\widehat{\Delta F}_{i,n}+w\widehat{\Delta L}_{i,n}$; default thử $w\approx0.2$ |
| F12 | Cluster best | $C_i^*=\min_{n\in\mathcal E_i(J)}C_{i,n}$ khi tập eligible không rỗng |
| F13 | Sentinel | $v_i^{eligible}=\mathbf1(|\mathcal E_i(J)|>0)$, $\bar C_i^*=C_i^*$ nếu hợp lệ, `0` nếu không; không truyền `inf`/`NaN` vào mạng |
| F14 | Cost calculator | Tính deterministic features $\Delta F$, $\Delta L$, $C_{i,n}$, $C_i^*$ dùng lại giữa Management và Cluster; không chia sẻ learned embeddings |

**Cảnh báo diễn giải:** $F_{max}$ có thể thay đổi theo EMA; chuẩn hóa cost không bảo đảm telescoping qua nhiều job. Đây là giới hạn V1, không tự thay bằng F-scale cố định.

### 3.2 Reward stream

| ID | Decision | Reward V1 |
|---|---|---|
| RWD01 | Management after final Allocate | $R_M=-C_{i_{final},n_{final}}-\lambda_M\mathbf1(i_{final}\ne i_{init})$ |
| RWD02 | Cluster Allocate | $R_C^{alloc}=-C_{i,n}$ (absolute cost, không dùng $C_i^*$ làm reward) |
| RWD03 | Cluster Forced Forward lần thứ $m\ge1$ | $R_C^{fwd}=-\beta(b^{m-1}-1)$ nếu cluster hiện tại không có node eligible |
| RWD04 | Cluster Proactive Forward lần thứ $m\ge1$ | $R_C^{fwd}=-\beta b^{m-1}$ nếu cluster hiện tại có node eligible |
| RWD05 | Requeue safety | $-\rho P_{requeue}$ Cluster; $-\rho_M P_{requeue}$ Management, chỉ khi RL attempt thất bại dù globally feasible. **Dormant V1**, không tune $\rho,\rho_M$ |
| RWD06 | Discount | Trong một job/Forward: $\gamma_{job}=1$; từ job này sang lần quyết định kế tiếp: $0<\gamma_g<1$ |

## 4. Kiến trúc hệ thống / API contract

| ID | Module | Input | Output / trách nhiệm |
|---|---|---|---|
| A01 | `EventSimulator` | arrivals, completion events | Cập nhật clock và phát các event, single environment |
| A02 | `ExecutionManager` | `Allocate(job,node,t)` | Reserve CPU/RAM/GPU; tạo completion event; giải phóng đúng hạn |
| A03 | `QueueController` | waiting queue, resource state | Queue Sweep, defer, PRIORITY_LOCK, gọi Gate |
| A04 | `ManagementGate` | job + all node resources | `global_eligible`; nếu false → **không** gọi RL, không tạo rollout transition |
| A05 | `CostFeatureCalculator` | job, resources, EMA, queue profile snapshot | eligible masks, pooled deterministic stats, per-node cost/gradients |
| A06 | `ManagementActor` | $o_M=(G_{outer}^{M,A},p_J)$ | Distribution/argmax trên **K cluster**, không mask cluster thiếu tài nguyên cục bộ |
| A07 | `ClusterActor` | $o_C=(H_i,G_{outer}^{C,A},p_J,q_J,\tilde p)$, candidate $\widehat{\Delta F}_{i,n}$ | Allocate local eligible node hoặc Forward eligible/unvisited remote cluster |
| A08 | `ManagementCritic` | $z_{global}^{M,V},p_J,\tilde p$ | $V_M$; encoder riêng |
| A09 | `ClusterCritic` | $z_{global}^{C,V},c_i,p_J,q_J,v_i^{visited},\tilde p$ | $V_C$; $c_i=g_i^{(E_C^V)}$ có $n_i^{eligible},\bar C_i^*,v_i^{eligible}$ |
| A10 | `TrainingEngine` | two rollout buffers | n-step A2C updates sau full macro-step batch; frozen policies trong collection |
| A11 | `EvaluationModule` | trained policies / 4 baselines + same workload | Metrics độc lập, đặc biệt $p_{eval}$ chung |
| A12 | `ExperimentLogger` | trajectories, costs, masks, returns | Diagnostics và báo cáo |

### 4.1 Network ownership và observations

| ID | Quy tắc | Đặc tả |
|---|---|---|
| NN01 | Four independent encoders | $E_M^A,E_M^V,E_C^A,E_C^V$; không chia sẻ learned weights giữa Actor/Critic hoặc Management/Cluster |
| NN02 | Shared Cluster policy | Mọi cluster chia sẻ **cùng Cluster Actor**, tương tự **cùng Cluster Critic**; không có K bộ weights riêng |
| NN03 | Node embedding | $e_{i,n}^{(E)}=E(x_{i,n})$ với raw resource features như GPU/CPU/RAM free/usage |
| NN04 | Cluster summary | $g_i^{(E)}=[\mathrm{MEAN}_n e_{i,n}^{(E)}\Vert\mathrm{MAX}_n e_{i,n}^{(E)}\Vert h_i\Vert u_i\Vert F_i\Vert n_i^{eligible}\Vert\bar C_i^*\Vert v_i^{eligible}]$ |
| NN05 | Histogram | Với node 4GPU, $h_i=(h_0,h_1,h_2,h_3,h_4)$ đếm node có 0..4 GPU free |
| NN06 | Cluster candidate score | Node score $\ell_{i,n}^{alloc}=f_{node}(e_{i,n},p_J,ctx_C,\widehat{\Delta F}_{i,n})$; Forward scores có context/candidate visited flag |
| NN07 | Permutation invariance | Node shared MLP + cluster MEAN/MAX; global cluster pooling; không dùng GNN |
| NN08 | Actor vs Critic scope | Actor nhận local/summary theo S4; Critic nhận pooled global CTDE state; encoder và gradient độc lập |
| NN09 | `visited` vs `eligible` | `v_i^visited` dùng cho Forward state; `v_i^eligible` dùng cho cluster eligibility, tuyệt đối không đặt chung một biến `v_i` |

### 4.2 Masks and forwarding

| ID | Action | Mask / invariant |
|---|---|---|
| MASK01 | Management cluster choice | Khi Gate cho qua, **cả K cluster đều là action khả dụng**, kể cả cluster không có node hợp lệ |
| MASK02 | Cluster Allocate | Chỉ node thuộc cluster hiện tại và đủ đồng thời GPU/CPU/RAM |
| MASK03 | Cluster Forward | Chỉ destination khác hiện tại, chưa visited và có ít nhất một eligible node |
| MASK04 | Max Forward | $forward\_count\le K-1$ (với K=3, tối đa 2 hops); reset per attempt |
| MASK05 | Forced/Proactive | Không có eligible local → chỉ Forward; có eligible local → được Allocate hoặc Proactive Forward |
| MASK06 | Valid-action fallback | Với Gate globally feasible và masking đúng, luôn tồn tại đường Allocate/Forward; thất bại là safety path bất thường cần log |

## 5. Queue lifecycle và scheduling state machine

| ID | Tình huống | Hành vi V1 |
|---|---|---|
| Q01 | Arrival | Enqueue; cập nhật EMA p từ job **mới**; tại timestamp hợp nhất event rồi Queue Sweep |
| Q02 | Gate ineligible, queue size >1 | Đưa job xuống cuối queue đúng một lần trong sweep, `defer_count += 1` |
| Q03 | Gate ineligible, queue size =1 | Giữ chờ release, không spin/tail-move giả |
| Q04 | `defer_count >= max_defer` | Kích hoạt `PRIORITY_LOCK` ở đầu queue; không đưa xuống tail và chặn job phía sau đến khi có thể Allocate |
| Q05 | Locked job still ineligible | Chờ resource-release event; **không** bỏ qua hard constraints; không loop busy-wait |
| Q06 | Permanently unschedulable | Nếu job không thể fit bất kỳ node nào **ngay cả khi node trống toàn bộ**, đánh dấu terminal `UNSCHEDULABLE` rõ ràng; tránh khóa vĩnh viễn hệ thống |
| Q07 | Gate eligible | Một JobTrajectory: Management initial choice → một hoặc nhiều Cluster decisions → terminal Allocate (hoặc safety Requeue) |
| Q08 | `retry_count` | Chỉ tăng khi có actual RL scheduling attempt thất bại; `max_retry` safety code, không đếm Gate deferrals |
| Q09 | Requeue reward | Dormant trong synchronous V1; không tạo training case giả để kích hoạt penalty |
| Q10 | Rollout record | Gate-only checks, defer, waiting và event processing **không** sinh RL transitions |

### 5.1 Controller pseudocode (normative at behavior level)

```text
at each event timestamp t:
    process all completions(t)
    process all arrivals(t)       # EMA update only for fresh arrivals
    snapshot = queue entries present at start of this sweep
    for job in snapshot, at most once per job:
        if priority-locked job exists at head:
            if globally eligible: schedule via RL/baseline and remove on success
            else: stop sweep; wait for future release
            # no later job may overtake a still-blocked locked job
        elif cannot ever fit an empty node:
            mark UNSCHEDULABLE, remove, log
        elif globally eligible:
            one complete SchedulingAttempt; remove upon successful Allocate
        elif queue length <= 1:
            retain at head, stop sweep
        else:
            tail_requeue(job); defer_count += 1
            if defer_count reaches max_defer:
                activate PRIORITY_LOCK at head; stop sweep
    # never repeat this sweep at the same timestamp without a new event
```

**Note on Priority Lock:** Nếu tồn tại locked job trước khi sweep bắt đầu, nó luôn được xét đầu. Các chi tiết cấu trúc dữ liệu phải bảo đảm quy tắc này kể cả khi các job khác đã có trong snapshot.

## 6. Training, episode và bootstrap

| ID | Thành phần | Quy tắc |
|---|---|---|
| TR01 | Episode | Workload gồm N job hữu hạn, environment khởi tạo rỗng; sau khi hết arrival, drain completion/queue đến khi mọi job allocated-completed hoặc có terminal `UNSCHEDULABLE` được ghi nhận |
| TR02 | Macro-step | Một actual RL scheduling attempt/job (Management 1 transition); Cluster có thể >1 transitions vì Forward |
| TR03 | Separate buffers | `ManagementRollout` và `ClusterRollout` là on-policy buffers độc lập; `JobTrajectory` gắn các decision của một attempt; `SchedulingHistory` chỉ log, không replay |
| TR04 | Batch boundary | Gom số **complete macro-steps** trước khi update; ví dụ 128 attempts; không cắt giữa Forward trajectory |
| TR05 | Same-policy bootstrap | Với rollout truncation chưa terminal, lưu/giữ env state rồi chạy các event **không tạo policy transition** tới observation kế tiếp thật sự của **đúng policy**; Critic tương ứng định giá; không invent next_obs |
| TR06 | Terminal bootstrap | True episode terminal: $V_M=V_C=0$ |
| TR07 | Mixed discounts | $\gamma=1$ qua Cluster Forward trong một job; $\gamma_g$ giữa scheduling attempts (không theo physical elapsed seconds) |
| TR08 | n-step target | $G_t^{(n)}=\sum_{k=0}^{n-1}(\prod_{j=0}^{k-1}\gamma_{t+j})r_{t+k}+(\prod_{j=0}^{n-1}\gamma_{t+j})V(s_{t+n})$ nếu chưa terminal; cắt tại done; $A_t=G_t-V(s_t)$ |
| TR09 | Loss | $\mathcal L=\mathcal L_{actor}+c_v\mathcal L_{critic}-c_e\bar H$; $\mathcal L_{actor}=-E[\log\pi(a|o)A]$, $\mathcal L_{critic}=E[(V-G)^2]$ |
| TR10 | Optimizers | Adam, Actor/Critic optimizer riêng và gradient clipping; actor/critic gradients chỉ cập nhật encoder sở hữu tương ứng |
| TR11 | On-policy update | Giữ cả hai policy cố định trong batch collection; sau batch cập nhật cả hai từ own buffers, clear buffers |
| TR12 | Training action | Sample masked categorical policy; entropy chỉ theo hành động valid |
| TR13 | Validation/Test action | Deterministic argmax trên valid actions; freeze weights, nhưng EMA profile theo arrivals vẫn update |
| TR14 | Checkpoint | `latest` và `best` lưu toàn bộ Management + Shared Cluster weights cùng training step; `best` từ validation fragmentation + feasibility checks, không từ test |

### 6.1 Transition schema

| Key | Management transition | Cluster transition |
|---|---|---|
| `policy_id` | `management` | `cluster_shared` |
| `episode_id, attempt_id, job_id` | Bắt buộc | Bắt buộc |
| `actor_observation` | $o_M$ | $o_C$ |
| `critic_state` | $s_M^V$ | $s_C^V$ |
| `action_mask, action` | cluster candidate K | Allocate node / Forward destination |
| `log_prob, value_pred` | $\log\pi_M,V_M$ | $\log\pi_C,V_C$ |
| `reward` | Final Management reward | Allocate reward hoặc Forward reward |
| `discount_to_next` | $\gamma_g$ (hoặc terminal) | `1` if next is same job, $\gamma_g$ if next job |
| `terminal, truncated` | Episode vs rollout split | Episode vs rollout split |
| `next_policy_critic_state` | Next real Management decision | Next real Cluster decision, possibly another cluster |

**Implementation note:** `next_policy_critic_state` chỉ xác định khi quan sát hợp lệ xuất hiện. Phải bảo toàn tính on-policy và sự kiện môi trường khi lookahead, không cập nhật trọng số và không nuốt mất decision tiếp theo. N-step horizon đề xuất đo bằng macro-steps, đi qua tất cả micro-Forward của các macro-step đó.

## 7. Evaluation protocol

| ID | Metric / rule | Definition / kỳ vọng |
|---|---|---|
| EV01 | Benchmark schedulers | MARL vs đúng 4 baselines: Random Valid, First Fit, Best Fit (least remaining GPU), RR cluster + Best Fit |
| EV02 | Frozen policies | Không update mạng trong validation/test; arrival EMA still online as V1 input |
| EV03 | Common fragmentation evaluator | `p_eval(t)` tính từ **cùng chuỗi arrivals bên ngoài**, không dùng model-specific queue, không cung cấp ngược vào policy/reward; dùng chung đo time-average $\bar F_{eval}$ |
| EV04 | Structural fragmentation | $B_4(t)=\frac{\sum_n r_n\mathbf1(0<r_n<4)}{\sum_n r_n+\varepsilon}$; báo time-average độc lập workload profile |
| EV05 | Load imbalance | Time-average $L(s)$, GPU utilization per cluster/global |
| EV06 | Wait/throughput | Waiting time average/p95, riêng nhóm job 4-GPU; makespan, completion count |
| EV07 | Scheduler success | Allocation success, Gate deferrals, RL retries/exhausted (dù thường 0 V1), UNSCHEDULABLE count |
| EV08 | Forward | Total/per-attempt, forced/proactive, match $i_{init}=i_{final}$ |
| EV09 | Cost diagnostic | $C_{init}^*$ nếu valid vs actual $C_{final}$, không coi sentinel 0 là cost thật |
| EV10 | Learning diagnostic | Management/Cluster Actor entropy, valid action count; respective Critic explained variance, return variance zero → N/A; ratio of clipped $\widehat{\Delta L}$ |
| EV11 | Checkpoint selection | Optimize validation $\bar F_{eval}$ với feasibility/deadlock/waiting checks; test giữ sạch |
| EV12 | Split/seeds | Train/validation/test tách biệt; Philly ưu tiên chia theo thời gian; 70/15/15 chỉ gợi ý; multiple workload/random seeds |

**Fairness warning:** Không điều chỉnh arrival riêng cho từng scheduler để chúng đạt cùng GPU utilization; những khác biệt utilization là một phần kết quả.

## 8. Hyperparameters / configuration — chưa khóa giá trị

| Parameter | Giá trị thử nghiệm | Ghi chú |
|---|---|---|
| `cluster_count, nodes_per_cluster, gpus_per_node` | `3, 4, 4` | V1 homogeneous; 48 GPUs |
| `cpu_capacity, ram_capacity` | `16, 64 GB` | Giá trị bắt đầu; non-binding **không** bắt buộc |
| `alpha_ema, lambda_queue` | TBD | $\lambda_Q$ khác $\lambda_M$ penalty management |
| `w` | `0.2` | Ưu tiên fragmentation |
| `epsilon_F, epsilon_L` | Positive, TBD | Numeric stability |
| `lambda_M, beta, b` | TBD, TBD, `b>1` | Forward penalties; `beta>0` |
| `gamma_global` | `(0,1)`, TBD | Discount giữa macro-steps |
| `max_defer, max_retry` | TBD | `max_defer` kích hoạt PRIORITY_LOCK; retry safety |
| `episode_jobs_N` | TBD (gợi ý 500) | Finite arrivals; drain to terminal |
| `rollout_macro_batch` | `128` | Đề xuất, không đóng đinh |
| `n_step_horizon` | `16` macro-steps | Đề xuất; triển khai mixed discount |
| `actor_lr / critic_lr` | `3e-4 / 1e-3` | Adam separate networks |
| `value_coef / entropy_coef` | `0.5 / 0.01` | Không khóa |
| `gradient_clip_norm` | `0.5` | Giá trị thử nghiệm |
| `L_scale` | Random Valid training p95 | Tính được khi chạy calibration, lưu cố định |
| `load_levels` | `40%, 65%, 85%` offered | Có thể thay khi đo workload |
| `synthetic_duration` | Constant `x` seconds | Chỉ synthetic/debug; Philly giữ runtime gốc |
| `trace_time_scale` | `s=1` default | Nếu khác 1 phải báo |

## 9. Acceptance criteria / unit and integration tests

| ID | Test | Pass condition |
|---|---|---|
| TST01 | Resource conservation | Tổng free+allocated đúng capacity mỗi node, không âm, không oversubscription |
| TST02 | One job one node | Không bao giờ split job giữa nodes/clusters |
| TST03 | Gate | Global ineligible: zero actor calls, zero rollout transitions, đúng Queue lifecycle |
| TST04 | Management mask | Có global eligible: tất cả K initial cluster choices vẫn có thể được sample/argmax |
| TST05 | Cluster mask | Allocate luôn valid CPU/RAM/GPU; Forward chỉ to unvisited/eligible other clusters |
| TST06 | Forward bound | Không quá K−1 Forward; visited reset mỗi attempt |
| TST07 | Cost | Snapshot before/after cùng $\tilde p$; negative/positive $\Delta F$ đúng công thức; no NaN/inf |
| TST08 | Sentinel | Empty cluster $\bar C_i^*=0$, $v_i^{eligible}=0$; không nhầm 0 cost thật |
| TST09 | Queue sweep | Một job tối đa một xét/sweep; tail requeue đúng một lần; không lặp tại cùng timestamp |
| TST10 | Priority lock | Locked head không tail requeue, không bị vượt; unlock chỉ sau allocation/explicit impossible terminal |
| TST11 | Impossibility guard | Job không fit node trống được xử lý UNSCHEDULABLE; không deadlock đến vô hạn |
| TST12 | Completion | Exact release at allocate timestamp + duration; các job chạy đồng thời release đúng |
| TST13 | Rollout isolation | Management 1 transition/attempt; Cluster 1+; Gate-only 0; không dùng experience replay |
| TST14 | Bootstrap | Terminal 0; truncated uses next valid same-policy state, skip event-only actions; mixed discount đúng |
| TST15 | Network sharing | Shared Cluster weights across all clusters; independent four encoders and gradients |
| TST16 | Eval fairness | Identical workload/initial resources/queue policy between MARL and 4 baselines |
| TST17 | Metrics isolation | $p_{eval}$ only external arrivals, does not feed back to scheduler |
| TST18 | Trace preprocessing | Keep {1,2,4}, valid timestamp/single-node; runtime kept, filtered records accounted |
| TST19 | Requeue safety | Dormant RL failure paths not artificially activated in synchronous eligible environment |
| TST20 | Checkpoints | Save and restore complete joint Management/Cluster model; deterministic eval under same seed |

## 10. Implementation sequence (sẵn sàng sang hiện thực)

| Phase | Deliverable | Bắt buộc pass |
|---|---|---|
| P0 — Schema & configs | Job/Node/Cluster, event types, config, invariant validators | TST01–02 |
| P1 — Discrete-event simulator | arrivals, execution/completion, queue sweep, Gate, PRIORITY_LOCK | TST03, TST09–12 |
| P2 — Cost & features | EMA, queue profile, F/ΔF, L/ΔL, `CostFeatureCalculator`, masks | TST04–08 |
| P3 — Baselines | Four baselines share simulator/controller | TST16 |
| P4 — MARL networks | 4 encoders, Management Actor/Critic, Shared Cluster Actor/Critic | TST15 |
| P5 — Training engine | JobTrajectory, two buffers, n-step, bootstrap, A2C, checkpoint | TST13–14, TST20 |
| P6 — Workload & evaluation | Synthetic + filtered Philly, calibration, fair metrics/logs | TST17–19, TST16 |
| P7 — Experiment/report | multi-seed, load levels, validation/test, plots and findings | All tests + reproducible configs |

## 11. V2+ backlog / deferred risk registry

| Code | Trạng thái | Vấn đề/khả năng nghiên cứu sau V1 |
|---|---|---|
| R1 | DEFER | Fragmentation reward không trực tiếp phạt gate waiting của large-GPU jobs; xem xét alternate reward/ablation |
| R2 | DEFER | Proactive Forward có thể về gần zero do penalties và Manager biết cluster best-cost; consider No-Forward ablation |
| R3 | DEFER | Management reward nhiễu vì phụ thuộc node do Cluster Agent chọn; consider cluster-level reward shaping |
| R4 | DEFER | $\gamma_g$ theo macro-step không phải elapsed time; consider continuous-time discount |
| R5 | DEFER | Single environment có phương sai gradient; consider parallel env/structured sampling |
| V2-A | DEFER | Heterogeneous clusters, capacities >4, variable node counts / adaptive histograms |
| V2-B | DEFER | Multi-resource fragmentation và stranded GPU optimization: GPU/CPU/RAM |
| V2-C | DEFER | Remaining-time features, queue-aware critics, complex multi-queue/workload scheduling |
| V2-D | DEFER | PPO, advanced reward normalization, Requeue penalty training, Greedy-C/No-Forward ablations |

## 12. Explicit non-goals and unresolved parameters

- **Không trong V1:** GNN, PPO, parallel environment, multi-resource fragmentation reward, Greedy-C baseline, No-Forward ablation, thêm feature remaining-time vào policy, giả lập forward network latency, cố ý sinh RL failures để tune requeue penalties.
- **Chưa khóa:** $\alpha$, $\lambda_Q$, $\lambda_M$, $\beta$, $b$, $\gamma_g$, `max_defer`, `max_retry`, $N$, learning rates, batch size, horizon, clip norm, trace time-scaling và CPU/RAM demand generator. Chúng là **config/tuning**, không phải các quyết định kiến trúc mới.
- **Giới hạn mô hình:** Homogeneous 4GPU/node, exclusive GPU, synchronous deterministic allocation, workload filtered; không khẳng định đại diện toàn bộ hệ Kubernetes hoặc datacenter thực tế.
- **Rủi ro nghiên cứu R1–R5:** ghi nhận để thảo luận V2+, không lặng lẽ áp dụng giải pháp vào V1.
