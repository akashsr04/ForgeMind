from typing import List, Dict, Any, Tuple
import numpy as np
import networkx as nx
from sqlalchemy.orm import Session
from app.infrastructure.db.models import Asset, AssetEdge, TelemetryReading
from app.ml.features import extract_node_features, FEATURE_NAMES


class FactoryGraphData:
    def __init__(
        self,
        node_ids: List[str],
        node_features: np.ndarray,
        edge_index: np.ndarray,
        edge_weights: np.ndarray,
        edge_types: List[str],
        nx_graph: nx.DiGraph,
    ):
        self.node_ids = node_ids
        self.node_features = node_features  # (N, D)
        self.edge_index = edge_index        # (2, E)
        self.edge_weights = edge_weights    # (E,)
        self.edge_types = edge_types        # list of strings
        self.nx_graph = nx_graph


def build_factory_graph(db: Session, window_readings_limit: int = 50) -> FactoryGraphData:
    """
    Constructs graph representation and feature matrices from persisted database records.
    """
    assets = db.query(Asset).order_by(Asset.created_at.asc()).all()
    edges = db.query(AssetEdge).all()

    node_ids = [a.id for a in assets]
    node_to_idx = {a_id: idx for idx, a_id in enumerate(node_ids)}
    num_nodes = len(node_ids)

    # 1. Node features
    X = np.zeros((num_nodes, len(FEATURE_NAMES)), dtype=np.float32)
    for idx, asset in enumerate(assets):
        recent_readings = (
            db.query(TelemetryReading)
            .filter(TelemetryReading.asset_id == asset.id)
            .order_by(TelemetryReading.observed_at.desc())
            .limit(window_readings_limit)
            .all()
        )
        X[idx] = extract_node_features(asset, recent_readings)

    # 2. Edge index and attributes
    src_indices = []
    dst_indices = []
    weights = []
    edge_types = []

    nx_g = nx.DiGraph()
    for a in assets:
        nx_g.add_node(a.id, name=a.name, asset_type=a.asset_type, criticality=a.criticality, status=a.status)

    for e in edges:
        if e.source_asset_id in node_to_idx and e.target_asset_id in node_to_idx:
            s_idx = node_to_idx[e.source_asset_id]
            d_idx = node_to_idx[e.target_asset_id]
            src_indices.append(s_idx)
            dst_indices.append(d_idx)
            weights.append(float(e.weight or 1.0))
            edge_types.append(e.relationship_type)
            nx_g.add_edge(e.source_asset_id, e.target_asset_id, relationship=e.relationship_type, weight=float(e.weight or 1.0))

    if src_indices:
        edge_index = np.array([src_indices, dst_indices], dtype=np.int64)
        edge_weights = np.array(weights, dtype=np.float32)
    else:
        edge_index = np.zeros((2, 0), dtype=np.int64)
        edge_weights = np.zeros((0,), dtype=np.float32)

    return FactoryGraphData(
        node_ids=node_ids,
        node_features=X,
        edge_index=edge_index,
        edge_weights=edge_weights,
        edge_types=edge_types,
        nx_graph=nx_g,
    )
