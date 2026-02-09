from memory.memory_store import fraud_memory
from llm_utils import safe_llm_call  # NEW IMPORT

class DecisionAgent:
    def assess_ring(self, ring):
        ring_id = ring["ring_id"]
        size = ring["ring_size"]
        
        past = fraud_memory.search(ring_id)
        
        if past:
            severity = "HIGH"
            action = "Repeat offender – immediate escalation"
            memory_note = "Known fraud ring"
        else:
            if size >= 4:
                severity = "HIGH"
                action = "Platform alert + user warnings"
            elif size >= 2:
                severity = "MEDIUM"
                action = "Flag & monitor closely"
            else:
                severity = "LOW"
                action = "Log for patterns"
            memory_note = "New fraud pattern"

        # LLM EXPLANATION WITH FALLBACK
        explanation = self._get_explanation(ring_id, severity, size, past)
        
        fraud_memory.add(text=ring_id, meta={"ring_id": ring_id, "severity": severity})
        
        return {
            "ring_id": ring_id,
            "severity": severity,
            "action": action,
            "memory_note": memory_note,
            "explanation": explanation
        }
    
    def _get_explanation(self, ring_id, severity, size, past):
        def llm_explain(ring_id):
            from llm_utils import llm  # Lazy import
            prompt = f"Explain why ring {ring_id} (size: {size}, {'repeat' if past else 'new'}) is {severity}. List 3 reasons."
            return [line.strip() for line in llm.invoke(prompt).content.split('\n') if line.strip()]
        
        def rule_explain(ring_id):
            reasons = [
                f"Ring size: {size} jobs",
                f"Status: {'Repeat offender' if past else 'New pattern'}",
                f"Severity: {severity} (threshold-based)"
            ]
            return reasons
        
        return safe_llm_call(llm_explain, rule_explain, ring_id)
