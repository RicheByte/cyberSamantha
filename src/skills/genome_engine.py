import os
import json
import glob
from typing import Dict, Any, List

class GenomeEngine:
    """
    Self-Evolving Skill Genome.
    Manages skill metadata, usage count, mutations, and recombinations.
    """
    def __init__(self, skills_dir: str = "skills/"):
        self.skills_dir = skills_dir
        self.genome_registry_path = os.path.join(skills_dir, "genome_registry.json")
        self.registry: Dict[str, Dict[str, Any]] = {}
        self._load_registry()

    def _load_registry(self):
        if os.path.exists(self.genome_registry_path):
            with open(self.genome_registry_path, 'r', encoding='utf-8') as f:
                self.registry = json.load(f)
        else:
            self._initialize_from_existing_skills()

    def _initialize_from_existing_skills(self):
        """Discovers existing markdown skills and adds them to the registry."""
        for md_file in glob.glob(os.path.join(self.skills_dir, "*.md")):
            skill_name = os.path.basename(md_file).replace(".md", "")
            if skill_name not in self.registry:
                self.registry[skill_name] = {
                    "usage_count": 0,
                    "success_rate": 1.0,
                    "execution_time_avg": 0.0,
                    "lineage_history": ["origin"]
                }
        self._save_registry()

    def _save_registry(self):
        with open(self.genome_registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2)

    def record_usage(self, skill_name: str, success: bool, execution_time: float):
        if skill_name in self.registry:
            stats = self.registry[skill_name]
            stats["usage_count"] += 1
            # Rolling average for success
            current_success = 1.0 if success else 0.0
            stats["success_rate"] = (stats["success_rate"] * (stats["usage_count"] - 1) + current_success) / stats["usage_count"]
            stats["execution_time_avg"] = (stats["execution_time_avg"] * (stats["usage_count"] - 1) + execution_time) / stats["usage_count"]
            self._save_registry()

    def mutate_skill(self, skill_name: str) -> str:
        """
        Uses an LLM to spawn a variant of a high-performing skill.
        Returns the name of the new mutated skill.
        """
        # TODO: Implement LLM prompt to rewrite skill instructions
        mutated_name = f"{skill_name}_mut_v1"
        return mutated_name

    def recombine_skills(self, skill_a: str, skill_b: str) -> str:
        """
        Merges two complementary skills.
        """
        # TODO: Implement LLM merge logic
        combined_name = f"{skill_a}_{skill_b}_fusion"
        return combined_name

    def prune_weak_skills(self, threshold: float = 0.4):
        """Archives skills with success rate below threshold."""
        for name, stats in list(self.registry.items()):
            if stats["usage_count"] > 5 and stats["success_rate"] < threshold:
                print(f"Pruning skill {name} due to low success rate.")
                # TODO: Move file to archive directory
                del self.registry[name]
        self._save_registry()
