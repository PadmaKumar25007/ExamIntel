import streamlit as st
import pandas as pd
import plotly.express as px
import json

from utils.pdf_extractor import extract_text_from_pdfs
from utils.topic_analyzer import extract_topics
from utils.trend_engine import calculate_trend
from utils.planner import generate_study_plan

from database.db import cursor, conn



if "logged_in" not in st.session_state:
 st.session_state["logged_in"] = False

if "user" not in st.session_state:
 st.session_state["user"] = None

if "active_plan" not in st.session_state:
 st.session_state["active_plan"] = None

# ---------------- LOGIN / SIGNUP ----------------

if not st.session_state["logged_in"]:

 st.title("🔐 ExamIntel Login")

 tab1, tab2 = st.tabs(["Login", "Create Account"])

# LOGIN
 with tab1:

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        if user:
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
            st.rerun()
        else:
            st.error("Invalid username or password")

# SIGNUP
 with tab2:

    new_user = st.text_input("Create Username")
    new_pass = st.text_input("Create Password", type="password")

    if st.button("Create Account"):

        if not new_user or not new_pass:
            st.warning("Please enter username and password")
            st.stop()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (new_user,)
        )

        existing = cursor.fetchone()

        if existing:
            st.error("Username already exists")
        else:

            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (new_user, new_pass)
            )

            conn.commit()

            st.success("Account created! Please login.")

 st.stop()

#sidebar styling

st.markdown("""

<style>

[data-testid="stSidebar"] > div:first-child {
    padding-top: 0rem;
    margin-top: -10px;
}

section[data-testid="stSidebar"] > div {
    display: flex;
    flex-direction: column;
    height: 100%;
}

#logout-section {
    margin-top: auto;
}

</style>

""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------

st.sidebar.image("assets/logo-transparent_croped.png", width=50)
st.sidebar.markdown(f"👤 **{st.session_state['user']}**")
st.sidebar.title("ExamIntel")
st.sidebar.subheader("📚 Your Plans")

if st.sidebar.button("➕ New Plan"):
 st.session_state["active_plan"] = None
 st.rerun()

cursor.execute(
"SELECT DISTINCT title FROM plans WHERE username=?",
(st.session_state["user"],)
)

plans = [row[0] for row in cursor.fetchall()]

selected_plan = st.sidebar.radio(
"Previous Plans",
plans,
index=plans.index(st.session_state["active_plan"])
if st.session_state["active_plan"] in plans else None
)

if selected_plan:
 st.session_state["active_plan"] = selected_plan

# ---------------- LOGOUT ----------------

st.sidebar.markdown('<div id="logout-section">', unsafe_allow_html=True)
st.sidebar.markdown("---")

if st.sidebar.button("⬅️ Logout"):
 st.session_state["logged_in"] = False
 st.session_state["user"] = None
 st.session_state["active_plan"] = None
 st.rerun()

st.sidebar.markdown('</div>', unsafe_allow_html=True)

#saved plan

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

 st.subheader("📚 Study Plan")
 st.dataframe(plan_df, use_container_width=True)

 fig = px.pie(
    plan_df,
    names="Topic",
    values="Allocated Hours",
    title="Study Time Distribution",
    hole=0.4
 )

 st.plotly_chart(fig, use_container_width=True)

# ---------------- PREDICTED QUESTIONS ----------------

 st.subheader("🧠 Predicted Exam Questions")

 top_topics = trend_df.sort_values(
    "Probability (%)", ascending=False
 ).head(5)["Topic"].tolist()

 templates = [
    "Explain the concept of {} with suitable examples.",
    "Discuss the important properties of {}.",
    "Derive key formulas related to {}.",
    "Write detailed notes on {}.",
    "Explain the applications of {}."
 ]

 for i, topic in enumerate(top_topics):
    question = templates[i % len(templates)].format(topic)
    st.write(f"{i+1}. {question}")
    

 st.subheader("⚡ AI Last Day Strategy")

 last_day = trend_df.sort_values(
    "Probability (%)", ascending=False
 ).head(3)

 for _, row in last_day.iterrows():
    st.write(
        f"• Focus on **{row['Topic']}** (~{row['Probability (%)']:.0f}% probability)"
    )

# ---------------- PYQ TREND TIMELINE ----------------

 st.subheader("📈 PYQ Trend Timeline")

 timeline_df = trend_df.sort_values(
    "Probability (%)", ascending=False
 ).head(8)

 fig_timeline = px.line(
    timeline_df,
    x="Topic",
    y="Probability (%)",
    markers=True,
    title="Topic Importance Trend Based on PYQs"
 )

 fig_timeline.update_layout(xaxis_tickangle=-40)

 st.plotly_chart(fig_timeline, use_container_width=True)


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

    topic_df.insert(0, "Rank", range(1, len(topic_df) + 1))
    topic_df["Score"] = topic_df["Score"].round(3)

    st.subheader("🔎 Top Extracted Topics")

    st.dataframe(
        topic_df,
        use_container_width=True
    )

    st.subheader("📈 Probability Analysis")

    st.dataframe(
        trend_df,
        use_container_width=True
    )

    st.subheader("📊 Topic Probability Chart")

    fig = px.bar(
        trend_df,
        x="Topic",
        y="Probability (%)",
        text="Probability (%)",
        color="Probability (%)",
        color_continuous_scale="Blues"
    )

    fig.update_traces(texttemplate='%{text:.0f}%', textposition='outside')
    fig.update_layout(xaxis_tickangle=-40)

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("⏳ Study Plan Generator")

    days = st.number_input("Days Left", min_value=1, value=10)
    hours = st.number_input("Hours Per Day", min_value=1, value=3)

    weak_topics = st.multiselect(
        "Select topics you feel WEAK in:",
        trend_df["Topic"].tolist()
    )

    strong_topics = st.multiselect(
        "Select topics you feel STRONG in:",
        trend_df["Topic"].tolist()
    )

    if st.button("Generate Study Plan"):

        if not plan_title:
            st.warning("Please enter a study plan title.")
            st.stop()

        cursor.execute(
            "SELECT 1 FROM plans WHERE username=? AND title=?",
            (st.session_state["user"], plan_title)
        )

        existing_plan = cursor.fetchone()

        if existing_plan:
            st.error("Plan already exists with this name.")
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

        st.session_state["active_plan"] = plan_title
        st.rerun()

