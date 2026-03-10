import streamlit as st
import pandas as pd
import plotly.express as px
import json

from utils.pdf_extractor import extract_text_from_pdfs
from utils.topic_analyzer import extract_topics
from utils.trend_engine import calculate_trend
from utils.planner import generate_study_plan

from database.db import cursor, conn


# ---------------- SESSION INIT ----------------

if "active_plan" not in st.session_state:
    st.session_state["active_plan"] = None

if "user" not in st.session_state:
    st.session_state["user"] = "demo_user"


# ---------------- SIDEBAR ----------------

st.sidebar.title("ExamIntel")
st.sidebar.title("📚 Your Plans")

# New plan button
if st.sidebar.button("➕ New Plan"):
    st.session_state["active_plan"] = None
    st.rerun()

# Load plans from DB
cursor.execute(
    "SELECT DISTINCT title FROM plans WHERE username=?",
    (st.session_state["user"],)
)

plans = [row[0] for row in cursor.fetchall()]

# Sidebar plan selector
selected_plan = st.sidebar.radio(
    "Previous Plans",
    plans,
    index=plans.index(st.session_state["active_plan"])
    if st.session_state["active_plan"] in plans else None
)

# Update active plan
if selected_plan:
    st.session_state["active_plan"] = selected_plan


# =========================================================
#                 MODE 1 → VIEW SAVED PLAN
# =========================================================

if st.session_state["active_plan"]:

    selected_plan = st.session_state["active_plan"]

    st.title(f"📚 Study Plan: {selected_plan}")

    cursor.execute(
        "SELECT analysis FROM plans WHERE username=? AND title=?",
        (st.session_state["user"], selected_plan)
    )

    data = cursor.fetchone()

    if data is None:
        st.warning("No saved analysis found for this plan.")
        st.stop()

    analysis = json.loads(data[0])

    topic_df = pd.DataFrame(analysis["topics"])
    trend_df = pd.DataFrame(analysis["trend"])
    plan_df = pd.DataFrame(analysis["plan"])

    st.subheader("🔎 Top Extracted Topics")
    st.dataframe(topic_df, use_container_width=True)

    st.subheader("📈 Probability Analysis")
    st.dataframe(trend_df, use_container_width=True)

    st.subheader("📚 Saved Study Plan")
    st.dataframe(plan_df, use_container_width=True)

    fig = px.pie(
        plan_df,
        names="Topic",
        values="Allocated Hours",
        title="Study Time Distribution",
        hole=0.4
    )

    st.plotly_chart(fig, use_container_width=True)


# =========================================================
#                 MODE 2 → CREATE NEW PLAN
# =========================================================

else:

    st.title("📊 AI Exam Strategy Architect")

    plan_title = st.text_input(
        "Enter Study Plan Title",
        placeholder="Example: OS Exam Prep"
    )

    uploaded_files = st.file_uploader(
        "Upload Previous Year Question Papers",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:

        with st.spinner("Analyzing exam papers..."):

            text_dict = extract_text_from_pdfs(uploaded_files)

            topic_df = extract_topics(text_dict)

            trend_df = calculate_trend(text_dict, topic_df)

        st.success("PDFs processed successfully!")

        # Format topic table
        topic_df.insert(0, "Rank", range(1, len(topic_df) + 1))
        topic_df["Score"] = topic_df["Score"].round(3)

        st.subheader("🔎 Top Extracted Topics")

        st.dataframe(
            topic_df.style
            .format({"Score": "{:.3f}"})
            .set_properties(**{'text-align': 'left'})
            .set_table_styles([
                {'selector': 'th', 'props': [('text-align', 'left')]}
            ]),
            use_container_width=True,
            hide_index=True
        )

        st.subheader("📈 Probability Analysis")

        st.dataframe(
            trend_df,
            use_container_width=True,
            hide_index=True
        )

        # Probability bar chart
        st.subheader("📊 Topic Probability Chart")

        fig = px.bar(
            trend_df,
            x="Topic",
            y="Probability (%)",
            text="Probability (%)",
            color="Probability (%)",
            color_continuous_scale="Blues",
            title="Topic Probability Analysis"
        )

        fig.update_traces(texttemplate='%{text:.0f}%', textposition='outside')

        fig.update_layout(
            xaxis_tickangle=-40,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # ---------------- STUDY PLAN GENERATOR ----------------

        st.subheader("⏳ Study Plan Generator")

        days = st.number_input("Days Left", min_value=1, value=10)
        hours = st.number_input("Hours Per Day", min_value=1, value=3)

        st.subheader("📌 Mark Your Strength Level")

        weak_topics = st.multiselect(
            "Select topics you feel WEAK in:",
            trend_df["Topic"].tolist()
        )

        strong_topics = st.multiselect(
            "Select topics you feel STRONG in:",
            trend_df["Topic"].tolist()
        )

        # Generate plan
        if st.button("Generate Study Plan"):

            if not plan_title:
                st.warning("Please enter a study plan title.")
                st.stop()

            plan = generate_study_plan(
                trend_df,
                days,
                hours,
                weak_topics,
                strong_topics
            )

            plan_df = pd.DataFrame(plan)

            analysis_data = {
                "topics": topic_df.to_dict(),
                "trend": trend_df.to_dict(),
                "plan": plan_df.to_dict()
            }

            cursor.execute(
                "INSERT INTO plans(username, title, analysis) VALUES (?, ?, ?)",
                (
                    st.session_state["user"],
                    plan_title,
                    json.dumps(analysis_data)
                )
            )

            conn.commit()

            # Activate the new plan
            st.session_state["active_plan"] = plan_title

            st.rerun()