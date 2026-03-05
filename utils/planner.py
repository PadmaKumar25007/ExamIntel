def generate_study_plan(trend_df, days, hours_per_day, weak_topics, strong_topics):
    total_hours = days * hours_per_day

    adjusted_scores = []

    for _, row in trend_df.iterrows():
        score = row["Probability (%)"]

        # Boost weak topics
        if row["Topic"] in weak_topics:
            score *= 1.3  # 30% boost

        # Reduce strong topics
        if row["Topic"] in strong_topics:
            score *= 0.8  # 20% reduction

        adjusted_scores.append(score)

    trend_df["Adjusted Score"] = adjusted_scores
    total_adjusted_score = sum(adjusted_scores)

    study_plan = []

    for _, row in trend_df.iterrows():
        allocated_hours = (row["Adjusted Score"] / total_adjusted_score) * total_hours

        study_plan.append({
            "Topic": row["Topic"],
            "Allocated Hours": round(allocated_hours, 2)
        })

    return study_plan