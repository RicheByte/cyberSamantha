import time
import threading
from typing import Any

class CuriosityDaemon:
    """
    Autonomous Research Drive.
    A background process that acts on internal pressure to resolve contradictions.
    """
    def __init__(self, reality_graph: Any, agent_router: Any, check_interval: int = 60):
        self.reality_graph = reality_graph
        self.agent_router = agent_router
        self.check_interval = check_interval
        self.is_running = False
        self._thread = None

    def start(self):
        if not self.is_running:
            self.is_running = True
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            print("[Curiosity] Daemon started.")

    def stop(self):
        self.is_running = False
        if self._thread:
            self._thread.join()

    def _run_loop(self):
        while self.is_running:
            self._evaluate_internal_pressure()
            time.sleep(self.check_interval)

    def _evaluate_internal_pressure(self):
        """
        Checks for contradictions or low-confidence nodes in the reality graph.
        """
        contradictions = self.reality_graph.detect_contradictions()
        if contradictions:
            for source, target in contradictions:
                print(f"[Curiosity] Found contradiction between {source} and {target}. Initiating background research...")
                task = f"There is a low-confidence relationship or contradiction between '{source}' and '{target}' in the Knowledge Graph. Research this via web search or other means to verify the connection, and then remember the facts."
                # Autonomous research trigger
                self.agent_router.query(task, mode="auto")
        else:
            # Simulate temporal drift if no immediate actions
            self.reality_graph.decay_confidence()
