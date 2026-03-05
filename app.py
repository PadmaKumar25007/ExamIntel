import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

    text_dict = extract_text_from_pdfs(uploaded_files)

    st.success("PDFs processed successfully!")

    topic_df = extract_topics(text_dict)

    st.subheader("🔎 Top Extracted Topics")
    st.dataframe(topic_df)

    trend_df = calculate_trend(text_dict, topic_df)

    st.subheader("📈 Probability Analysis")
    st.dataframe(trend_df)

    st.subheader("📊 Topic Probability Chart")
    fig, ax = plt.subplots()
    ax.bar(trend_df["Topic"], trend_df["Probability (%)"])
    plt.xticks(rotation=45)
    st.pyplot(fig)

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

        st.dataframe(plan_df)

        fig2, ax2 = plt.subplots()
        ax2.pie(plan_df["Allocated Hours"], labels=plan_df["Topic"], autopct="%1.1f%%")
        st.pyplot(fig2)
        st.info("Weak topics boosted by 30%, strong topics reduced by 20%")