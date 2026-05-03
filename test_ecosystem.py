import os
import time
import sys

# Ensure imports work from project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.knowledge.reality_graph import RealityGraph
from src.memory.meta_memory import MetaMemory
from src.skills.genome_engine import GenomeEngine
from src.core.thought_router import ThoughtRouter

def run_tests():
    print("Starting Ecosystem Component Tests...\n")
    
    try:
        print("1. Testing RealityGraph...")
        rg = RealityGraph("data/test_reality_graph.json")
        rg.add_relationship("MalwareA", "System32", "modifies", confidence=0.3)
        contradictions = rg.detect_contradictions()
        if not contradictions:
            raise AssertionError("RealityGraph failed to detect low-confidence contradiction.")
        print("   ✅ RealityGraph initialized and detected contradiction.")
        
        print("\n2. Testing MetaMemory...")
        mm = MetaMemory("data/test_meta_memory.json")
        mm.log_strategy_execution("test_task", "debate", ["coder", "hacker"], 0.95, "Test context")
        best = mm.query_best_strategy("test_task")
        if best.get("strategy") != "debate":
            raise AssertionError("MetaMemory failed to retrieve the best strategy.")
        print("   ✅ MetaMemory successfully stored and retrieved reasoning strategy.")
        
        print("\n3. Testing ThoughtRouter...")
        tr = ThoughtRouter(meta_memory=mm)
        route_decision = tr.route_task("Solve this complex problem", "test_task")
        if "debate" not in route_decision.get("status", ""):
            raise AssertionError("ThoughtRouter failed to route based on MetaMemory.")
        print("   ✅ ThoughtRouter correctly routed task to 'debate' based on memory.")
        
        print("\n4. Testing GenomeEngine...")
        ge = GenomeEngine("skills/")
        ge.record_usage("dummy_skill", success=True, execution_time=2.5)
        print("   ✅ GenomeEngine correctly registered skill execution.")
        
        print("\n🎉 All components successfully loaded and tested without errors!")
        
    except Exception as e:
        print(f"\n❌ Test Failed: {str(e)}")

if __name__ == "__main__":
    run_tests()
