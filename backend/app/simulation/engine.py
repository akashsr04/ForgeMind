from typing import List, Dict, Any, Tuple
from app.schemas.simulations import MetricSnapshot, SimulationResponse
from app.infrastructure.db.models import Asset, AssetEdge


class DigitalTwinEngine:
    """
    Deterministic Digital Twin simulator for the ForgeMind factory.
    Simulates production flows, dependency cascade effects, downtime, and financial cost.
    """

    FACTORY_DOWNTIME_COST_PER_HOUR = 1500.0  # Industry standard benchmark for mid-scale assembly

    def __init__(self, assets: List[Asset], edges: List[AssetEdge]):
        self.assets = {a.id: a for a in assets}
        self.edges = edges

        # Adjacency maps
        self.downstream: Dict[str, List[Tuple[str, str, float]]] = {}
        self.upstream: Dict[str, List[Tuple[str, str, float]]] = {}

        for a_id in self.assets:
            self.downstream[a_id] = []
            self.upstream[a_id] = []

        for e in self.edges:
            if e.source_asset_id in self.downstream and e.target_asset_id in self.assets:
                self.downstream[e.source_asset_id].append((e.target_asset_id, e.relationship_type, e.weight))
            if e.target_asset_id in self.upstream and e.source_asset_id in self.assets:
                self.upstream[e.target_asset_id].append((e.source_asset_id, e.relationship_type, e.weight))

    def _get_nominal_capacity(self, asset: Asset) -> float:
        if asset.asset_type == "feeder":
            return 350.0
        elif asset.asset_type == "conveyor":
            return 320.0
        elif asset.asset_type == "motor":
            return 320.0  # drives conveyor
        elif asset.asset_type == "pump":
            return 350.0  # auxiliary
        elif asset.asset_type == "cnc":
            return 300.0  # Primary bottleneck
        elif asset.asset_type == "inspection":
            return 310.0
        elif asset.asset_type == "packaging":
            return 330.0
        return 300.0

    def compute_factory_metrics(
        self, asset_capacities: Dict[str, float], duration_hours: float, direct_intervention_cost: float = 0.0
    ) -> Tuple[MetricSnapshot, List[str]]:
        """
        Calculates end-to-end production throughput based on min-capacity propagation
        along the critical manufacturing path.
        """
        # Critical production flow: Feeder -> Conveyor -> CNC -> Inspection -> Packaging
        # Motor drives Conveyor; Pump cools CNC & Motor.

        # Effective capacities considering dependencies
        effective_caps: Dict[str, float] = {}

        for a_id, cap in asset_capacities.items():
            effective_caps[a_id] = cap

        # 1. Motor M-101 drives Conveyor C-101
        for a_id, asset in self.assets.items():
            if asset.asset_type == "conveyor":
                # Find driving motor
                for up_id, rel, weight in self.upstream.get(a_id, []):
                    if rel == "drives":
                        motor_cap = effective_caps.get(up_id, 1.0)
                        effective_caps[a_id] = min(effective_caps[a_id], motor_cap)

        # 2. Coolant pump cools CNC
        for a_id, asset in self.assets.items():
            if asset.asset_type == "cnc":
                for up_id, rel, weight in self.upstream.get(a_id, []):
                    if rel == "cools":
                        pump_cap = effective_caps.get(up_id, 1.0)
                        if pump_cap < 0.3:  # Severe coolant starvation trips thermal interlock
                            effective_caps[a_id] = 0.0

        # Critical path assets in topological order
        path_types = ["feeder", "conveyor", "cnc", "inspection", "packaging"]
        critical_assets = []
        for ptype in path_types:
            for a_id, asset in self.assets.items():
                if asset.asset_type == ptype:
                    critical_assets.append(a_id)
                    break

        # Flow through critical path
        min_throughput = 300.0  # Default nominal bottleneck
        bottlenecks = []

        if critical_assets:
            path_caps = [
                (a_id, self._get_nominal_capacity(self.assets[a_id]) * effective_caps.get(a_id, 1.0))
                for a_id in critical_assets
            ]
            min_throughput = min(c for _, c in path_caps)
            bottlenecks = [self.assets[a_id].name for a_id, c in path_caps if abs(c - min_throughput) < 1e-3]

        nominal_baseline = 300.0
        capacity_pct = round(max(0.0, min(100.0, (min_throughput / nominal_baseline) * 100.0)), 1)
        lost_capacity_fraction = max(0.0, 1.0 - (min_throughput / nominal_baseline))
        downtime_hours = round(duration_hours * lost_capacity_fraction, 2)
        downtime_cost = round(downtime_hours * self.FACTORY_DOWNTIME_COST_PER_HOUR, 2)
        total_cost = round(direct_intervention_cost + downtime_cost, 2)

        snapshot = MetricSnapshot(
            throughput_units_per_hour=round(min_throughput, 1),
            total_factory_capacity_pct=capacity_pct,
            active_bottlenecks=bottlenecks,
            estimated_downtime_hours=downtime_hours,
            estimated_financial_cost=total_cost,
        )
        return snapshot, bottlenecks

    def run_simulation(
        self,
        target_asset_id: str,
        scenario_type: str,
        duration_minutes: float = 60.0,
        derating_factor: float = 0.5,
        repair_cost_estimate: float = 500.0,
        incident_id: str = None,
    ) -> SimulationResponse:
        """
        Executes a deterministic what-if scenario against the digital twin snapshot.
        """
        duration_hours = max(0.1, duration_minutes / 60.0)

        # Baseline: All assets at normal operational capacity
        baseline_caps = {a_id: 1.0 for a_id in self.assets}
        baseline_metrics, _ = self.compute_factory_metrics(baseline_caps, duration_hours, direct_intervention_cost=0.0)

        # Scenario modification
        scenario_caps = {a_id: 1.0 for a_id in self.assets}
        direct_cost = 0.0
        affected_assets = [target_asset_id]
        assumptions = [
            f"Simulation horizon: {duration_minutes:.0f} minutes.",
            f"Nominal factory bottleneck throughput is 300 units/hour.",
            f"Factory downtime valuation is ${self.FACTORY_DOWNTIME_COST_PER_HOUR:.0f}/hour.",
        ]

        if scenario_type == "outage":
            scenario_caps[target_asset_id] = 0.0
            assumptions.append(f"Target asset '{self.assets[target_asset_id].name}' is completely offline (0% capacity).")
        elif scenario_type == "derating":
            factor = max(0.0, min(1.0, derating_factor))
            scenario_caps[target_asset_id] = factor
            assumptions.append(f"Target asset '{self.assets[target_asset_id].name}' derated to {factor*100:.0f}% capacity to alleviate thermal stress.")
        elif scenario_type == "inspection":
            scenario_caps[target_asset_id] = 0.0  # Brief stoppage during acoustic inspection
            direct_cost = 100.0  # Technician inspection fee
            assumptions.append("Visual and ultrasonic vibration check conducted; asset stopped during sensor placement.")
        elif scenario_type == "repair":
            scenario_caps[target_asset_id] = 0.0
            direct_cost = repair_cost_estimate
            assumptions.append(f"Complete mechanical replacement / overhaul with direct parts cost of ${repair_cost_estimate:.2f}.")
        else:
            scenario_caps[target_asset_id] = 1.0
            assumptions.append("Monitoring only; baseline parameters maintained.")

        # Propagate downstream effects
        queue = [target_asset_id]
        propagation_path = [self.assets[target_asset_id].name]
        visited = {target_asset_id}

        while queue:
            curr = queue.pop(0)
            for down_id, rel, weight in self.downstream.get(curr, []):
                if down_id not in visited:
                    visited.add(down_id)
                    affected_assets.append(down_id)
                    propagation_path.append(f"{self.assets[down_id].name} (via {rel})")
                    queue.append(down_id)

        scenario_metrics, _ = self.compute_factory_metrics(scenario_caps, duration_hours, direct_intervention_cost=direct_cost)

        return SimulationResponse(
            incident_id=incident_id,
            target_asset_id=target_asset_id,
            scenario_type=scenario_type,
            duration_minutes=duration_minutes,
            baseline=baseline_metrics,
            scenario=scenario_metrics,
            delta_throughput=round(scenario_metrics.throughput_units_per_hour - baseline_metrics.throughput_units_per_hour, 1),
            delta_cost=round(scenario_metrics.estimated_financial_cost - baseline_metrics.estimated_financial_cost, 2),
            delta_downtime_hours=round(scenario_metrics.estimated_downtime_hours - baseline_metrics.estimated_downtime_hours, 2),
            affected_asset_ids=affected_assets,
            propagation_path=propagation_path,
            assumptions=assumptions,
            is_synthetic=True,
        )
