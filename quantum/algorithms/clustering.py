"""
Quantum clustering file organization functionality.
Refactored from original quantum_clustering_file_organization.py with enhanced modularity.
"""

import argparse
import os
from pathlib import Path
from typing import Optional

from qiskit.circuit.library import ZZFeatureMap
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

try:
    from qiskit_machine_learning.kernels import FidelityQuantumKernel
except Exception:  # pragma: no cover - optional dependency
    FidelityQuantumKernel = None

try:
    from qiskit import BasicAer
except Exception:  # pragma: no cover - optional dependency
    BasicAer = None

from .base import QuantumAlgorithmBase, TEXT_INDICATORS


class QuantumClustering(QuantumAlgorithmBase):
    """Quantum clustering for file organization using quantum kernels"""
    
    def __init__(self, workspace_path: Optional[str] = None, n_clusters: Optional[int] = None):
        if workspace_path is None:
            workspace_path = os.getenv("GH_COPILOT_WORKSPACE", str(Path.cwd()))
        super().__init__(workspace_path)
        self.n_clusters = n_clusters
        
        self.backend = None
        self.use_hardware = False

    def get_algorithm_name(self) -> str:
        """Get the algorithm name"""
        return "Quantum Clustering File Organization"

    def set_backend(self, backend, use_hardware: bool = False):
        """Set quantum backend for execution."""
        self.backend = backend
        self.use_hardware = use_hardware
    
    def execute_algorithm(self) -> bool:
        """Execute quantum clustering for file organization"""
        return self.perform_quantum_clustering()
    
    def perform_quantum_clustering(self) -> bool:
        """Cluster files using a quantum kernel."""
        file_paths = [p for p in self.workspace_path.iterdir() if p.is_file()]
        if not file_paths:
            self.logger.info(f"{TEXT_INDICATORS['info']} No files found in {self.workspace_path}")
            return False

        # Extract file features (size and modification time)
        features = [
            [f.stat().st_size, f.stat().st_mtime]
            for f in file_paths
        ]

        # Scale features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)

        # Use quantum kernel if available, otherwise fallback to classical
        kernel_matrix = self.compute_kernel_matrix(features_scaled)
        
        # Determine optimal number of clusters if not specified
        n_clusters = self.n_clusters or self.determine_optimal_clusters(features_scaled)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(kernel_matrix)

        # Log results
        cluster_counts = {}
        for path, label in zip(file_paths, labels):
            self.logger.info(f"{TEXT_INDICATORS['info']} {path.name}: cluster {label}")
            cluster_counts[label] = cluster_counts.get(label, 0) + 1
        
        self.logger.info(f"{TEXT_INDICATORS['info']} Clustered {len(file_paths)} files into {n_clusters} clusters")
        for cluster_id, count in cluster_counts.items():
            self.logger.info(f"{TEXT_INDICATORS['info']} Cluster {cluster_id}: {count} files")
        
        # Store clustering results in execution stats
        self.execution_stats.update({
            'files_clustered': len(file_paths),
            'n_clusters': n_clusters,
            'cluster_distribution': cluster_counts,
            'used_quantum_kernel': FidelityQuantumKernel is not None and BasicAer is not None
        })

        return True
    
    def compute_kernel_matrix(self, features_scaled):
        """Compute kernel matrix using quantum kernel if available"""
        if FidelityQuantumKernel is not None and BasicAer is not None:
            self.logger.info(f"{TEXT_INDICATORS['info']} Using quantum kernel")
            feature_map = ZZFeatureMap(feature_dimension=2, reps=1)
            backend = self.backend or BasicAer.get_backend("statevector_simulator")
            kernel = FidelityQuantumKernel(
                feature_map=feature_map, quantum_instance=backend
            )
            return kernel.evaluate(features_scaled)
        else:
            # Fallback to classical Euclidean distance matrix
            self.logger.info(f"{TEXT_INDICATORS['info']} Using classical kernel (quantum dependencies not available)")
            from sklearn.metrics import pairwise_distances
            return pairwise_distances(features_scaled, metric="euclidean")
    
    def determine_optimal_clusters(self, features_scaled):
        """Determine optimal number of clusters using elbow method"""
        if len(features_scaled) < 2:
            return 1
            
        max_clusters = min(10, len(features_scaled))
        distortions = []
        
        for k in range(1, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(features_scaled)
            distortions.append(kmeans.inertia_)
        
        # Simple elbow detection - find point where improvement diminishes
        if len(distortions) > 2:
            improvements = [distortions[i] - distortions[i+1] for i in range(len(distortions)-1)]
            if improvements:
                # Find elbow as point where improvement is less than half of max improvement
                max_improvement = max(improvements)
                for i, improvement in enumerate(improvements):
                    if improvement < max_improvement * 0.5:
                        return i + 2  # +2 because we start from k=1 and want the cluster count
        
        return max(2, len(features_scaled) // 4)  # Default heuristic


def main() -> bool:
    """Main execution function - maintains backward compatibility"""
    parser = argparse.ArgumentParser(
        description="Quantum Clustering File Organization"
    )
    parser.add_argument(
        "--clusters",
        type=int,
        default=None,
        help="Number of clusters to form (auto if omitted)",
    )
    parser.add_argument(
        "--workspace",
        default=None,
        help="Workspace path to cluster files in"
    )

    args = parser.parse_args()

    utility = QuantumClustering(workspace_path=args.workspace, n_clusters=args.clusters)
    success = utility.execute_utility()

    if success:
        stats = utility.get_execution_stats()
        print(f"\n{TEXT_INDICATORS['success']} Clustering completed:")
        print(f"  Files clustered: {stats.get('files_clustered', 0)}")
        print(f"  Number of clusters: {stats.get('n_clusters', 0)}")
        print(f"  Used quantum kernel: {stats.get('used_quantum_kernel', False)}")
        
        cluster_dist = stats.get('cluster_distribution', {})
        if cluster_dist:
            print("  Cluster distribution:")
            for cluster_id, count in cluster_dist.items():
                print(f"    Cluster {cluster_id}: {count} files")
    else:
        print(f"{TEXT_INDICATORS['error']} Clustering failed")

    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)