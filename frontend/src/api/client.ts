import {
  Asset,
  FactoryGraphData,
  Incident,
  AssetTelemetryData,
  StructuredInvestigation,
  SimulationResult,
  DocumentChunk,
  ModelMetrics,
} from '../types';

const API_BASE = '/api/v1';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let errorMsg = `HTTP Error ${response.status}: ${response.statusText}`;
    try {
      const errBody = await response.json();
      if (errBody?.error?.message) {
        errorMsg = errBody.error.message;
      }
    } catch {
      // Keep statusText
    }
    throw new Error(errorMsg);
  }

  return response.json() as Promise<T>;
}

export const api = {
  // Health
  getHealth: () => request<{ status: string; app: string; dependencies: Record<string, string> }>('/health'),

  // Factory Overview
  getOverview: () => request<any>('/overview'),

  // Factory Assets & Graph
  getAssets: (params?: { asset_type?: string; status?: string }) => {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return request<Asset[]>(`/assets${query ? `?${query}` : ''}`);
  },
  getAsset: (id: string) => request<Asset>(`/assets/${id}`),
  getAssetNeighbors: (id: string) => request<any>(`/assets/${id}/neighbors`),
  getAssetTelemetry: (id: string, hours: number = 24) =>
    request<AssetTelemetryData>(`/assets/${id}/telemetry?hours=${hours}`),
  getFactoryGraph: () => request<FactoryGraphData>('/factory/graph'),

  // Incidents & Agent Investigation
  getIncidents: (params?: { status?: string; asset_id?: string }) => {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return request<Incident[]>(`/incidents${query ? `?${query}` : ''}`);
  },
  triggerDemoIncident: (data: { asset_id?: string; scenario?: string; severity?: string }) =>
    request<Incident>('/incidents/demo-trigger', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  triggerInvestigation: (incidentId: string) =>
    request<StructuredInvestigation>(`/incidents/${incidentId}/investigations`, {
      method: 'POST',
      body: JSON.stringify({}),
    }),
  getInvestigation: (investigationId: string) =>
    request<StructuredInvestigation>(`/investigations/${investigationId}`),

  // Digital Twin Simulation
  runSimulation: (data: {
    target_asset_id: string;
    scenario_type: string;
    duration_minutes: number;
    derating_factor?: number;
    repair_cost_estimate?: number;
    incident_id?: string;
  }) =>
    request<SimulationResult>('/simulations', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  getSimulation: (id: string) => request<SimulationResult>(`/simulations/${id}`),

  // Action Recommendations
  rankRecommendations: (data: {
    asset_id: string;
    incident_id?: string;
    weight_risk?: number;
    weight_downtime?: number;
    weight_direct_cost?: number;
    weight_uncertainty?: number;
  }) =>
    request<any>('/recommendations/rank', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Documents & RAG
  getDocuments: () => request<any[]>('/documents'),
  ingestDocuments: () =>
    request<{ status: string; total_documents: number; total_chunks: number; message: string }>(
      '/documents/ingest-demo',
      { method: 'POST' }
    ),

  // Model Evaluation & Card
  getModelEvaluation: () => request<ModelMetrics>('/model/evaluation'),
};
