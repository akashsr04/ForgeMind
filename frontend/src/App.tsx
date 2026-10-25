import React, { useState, useEffect } from 'react';
import { Sidebar, ViewType } from './components/Sidebar';
import { TopBar } from './components/TopBar';
import { OverviewView } from './features/overview/OverviewView';
import { FactoryGraphView } from './features/factory-graph/FactoryGraphView';
import { AssetDetailModal } from './features/assets/AssetDetailModal';
import { IncidentInvestigationView } from './features/incidents/IncidentInvestigationView';
import { DigitalTwinLabView } from './features/simulation/DigitalTwinLabView';
import { EvidenceView } from './features/evidence/EvidenceView';
import { ModelEvaluationView } from './features/evaluation/ModelEvaluationView';
import { api } from './api/client';
import { FactoryGraphData } from './types';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewType>('overview');
  const [overviewData, setOverviewData] = useState<any>(null);
  const [graphData, setGraphData] = useState<FactoryGraphData | null>(null);
  const [selectedAssetIdModal, setSelectedAssetIdModal] = useState<string | null>(null);
  const [activeInvestigationIncidentId, setActiveInvestigationIncidentId] = useState<string | null>(null);
  const [simulationAssetId, setSimulationAssetId] = useState<string | null>(null);
  const [simulationScenarioType, setSimulationScenarioType] = useState<string | null>(null);
  const [isTriggering, setIsTriggering] = useState<boolean>(false);

  useEffect(() => {
    loadOverviewAndGraph();
    const interval = setInterval(loadOverviewAndGraph, 10000); // 10s polling
    return () => clearInterval(interval);
  }, []);

  async function loadOverviewAndGraph() {
    try {
      const [ov, gr] = await Promise.all([api.getOverview(), api.getFactoryGraph()]);
      setOverviewData(ov);
      setGraphData(gr);
    } catch (err) {
      console.error('Failed to refresh data', err);
    }
  }

  async function handleTriggerDemoIncident() {
    setIsTriggering(true);
    try {
      const inc = await api.triggerDemoIncident({
        asset_id: '11111111-1111-1111-1111-111111111102',
        scenario: 'bearing_wear_overheating',
        severity: 'high',
      });
      await loadOverviewAndGraph();
      setActiveInvestigationIncidentId(inc.id);
      setCurrentView('investigation');
    } catch (err) {
      console.error('Failed to trigger demo incident', err);
    } finally {
      setIsTriggering(false);
    }
  }

  function handleInvestigate(incidentId: string) {
    setActiveInvestigationIncidentId(incidentId);
    setCurrentView('investigation');
  }

  function handleNavigateToSimulation(assetId: string, actionType: string) {
    setSimulationAssetId(assetId);
    let mappedScenario = 'derating';
    if (actionType === 'inspect') mappedScenario = 'inspection';
    else if (actionType === 'repair' || actionType === 'replace') mappedScenario = 'repair';
    else if (actionType === 'monitor') mappedScenario = 'outage';
    setSimulationScenarioType(mappedScenario);
    setCurrentView('digital-twin');
  }

  const viewTitles: Record<ViewType, string> = {
    overview: 'Factory Operations Overview',
    graph: 'Factory Asset Topology & Dependencies',
    investigation: 'Incident Investigation Workbench',
    'digital-twin': 'Digital Twin Simulation Lab',
    evidence: 'Maintenance Technical Knowledge Base',
    'model-eval': 'Model Card & Reliability Evaluation',
  };

  return (
    <div className="app-container">
      <Sidebar
        currentView={currentView}
        onSelectView={setCurrentView}
        openIncidentsCount={overviewData?.active_incidents_count || 0}
      />

      <div className="main-content">
        <TopBar
          title={viewTitles[currentView]}
          onTriggerDemo={handleTriggerDemoIncident}
          isTriggering={isTriggering}
        />

        <main className="content-body">
          {currentView === 'overview' && (
            <OverviewView
              overviewData={overviewData}
              onInvestigateIncident={handleInvestigate}
              onInspectAsset={setSelectedAssetIdModal}
            />
          )}

          {currentView === 'graph' && (
            <FactoryGraphView
              graphData={graphData}
              onSelectNode={setSelectedAssetIdModal}
            />
          )}

          {currentView === 'investigation' && (
            <IncidentInvestigationView
              initialIncidentId={activeInvestigationIncidentId}
              onNavigateToSimulation={handleNavigateToSimulation}
            />
          )}

          {currentView === 'digital-twin' && (
            <DigitalTwinLabView
              initialAssetId={simulationAssetId}
              initialScenarioType={simulationScenarioType}
            />
          )}

          {currentView === 'evidence' && <EvidenceView />}

          {currentView === 'model-eval' && <ModelEvaluationView />}
        </main>
      </div>

      {selectedAssetIdModal && (
        <AssetDetailModal
          assetId={selectedAssetIdModal}
          onClose={() => setSelectedAssetIdModal(null)}
          onInvestigateIncident={handleInvestigate}
        />
      )}
    </div>
  );
};

export default App;
