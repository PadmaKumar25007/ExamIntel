import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

from utils.pdf_extractor import extract_text_from_pdfs
from utils.topic_analyzer import extract_topics
from utils.trend_engine import calculate_trend
from utils.planner import generate_study_plan

st.title("📊 AI Exam Strategy Architect")

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
        plan = generate_study_plan(trend_df, days, hours, weak_topics, strong_topics)
        plan_df = pd.DataFrame(plan)

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