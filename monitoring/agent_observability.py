# monitoring/agent_observability.py
import time
from collections import defaultdict
from typing import Dict, List

class AgentObservability:
    """Monitors agent performance and health"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def record_latency(self, agent: str, duration_ms: float):
        self.metrics[f"{agent}:latency"].append(duration_ms)
    
    def record_action(self, agent: str, action: str, status: str):
        self.metrics[f"{agent}:{action}:{status}"].append(time.time())
    
    def get_agent_metrics(self, agent: str) -> Dict:
        latencies = self.metrics.get(f"{agent}:latency", [])
        if latencies:
            latencies.sort()
            return {
                "agent": agent,
                "total_actions": len(latencies),
                "avg_latency_ms": sum(latencies)/len(latencies),
                "p95_latency_ms": latencies[int(len(latencies)*0.95)] if len(latencies) > 20 else latencies[-1]
            }
        return {"agent": agent, "total_actions": 0}
    
    def get_all_metrics(self) -> Dict:
        agents = set(k.split(":")[0] for k in self.metrics.keys() if ":latency" in k)
        return {a: self.get_agent_metrics(a) for a in agents}