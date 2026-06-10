# monitoring/decision_tracer.py
import json
from datetime import datetime
from typing import Dict, List

class DecisionTracer:
    """Traces agent decisions for explainability"""
    
    def __init__(self):
        self.traces: Dict[str, List] = {}
    
    def trace_decision(self, task_id: str, agent: str, step: str, input_data: Dict, output_data: Dict, reasoning: str):
        if task_id not in self.traces:
            self.traces[task_id] = []
        
        self.traces[task_id].append({
            "agent": agent,
            "step": step,
            "reasoning": reasoning,
            "input_summary": str(input_data)[:200],
            "output_summary": str(output_data)[:200],
            "timestamp": datetime.now().isoformat()
        })
    
    def get_task_trace(self, task_id: str) -> List[Dict]:
        return self.traces.get(task_id, [])
    
    def get_agent_decisions(self, agent: str) -> List[Dict]:
        decisions = []
        for task_id, traces in self.traces.items():
            decisions.extend([t for t in traces if t["agent"] == agent])
        return decisions
    
    def export_trace(self, task_id: str) -> str:
        return json.dumps(self.get_task_trace(task_id), indent=2)