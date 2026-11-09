import json
from pathlib import Path
import pytest
from gpusched.sim.cost import delta_f_hat, f_max, combined_profile
from gpusched.sim.models import Node
from gpusched.sim.observations import histogram_free_gpus

FIXTURES=Path(__file__).resolve().parents[2]/"fixtures"
DATA=json.loads((FIXTURES/"golden_cases.json").read_text(encoding="utf8"))["cases"]


def _nodes(frees):
    return [Node(0,i,4,16,64,g,16,64) for i,g in enumerate(frees)]

@pytest.mark.parametrize("case",DATA,ids=[x["id"] for x in DATA])
def test_assignment_six_scenarios(case):
    input=case["input"]; expected=case["expected"]
    match case["id"]:
        case "G01":
            assert histogram_free_gpus(_nodes(input["gpu_free"]))==pytest.approx(expected["normalized_histogram"])
            assert sum(x>=input["gpu_req"] for x in input["gpu_free"])==expected["eligible_gpu_nodes"]
            assert 1-sum(input["gpu_free"])/(4*4)==expected["cluster_gpu_utilization"]
        case "G02":
            assert histogram_free_gpus(_nodes(input["gpu_free"]))==pytest.approx(expected["normalized_histogram"])
            assert 1-sum(input["gpu_free"])/16==expected["cluster_gpu_utilization"]
            assert sum(input["gpu_free"])/4==expected["mean_free"]
            assert max(input["gpu_free"])==expected["max_free"]
        case "G03":
            eligible=sum(x>=input["gpu_req"] for x in input["gpu_free"])
            assert eligible==expected["eligible_nodes"]
            assert expected["best_cost_or_zero"]==0.0 and expected["v_eligible"]==0.0
        case "G04":
            mask=[i not in input["visited"] and input["destination_eligible"][i]
                  for i in range(input["K"])]
            assert mask==expected["forward_mask"]
            assert input["forward_count"]/(input["K"]-1)==expected["q_j"]
        case "G05":
            profile=input["arrival_profile"] # p^Q falls back to EMA when queue empty
            assert combined_profile(profile,profile,input["lambda_queue"])==pytest.approx(expected["p_tilde"])
        case "G06":
            p=input["p_tilde"]
            assert f_max(p)==pytest.approx(expected["f_max"])
            assert delta_f_hat(4,4,p)==pytest.approx(expected["delta_f_hat_job4_from4"])
            assert delta_f_hat(4,2,p)==pytest.approx(expected["delta_f_hat_job2_from4"])
            assert delta_f_hat(3,1,p)==pytest.approx(expected["delta_f_hat_job1_from3"])
