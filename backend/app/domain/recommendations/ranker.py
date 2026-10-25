from typing import List, Dict, Any, Optional
from app.schemas.recommendations import (
    CandidateAction,
    ActionScoreComponents,
    ScoredActionResponse,
    ActionRankingRequest,
    ActionRankingResponse,
)

# Standard catalog of maintenance candidate actions by asset type
ACTION_CATALOG: Dict[str, List[CandidateAction]] = {
    "motor": [
        CandidateAction(
            action_type="inspect",
            title="Acoustic Ultrasound & Thermographic Bearing Inspection",
            rationale="Isolate specific bearing race defects and verify grease degradation without disassembly.",
            estimated_risk_reduction=0.35,
            estimated_downtime_minutes=20.0,
            estimated_direct_cost=80.0,
            production_impact_score=0.15,
            uncertainty_level="low",
        ),
        CandidateAction(
            action_type="derate",
            title="Derate Motor Operating Frequency to 42 Hz (30% Load Shed)",
            rationale="Reduces mechanical shear stresses and slows bearing temperature rise while keeping the line running.",
            estimated_risk_reduction=0.45,
            estimated_downtime_minutes=0.0,
            estimated_direct_cost=0.0,
            production_impact_score=0.30,
            uncertainty_level="low",
        ),
        CandidateAction(
            action_type="repair",
            title="Planned Drive-End Bearing Replacement (SKF 6312)",
            rationale="Permanently resolves bearing spalling defect and restores nominal operating reliability.",
            estimated_risk_reduction=0.95,
            estimated_downtime_minutes=90.0,
            estimated_direct_cost=450.0,
            production_impact_score=0.90,
            uncertainty_level="low",
        ),
        CandidateAction(
            action_type="monitor",
            title="Increase Telemetry Polling Rate & Continue Monitoring",
            rationale="Passive monitoring with 1-minute alert thresholds; carries severe risk of catastrophic seizure.",
            estimated_risk_reduction=0.05,
            estimated_downtime_minutes=0.0,
            estimated_direct_cost=0.0,
            production_impact_score=0.05,
            uncertainty_level="high",
        ),
    ],
    "pump": [
        CandidateAction(
            action_type="inspect",
            title="Suction Strainer & Cavitation Acoustic Check",
            rationale="Inspect suction basket for metal chips and verify fluid inlet pressure.",
            estimated_risk_reduction=0.40,
            estimated_downtime_minutes=15.0,
            estimated_direct_cost=50.0,
            production_impact_score=0.10,
            uncertainty_level="low",
        ),
        CandidateAction(
            action_type="repair",
            title="Impeller & Mechanical Seal Replacement",
            rationale="Replaces worn impeller vanes and restores nominal 55 L/min coolant flow rate.",
            estimated_risk_reduction=0.90,
            estimated_downtime_minutes=75.0,
            estimated_direct_cost=280.0,
            production_impact_score=0.70,
            uncertainty_level="low",
        ),
    ],
    "general": [
        CandidateAction(
            action_type="inspect",
            title="General Preventive Diagnostic Inspection",
            rationale="Perform visual, electrical, and vibration check of asset components.",
            estimated_risk_reduction=0.30,
            estimated_downtime_minutes=30.0,
            estimated_direct_cost=100.0,
            production_impact_score=0.20,
            uncertainty_level="medium",
        ),
        CandidateAction(
            action_type="monitor",
            title="Observe Asset State & Tighten Telemetry Thresholds",
            rationale="Maintain current operating setpoints while observing sensor trends.",
            estimated_risk_reduction=0.05,
            estimated_downtime_minutes=0.0,
            estimated_direct_cost=0.0,
            production_impact_score=0.0,
            uncertainty_level="high",
        ),
    ],
}


def score_action(
    action: CandidateAction,
    w_risk: float = 100.0,
    w_downtime: float = 0.5,
    w_direct_cost: float = 0.1,
    w_uncertainty: float = 20.0,
    evidence_refs: Optional[List[str]] = None,
) -> ScoredActionResponse:
    """
    Transparent weighted multi-criteria decision ranker.
    Score = w_risk * risk_reduction - w_downtime * downtime_cost - w_cost * direct_cost - w_uncertainty * penalty
    """
    uncertainty_multiplier = {
        "low": 0.2,
        "medium": 0.5,
        "high": 1.0,
    }.get(action.uncertainty_level.lower(), 0.5)

    risk_term = round(w_risk * action.estimated_risk_reduction, 2)
    downtime_term = round(w_downtime * action.estimated_downtime_minutes, 2)
    cost_term = round(w_direct_cost * action.estimated_direct_cost, 2)
    prod_term = round(15.0 * action.production_impact_score, 2)
    uncertainty_term = round(w_uncertainty * uncertainty_multiplier, 2)

    net_score = round(risk_term - downtime_term - cost_term - prod_term - uncertainty_term, 2)

    components = ActionScoreComponents(
        risk_reduction_term=risk_term,
        downtime_cost_term=-downtime_term,
        direct_cost_term=-cost_term,
        production_loss_term=-prod_term,
        uncertainty_penalty_term=-uncertainty_term,
        net_score=net_score,
    )

    return ScoredActionResponse(
        action_type=action.action_type,
        title=action.title,
        rationale=action.rationale,
        net_score=net_score,
        score_components=components,
        uncertainty_summary={
            "level": action.uncertainty_level,
            "penalty_applied": uncertainty_term,
            "confidence_status": "reliable" if action.uncertainty_level == "low" else "advisory",
        },
        evidence_refs=evidence_refs or [],
        is_advisory=True,
    )


def rank_candidate_actions(
    asset_type: str,
    request: ActionRankingRequest,
    evidence_refs: Optional[List[str]] = None,
) -> ActionRankingResponse:
    candidates = request.candidate_actions
    if not candidates:
        candidates = ACTION_CATALOG.get(asset_type.lower(), ACTION_CATALOG["general"])

    scored_actions = [
        score_action(
            action=c,
            w_risk=request.weight_risk,
            w_downtime=request.weight_downtime,
            w_direct_cost=request.weight_direct_cost,
            w_uncertainty=request.weight_uncertainty,
            evidence_refs=evidence_refs,
        )
        for c in candidates
    ]

    scored_actions.sort(key=lambda a: a.net_score, reverse=True)

    ranking_notes = [
        f"Ranked {len(scored_actions)} candidate actions using configurable multi-criteria weights.",
        f"Weights: w_risk={request.weight_risk}, w_downtime={request.weight_downtime}, w_cost={request.weight_direct_cost}, w_uncertainty={request.weight_uncertainty}.",
        "Scores balance immediate downtime and repair cost against long-term operational risk reduction.",
    ]

    return ActionRankingResponse(
        asset_id=request.asset_id,
        incident_id=request.incident_id,
        ranked_actions=scored_actions,
        ranking_notes=ranking_notes,
    )
