from typing import TypedDict, List
from langgraph.graph import StateGraph, END

from agents.scout_agent import ScoutAgent
from agents.undercover_agent import UndercoverAgent
from agents.pattern_hunter_agent import PatternHunterAgent
from agents.decision_agent import DecisionAgent



class FraudState(TypedDict):
    flagged_jobs: List[dict]
    undercover_results: List[dict]
    fraud_rings: List[dict]
    decisions: List[dict]



def scout_node(state: FraudState):
    scout = ScoutAgent()
    flagged = scout.scan_jobs(
        csv_path="data/gig_job_listings.csv",
        threshold=0.6
    )
    return {"flagged_jobs": flagged.to_dict("records")}


def undercover_node(state: FraudState):

    undercover = UndercoverAgent(
        chat_script_path="data/recruiter_chat_scripts.json"
    )

    results = []
    for job in state["flagged_jobs"]:
        results.append(
            undercover.simulate_conversation(
                job["job_id"],
                job.get("description", "")
            )
        )

    return {"undercover_results": results}



    return {"undercover_results": results}


def pattern_node(state: FraudState):
    hunter = PatternHunterAgent()
    rings = hunter.detect_fraud_rings(state["undercover_results"])
    return {"fraud_rings": rings}


def decision_node(state: FraudState):
    decision_agent = DecisionAgent()
    decisions = []

    for ring in state["fraud_rings"]:
        decisions.append(
            decision_agent.assess_ring(ring)
        )

    return {"decisions": decisions}



def should_continue_after_scout(state: FraudState):
    if not state["flagged_jobs"]:
        return END
    return "undercover"


def build_fraud_graph():
    graph = StateGraph(FraudState)

    graph.add_node("scout", scout_node)
    graph.add_node("undercover", undercover_node)
    graph.add_node("pattern", pattern_node)
    graph.add_node("decision", decision_node)

    graph.set_entry_point("scout")

    graph.add_conditional_edges(
        "scout",
        should_continue_after_scout,
        {
            "undercover": "undercover",
            END: END
        }
    )

    graph.add_edge("undercover", "pattern")
    graph.add_edge("pattern", "decision")
    graph.add_edge("decision", END)

    return graph.compile()
