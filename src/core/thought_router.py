from typing import Any, Dict

class ThoughtRouter:
    """
    Routes tasks through various cognitive modes instead of direct linear delegation.
    Queries Meta-Memory to determine if a task requires debate, synthesis, or standard execution.
    """
    def __init__(self, meta_memory=None):
        self.meta_memory = meta_memory

    def route_task(self, task_description: str, task_type: str) -> Dict[str, Any]:
        """
        Determines the execution strategy.
        """
        if self.meta_memory:
            strategy_info = self.meta_memory.query_best_strategy(task_type)
            strategy = strategy_info.get("strategy", "linear")
        else:
            strategy = "linear"
            
        print(f"[ThoughtRouter] Selected strategy for '{task_type}': {strategy}")
        
        if strategy == "debate":
            return self._trigger_debate(task_description)
        else:
            return self._trigger_linear(task_description)

    def _trigger_debate(self, task_description: str) -> Dict[str, Any]:
        # TODO: Hook into DebateOrchestrator
        return {"status": "routed_to_debate", "task": task_description}

    def _trigger_linear(self, task_description: str) -> Dict[str, Any]:
        # Standard agent assignment
        return {"status": "routed_to_linear", "task": task_description}
