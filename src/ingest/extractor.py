import os
import json
from typing import List, Dict, Any

from src.core.llm_provider import LLMProvider
from src.knowledge.graph_store import GraphStore

class GraphExtractor:
    def __init__(self, graph_store: GraphStore):
        self.graph_store = graph_store
        self.llm = LLMProvider()

    def extract_from_text(self, text: str, source_file: str):
        """Extract entities and relationships from text using LLM, then add to GraphStore."""
        if not self.llm.is_available or not text.strip():
            return

        prompt = f"""Extract key cybersecurity entities and their relationships from the text below. 
        Focus on Vulnerabilities, Tools, Actors, Techniques, and Mitigation strategies.
        Respond ONLY with a valid JSON array of relationships in this exact format, with no markdown formatting or backticks:
        [
            {{"source": "Entity1", "target": "Entity2", "relation": "uses", "source_type": "Actor", "target_type": "Tool"}},
            {{"source": "Entity1", "target": "Entity2", "relation": "mitigates", "source_type": "Mitigation", "target_type": "Vulnerability"}}
        ]
        
        TEXT (Source: {source_file}):
        {text[:4000]}  # Limiting length for safety
        """

        try:
            response = self.llm.generate(prompt, temperature=0.1, max_tokens=1024)
            # Clean up response (sometimes models add markdown formatting even if asked not to)
            output = response.text.strip()
            if output.startswith("```json"):
                output = output[7:]
            if output.startswith("```"):
                output = output[3:]
            if output.endswith("```"):
                output = output[:-3]
                
            relationships = json.loads(output)
            
            for rel in relationships:
                source = rel.get("source")
                target = rel.get("target")
                relation = rel.get("relation", "related_to")
                if source and target:
                    self.graph_store.add_relationship(
                        source, target, relation, 
                        attributes={
                            "source_type": rel.get("source_type"),
                            "target_type": rel.get("target_type"),
                            "source_file": source_file
                        }
                    )
        except Exception as e:
            # Silently pass extraction errors on chunks to avoid spamming the console
            pass
