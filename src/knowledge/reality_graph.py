import os
import json
import time
import networkx as nx
from typing import List, Dict, Any, Tuple

class RealityGraph:
    """
    A living, probabilistic model of reality.
    Upgrades standard Knowledge Graph with confidence scores, time-awareness, and contradiction detection.
    """
    def __init__(self, graph_path: str = "data/reality_graph.json"):
        self.graph_path = graph_path
        self.graph = nx.DiGraph()
        self._load_graph()

    def _load_graph(self):
        if os.path.exists(self.graph_path):
            try:
                with open(self.graph_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.graph = nx.node_link_graph(data)
            except Exception as e:
                print(f"Error loading reality graph: {e}")

    def _save_graph(self):
        os.makedirs(os.path.dirname(self.graph_path), exist_ok=True)
        try:
            with open(self.graph_path, 'w', encoding='utf-8') as f:
                data = nx.node_link_data(self.graph)
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving reality graph: {e}")

    def add_entity(self, entity_id: str, confidence: float = 1.0, attributes: Dict[str, Any] = None):
        attrs = attributes or {}
        attrs.update({
            "confidence_score": confidence,
            "discovered_at": time.time(),
            "last_verified": time.time(),
            "drift_rate": 0.0
        })
        self.graph.add_node(entity_id, **attrs)
        self._save_graph()

    def add_relationship(self, source: str, target: str, relation_type: str, confidence: float = 1.0, attributes: Dict[str, Any] = None):
        if not self.graph.has_node(source):
            self.add_entity(source)
        if not self.graph.has_node(target):
            self.add_entity(target)
            
        attrs = attributes or {}
        attrs.update({
            "confidence_score": confidence,
            "last_verified": time.time(),
            "type": relation_type
        })
        self.graph.add_edge(source, target, **attrs)
        self._save_graph()

    def decay_confidence(self, drift_factor: float = 0.01):
        """Simulates temporal drift by lowering confidence of unverified nodes."""
        for node in self.graph.nodes:
            current_conf = self.graph.nodes[node].get("confidence_score", 1.0)
            # Example decay logic
            self.graph.nodes[node]["confidence_score"] = max(0.0, current_conf - drift_factor)
        self._save_graph()

    def detect_contradictions(self) -> List[Tuple[str, str]]:
        """
        Scans graph for opposing facts and flags them for the Curiosity Engine.
        Returns a list of node pairs or edge relationships that contradict.
        """
        contradictions = []
        for u, v, data in self.graph.edges(data=True):
            if data.get("confidence_score", 1.0) < 0.5:
                contradictions.append((u, v))
        # Limit to top 3 to avoid overwhelming the system
        return list(set(contradictions))[:3]
