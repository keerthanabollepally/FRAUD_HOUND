import json
from llm_utils import llm_undercover_simulation  # Already has fallback!

class UndercoverAgent:
    def __init__(self, chat_script_path=None):
        self.chat_scripts = []

    def simulate_conversation(self, job_id, job_description=""):
        # Already has fallback in llm_undercover_simulation!
        result = llm_undercover_simulation(job_description)
        
        return {
            "job_id": job_id,
            "script_id": "llm_generated" if result.get("conversation") else "rule_based",
            "scam_detected": result.get("scam_detected", False),
            "conversation": result.get("conversation", [{"sender":"system","message":"Fallback active"}])
        }
