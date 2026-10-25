export interface Asset {
  id: string;
  name: string;
  asset_type: string;
  location?: string;
  criticality: number;
  status: 'operational' | 'degraded' | 'offline' | 'maintenance';
  metadata_json?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

export interface GraphNode {
  id: string;
  name: string;
  asset_type: string;
  location?: string;
  criticality: number;
  status: string;
  active_incidents_count: number;
  current_risk_score?: number;
  metadata?: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relationship_type: string;
  weight: number;
}

export interface FactoryGraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  total_assets: number;
  operational_count: number;
  degraded_count: number;
  offline_count: number;
}

export interface Incident {
  id: string;
  asset_id: string;
  title: string;
  description?: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'investigating' | 'mitigated' | 'resolved';
  trigger_type: string;
  detected_at: string;
  resolved_at?: string;
  context_json?: Record<string, any>;
  is_synthetic: boolean;
}

export interface SensorSummary {
  sensor_name: string;
  unit: string;
  current_value: number;
  min_value: number;
  max_value: number;
  mean_value: number;
  std_value: number;
  reading_count: number;
  is_anomalous: boolean;
  status_label: string;
}

export interface TelemetryReading {
  id: string;
  asset_id: string;
  sensor_name: string;
  value: number;
  unit: string;
  observed_at: string;
  source: string;
}

export interface AssetTelemetryData {
  asset_id: string;
  window_hours: number;
  readings: TelemetryReading[];
  summaries: Record<string, SensorSummary>;
}

export interface UncertaintyDetail {
  method: string;
  lower?: number;
  upper?: number;
  limitations: string[];
}

export interface RiskAssessment {
  risk_score: number;
  estimated_probability?: number | null;
  reliability_status: 'high' | 'medium' | 'low' | 'insufficient_evidence';
  uncertainty: UncertaintyDetail;
  explanation?: string;
}

export interface DocumentChunk {
  chunk_id: string;
  document_id: string;
  title: string;
  section: string;
  asset_type: string;
  content: string;
  similarity_score?: number;
  metadata: Record<string, any>;
}

export interface Hypothesis {
  label: string;
  supporting_evidence_refs: string[];
  counter_evidence: string[];
  status: string;
  rationale?: string;
}

export interface ActionScoreComponents {
  risk_reduction_term: number;
  downtime_cost_term: number;
  direct_cost_term: number;
  production_loss_term: number;
  uncertainty_penalty_term: number;
  net_score: number;
}

export interface ScoredAction {
  action_type: string;
  title: string;
  rationale: string;
  net_score: number;
  score_components: ActionScoreComponents;
  uncertainty_summary: Record<string, any>;
  evidence_refs: string[];
  is_advisory: boolean;
}

export interface AuditEvent {
  timestamp: string;
  step: string;
  action: string;
  outcome: string;
  details?: Record<string, any>;
}

export interface StructuredInvestigation {
  investigation_id: string;
  incident_id: string;
  status: string;
  summary: string;
  risk: RiskAssessment;
  hypotheses: Hypothesis[];
  recommendations: ScoredAction[];
  retrieved_evidence: DocumentChunk[];
  missing_information: string[];
  audit_events: AuditEvent[];
  safety_disclaimer: string;
}

export interface MetricSnapshot {
  throughput_units_per_hour: number;
  total_factory_capacity_pct: number;
  active_bottlenecks: string[];
  estimated_downtime_hours: number;
  estimated_financial_cost: number;
}

export interface SimulationResult {
  id?: string;
  incident_id?: string;
  target_asset_id: string;
  scenario_type: string;
  duration_minutes: number;
  baseline: MetricSnapshot;
  scenario: MetricSnapshot;
  delta_throughput: number;
  delta_cost: number;
  delta_downtime_hours: number;
  affected_asset_ids: string[];
  propagation_path: string[];
  assumptions: string[];
  is_synthetic: boolean;
  created_at?: string;
}

export interface ModelMetrics {
  dataset: {
    type: string;
    total_instances: number;
    train_samples: number;
    validation_samples: number;
    test_samples: number;
    anomaly_rate: number;
    split_method: string;
  };
  baseline_model: {
    model_name: string;
    auroc: number;
    accuracy: number;
    f1_score: number;
    brier_score: number;
    description: string;
  };
  gnn_model: {
    model_name: string;
    auroc: number;
    accuracy: number;
    f1_score: number;
    brier_score: number;
    description: string;
  };
  uncertainty_evaluation: {
    method: string;
    nominal_coverage_target: number;
    empirical_coverage_achieved: number;
    interval_half_width_q_hat: number;
    brier_score_calibration: number;
  };
  limitations_and_caveats: string[];
}
