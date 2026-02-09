import streamlit as st
import pandas as pd

from agents.scout_agent import ScoutAgent
from agents.undercover_agent import UndercoverAgent
from agents.pattern_hunter_agent import PatternHunterAgent
from agents.decision_agent import DecisionAgent

from database.db import init_db, insert_event, get_connection

# Initialize DB
init_db()

st.set_page_config(page_title="FraudHound", layout="wide")

st.title("FraudHound – Gig Scam Detection System")

st.markdown("""
FraudHound is a **role-based agentic AI system** for detecting gig-economy scams.
It supports **Users, Trust & Safety Analysts, and Researchers**.
""")

# Sidebar role selection
mode = st.sidebar.radio(
    "Select Role",
    ["User", "Analyst / Developer", "Research / NGO"]
)

if mode == "User":

    st.header("Check a Job / Recruiter Message")

    user_message = st.text_area("Paste the message here:", height=180)

    if st.button("Check Message"):

        if not user_message.strip():
            st.warning("Paste a message")
        else:
            scout = ScoutAgent()

            fake_job = {"description": user_message}

            score, reasons, suggestion = scout.calculate_risk_score(fake_job)

            insert_event(user_message, score, "user")

            if score >= 0.7:
                st.error("HIGH SCAM RISK")
            elif score >= 0.4:
                st.warning("Suspicious")
            else:
                st.success("Likely Safe")

            st.metric("Risk Score", score)

            st.subheader("Reasons")
            st.write(reasons)

            st.subheader("Safety Suggestion")
            st.info(suggestion)

elif mode == "Analyst / Developer":

    st.header("Fraud Analysis Dashboard")

    uploaded_file = st.file_uploader(
        "Upload gig job listings CSV",
        type=["csv"]
    )

    if uploaded_file is not None:

        try:
            df_uploaded = pd.read_csv(uploaded_file)

            if df_uploaded.empty:
                st.warning("Uploaded file is empty.")
                st.stop()

        except Exception:
            st.error("Invalid CSV file. Please upload a proper CSV.")
            st.stop()

        st.subheader("Uploaded Dataset")
        st.dataframe(df_uploaded)

        if st.button("Run Full FraudHound Analysis"):

            scout = ScoutAgent()

            # Scout Agent
            flagged_jobs = scout.scan_jobs(df=df_uploaded, threshold=0.4)

            if flagged_jobs.empty:
                st.success("No suspicious jobs detected.")
                st.stop()

            st.subheader("Scout Agent Output")
            st.dataframe(flagged_jobs)
            st.write("DEBUG:", len(flagged_jobs))
            st.write(flagged_jobs)
            # Undercover Agent
            st.subheader("Undercover Agent")
            undercover = UndercoverAgent("data/recruiter_chat_scripts.json")

            undercover_results = []
            for _, row in flagged_jobs.iterrows():
                undercover_results.append(
                    undercover.simulate_conversation(
                        row["job_id"],
                        row.get("description", "")
                    )
                )

            st.json(undercover_results)

            # Pattern Hunter
            st.subheader("Pattern Hunter")
            hunter = PatternHunterAgent()
            fraud_rings = hunter.detect_fraud_rings(undercover_results)
            st.json(fraud_rings)

            # Decision Agent
            st.subheader("Decision Agent")
            decision_agent = DecisionAgent()

            for ring in fraud_rings:
                decision = decision_agent.assess_ring(ring)

                insert_event(
                    text=ring["ring_id"],
                    risk_score=1 if decision["severity"] == "HIGH" else 0.5,
                    source="analyst"
                )

                st.write(decision)


elif mode == "Research / NGO":

    st.header("Scam Pattern Insights")

    conn = get_connection()
    df = pd.read_sql("SELECT * FROM scam_events", conn)
    conn.close()

    if df.empty:
        st.info("No data yet")
    else:
        st.dataframe(df)
        st.write("Total Records:", len(df))
        st.bar_chart(df["risk_score"])
