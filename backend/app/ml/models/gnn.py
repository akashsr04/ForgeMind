from typing import Optional, Tuple, Dict, Any
import numpy as np
from app.core.logging import logger

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except (ImportError, OSError) as e:
    logger.warning(f"PyTorch C-extensions unavailable on host OS ({e}); activating transparent spectral graph-convolutional fallback.")
    TORCH_AVAILABLE = False


if TORCH_AVAILABLE:
    class GraphConvLayer(nn.Module):
        """
        Direct spectral Graph Convolutional Layer (Kipf & Welling GCN):
        H' = \hat{D}^{-1/2} \hat{A} \hat{D}^{-1/2} H W
        """
        def __init__(self, in_features: int, out_features: int):
            super().__init__()
            self.linear = nn.Linear(in_features, out_features, bias=True)

        def forward(self, x: torch.Tensor, adj_norm: torch.Tensor) -> torch.Tensor:
            # (N, N) @ (N, F) -> (N, F)
            ax = torch.matmul(adj_norm, x)
            return self.linear(ax)

    class PyTorchGNN(nn.Module):
        def __init__(self, in_channels: int = 16, hidden_channels: int = 32, num_classes: int = 1):
            super().__init__()
            self.conv1 = GraphConvLayer(in_channels, hidden_channels)
            self.conv2 = GraphConvLayer(hidden_channels, 16)
            self.out_head = nn.Linear(16, num_classes)
            self.dropout = nn.Dropout(p=0.1)

        def forward(self, x: torch.Tensor, adj_norm: torch.Tensor) -> torch.Tensor:
            h = self.conv1(x, adj_norm)
            h = F.relu(h)
            h = self.dropout(h)
            h = self.conv2(h, adj_norm)
            h = F.relu(h)
            logits = self.out_head(h)
            return logits


class GNNRiskModel:
    """
    Wrapper for Graph Neural Network training and inference on factory topology.
    Includes adjacency normalization with self-loops and degree scaling.
    """

    def __init__(self, in_features: int = 16, hidden_dim: int = 32):
        self.in_features = in_features
        self.hidden_dim = hidden_dim
        self.is_trained = False
        self.model: Optional[Any] = None

        if TORCH_AVAILABLE:
            self.model = PyTorchGNN(in_features, hidden_dim, num_classes=1)

    def _compute_normalized_adjacency(self, num_nodes: int, edge_index: np.ndarray) -> Any:
        if not TORCH_AVAILABLE:
            return None

        # Build adjacency matrix with self-loops: \hat{A} = A + I
        adj = np.eye(num_nodes, dtype=np.float32)
        if edge_index.shape[1] > 0:
            for s, d in zip(edge_index[0], edge_index[1]):
                adj[s, d] = 1.0
                adj[d, s] = 1.0  # Undirected operational message passing

        # Degree matrix D: D_ii = \sum_j A_ij
        deg = np.sum(adj, axis=1)
        deg_inv_sqrt = np.power(deg, -0.5, where=deg > 0)
        deg_inv_sqrt[deg == 0] = 0.0

        d_mat = np.diag(deg_inv_sqrt)
        adj_norm = d_mat @ adj @ d_mat

        return torch.tensor(adj_norm, dtype=torch.float32)

    def train_on_synthetic_scenarios(
        self,
        X_train: np.ndarray,
        edge_index: np.ndarray,
        y_train: np.ndarray,
        epochs: int = 50,
        lr: float = 0.01,
    ) -> Dict[str, Any]:
        if not TORCH_AVAILABLE or self.model is None:
            logger.warning("PyTorch unavailable; skipping GNN neural training.")
            return {"status": "skipped", "reason": "PyTorch not installed"}

        self.model.train()
        num_nodes = X_train.shape[0]
        adj_norm = self._compute_normalized_adjacency(num_nodes, edge_index)

        X_tensor = torch.tensor(X_train, dtype=torch.float32)
        y_tensor = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)

        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr, weight_decay=1e-4)
        pos_weight = torch.tensor([2.0])  # Anomaly class weight
        criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

        loss_val = 0.0
        for epoch in range(epochs):
            optimizer.zero_grad()
            logits = self.model(X_tensor, adj_norm)
            loss = criterion(logits, y_tensor)
            loss.backward()
            optimizer.step()
            loss_val = float(loss.item())

        self.is_trained = True
        return {
            "status": "trained",
            "epochs": epochs,
            "final_loss": round(loss_val, 4),
            "architecture": "2-layer Kipf-Welling GCN (16 -> 32 -> 16 -> 1)",
        }

    def predict_node_risks(self, X: np.ndarray, edge_index: np.ndarray) -> np.ndarray:
        """
        Returns risk scores on [0.0, 1.0] for all nodes in the graph.
        """
        if not TORCH_AVAILABLE or self.model is None or not self.is_trained:
            # Deterministic graph-aware fallback
            # Propagate node anomaly to 1-hop neighbors
            base_risk = np.zeros(X.shape[0], dtype=np.float32)
            for i in range(X.shape[0]):
                # Node feature heuristic
                base_risk[i] = 0.1 + (0.5 * X[i, 14]) + (0.2 * X[i, 10]) + (0.2 * X[i, 12])

            # 1-hop propagation
            propagated_risk = np.copy(base_risk)
            if edge_index.shape[1] > 0:
                for src, dst in zip(edge_index[0], edge_index[1]):
                    if base_risk[src] > 0.6:
                        propagated_risk[dst] = max(propagated_risk[dst], base_risk[src] * 0.75)

            return np.clip(propagated_risk, 0.0, 1.0)

        self.model.eval()
        with torch.no_grad():
            adj_norm = self._compute_normalized_adjacency(X.shape[0], edge_index)
            X_tensor = torch.tensor(X, dtype=torch.float32)
            logits = self.model(X_tensor, adj_norm)
            probs = torch.sigmoid(logits).squeeze(1).numpy()
            return np.round(probs, 4)
