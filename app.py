import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

from utils.pdf_extractor import extract_text_from_pdfs
from utils.topic_analyzer import extract_topics
from utils.trend_engine import calculate_trend
from utils.planner import generate_study_plan

from database.db import cursor, conn

if "selected_plan" not in st.session_state:
    st.session_state["selected_plan"] = None

# Initialize session state
if "user" not in st.session_state:
    st.session_state["user"] = "demo_user"

# Sidebar navigation
st.sidebar.title("ExamIntel")
st.sidebar.title("📚 Your Plans")

if st.sidebar.button("➕ New Plan"):
    st.session_state["selected_plan"] = None
    st.rerun()

cursor.execute(
    "SELECT DISTINCT title FROM plans WHERE username=?",
    (st.session_state["user"],)
)

plans = [row[0] for row in cursor.fetchall()]

selected_plan = st.sidebar.radio(
    "Previous Plans",
    plans,
    key="selected_plan"
)

if st.session_state["selected_plan"]:
    
    selected_plan = st.session_state["selected_plan"]
        
    st.title(f"📚 Study Plan: {selected_plan}")

    cursor.execute(
        "SELECT topic, hours FROM plans WHERE username=? AND title=?",
        (st.session_state["user"], selected_plan)
    )

    data = cursor.fetchall()

    plan_df = pd.DataFrame(data, columns=["Topic", "Allocated Hours"])

    st.subheader("Saved Study Plan")
    st.dataframe(plan_df, use_container_width=True)

    fig = px.pie(
        plan_df,
        names="Topic",
        values="Allocated Hours",
        title="Study Time Distribution",
        hole=0.4
    )

    st.plotly_chart(fig, use_container_width=True)
if st.session_state["selected_plan"] is None: 
 st.title("📊 AI Exam Strategy Architect")

plan_title = st.text_input("Enter Study Plan Title", placeholder="Example: OS Exam Prep")

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
      trend_df.style
          .format({"Score": "{:.3f}"})
          .set_properties(**{'text-align': 'left'})
          .set_table_styles([
              {'selector': 'th', 'props': [('text-align', 'left')]}
          ]),
      use_container_width=True,
      hide_index=True
  )

      st.subheader("📊 Topic Probability Chart")
      fig = px.bar(
      trend_df,
      x="Topic",
      y="Probability (%)",
      title="Topic Probability Analysis",
      text="Probability (%)",
      color="Probability (%)",
      color_continuous_scale="Blues"
  )

      fig.update_traces(texttemplate='%{text:.0f}%', textposition='outside')

      fig.update_layout(
          xaxis_tickangle=-40,
          yaxis_title=dict(
          text="Probability (%)",
          font=dict(size=14, family="Arial Black")
      ),
      xaxis_title=dict(
          text="Topics",
          font=dict(size=14, family="Arial Black")
      ),
              showlegend=False
      )

      st.plotly_chart(fig, use_container_width=True)
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

      if st.button("Generate Study Plan"):
          
          if not plan_title:
            st.warning("Please enter a study plan title.")
            st.stop()

          plan = generate_study_plan(trend_df, days, hours, weak_topics, strong_topics)
          plan_df = pd.DataFrame(plan)

          for _, row in plan_df.iterrows():
                cursor.execute(
                "INSERT INTO plans(username, title, topic, hours) VALUES (?, ?, ?, ?)",
                (st.session_state["user"], plan_title, row["Topic"], row["Allocated Hours"])
            )

          conn.commit()
          
          st.rerun()

          st.dataframe(plan_df, use_container_width=True)

          fig2 = px.pie(
              plan_df,
              names="Topic",
              values="Allocated Hours",
              title="Study Time Distribution",
              hole=0.4
          )

          fig2.update_traces(textposition='inside', textinfo='percent+label')

          plan_df = plan_df.sort_values(by="Allocated Hours", ascending=False).head(7)

          st.plotly_chart(fig2, use_container_width=True)