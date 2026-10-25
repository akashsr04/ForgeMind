import pytest
from app.domain.recommendations.ranker import rank_candidate_actions, ACTION_CATALOG
from app.schemas.recommendations import ActionRankingRequest


def test_ranking_sorts_highest_score_first():
    motor_id = "11111111-1111-1111-1111-111111111102"
    req = ActionRankingRequest(
        asset_id=motor_id,
        weight_risk=100.0,
        weight_downtime=0.5,
        weight_direct_cost=0.1,
        weight_uncertainty=20.0,
    )
    res = rank_candidate_actions("motor", req)
    assert len(res.ranked_actions) > 0

    # Verify descending score order
    scores = [a.net_score for a in res.ranked_actions]
    assert scores == sorted(scores, reverse=True)

    # First recommendation should have valid score components
    top = res.ranked_actions[0]
    assert top.score_components.net_score == top.net_score
    assert top.is_advisory is True


def test_custom_weights_change_preference():
    motor_id = "11111111-1111-1111-1111-111111111102"
    # When downtime penalty is extremely high, derating or monitoring ranks above full repair
    req_high_downtime = ActionRankingRequest(
        asset_id=motor_id,
        weight_risk=50.0,
        weight_downtime=5.0,  # 10x penalty
        weight_direct_cost=0.1,
        weight_uncertainty=10.0,
    )
    res = rank_candidate_actions("motor", req_high_downtime)
    # The 90-minute repair should be penalized severely compared to derate (0 min) or inspect (20 min)
    repair_action = next(a for a in res.ranked_actions if a.action_type == "repair")
    inspect_action = next(a for a in res.ranked_actions if a.action_type == "inspect")
    assert inspect_action.net_score > repair_action.net_score
