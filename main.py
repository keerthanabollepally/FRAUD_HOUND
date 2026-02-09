from agents.scout_agent import ScoutAgent
from agents.undercover_agent import UndercoverAgent
from agents.pattern_hunter_agent import PatternHunterAgent
from agents.decision_agent import DecisionAgent


scout = ScoutAgent()
flagged_jobs = scout.scan_jobs(
    csv_path="data/gig_job_listings.csv",
    threshold=0.6
)

undercover = UndercoverAgent(
    chat_script_path="data/recruiter_chat_scripts.json"
)

undercover_results = []
for _, row in flagged_jobs.iterrows():
    undercover_results.append(
        undercover.simulate_conversation(row["job_id"])
    )


pattern_hunter = PatternHunterAgent()
fraud_rings = pattern_hunter.detect_fraud_rings(undercover_results)

decision_agent = DecisionAgent()
decisions = []

print("\n DECISION & ESCALATION REPORT:\n")

for ring in fraud_rings:
    decision = decision_agent.assess_ring(ring)
    decisions.append(decision)

    print(f"Fraud Ring: {decision['ring_id']}")
    print(f"Severity: {decision['severity']}")
    print(f"Action: {decision['recommended_action']}")
    print(f"Reason: {decision['explanation']}")
    print("-" * 50)
