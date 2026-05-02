import os
import json
import networkx as nx
from typing import List, Dict, Any

class GraphStore:
    def __init__(self, graph_path: str = "data/graph.json"):
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
                print(f"Error loading graph: {e}")

    def _save_graph(self):
        os.makedirs(os.path.dirname(self.graph_path), exist_ok=True)
        try:
            with open(self.graph_path, 'w', encoding='utf-8') as f:
                data = nx.node_link_data(self.graph)
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving graph: {e}")

    def add_entity(self, entity_id: str, attributes: Dict[str, Any] = None):
        self.graph.add_node(entity_id, **(attributes or {}))
        self._save_graph()

    def add_relationship(self, source: str, target: str, relation_type: str, attributes: Dict[str, Any] = None):
        if not self.graph.has_node(source):
            self.add_entity(source)
        if not self.graph.has_node(target):
            self.add_entity(target)
            
        self.graph.add_edge(source, target, type=relation_type, **(attributes or {}))
        self._save_graph()

    def get_entity_context(self, entity_id: str, depth: int = 1) -> Dict[str, Any]:
        """Get an entity and its immediate neighbors to build a knowledge context"""
        if not self.graph.has_node(entity_id):
            return {}
            
        subgraph_nodes = set([entity_id])
        current_layer = set([entity_id])
        
        for _ in range(depth):
            next_layer = set()
            for node in current_layer:
                next_layer.update(self.graph.successors(node))
                next_layer.update(self.graph.predecessors(node))
            subgraph_nodes.update(next_layer)
            current_layer = next_layer
            
        subgraph = self.graph.subgraph(subgraph_nodes)
        return nx.node_link_data(subgraph)

    def search_entities(self, keyword: str) -> List[str]:
        """Simple keyword search across node IDs"""
        keyword = keyword.lower()
        return [node for node in self.graph.nodes() if keyword in str(node).lower()]
