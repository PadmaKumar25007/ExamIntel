import pandas as pd

def calculate_trend(text_dict, topic_df):
    trend_data = []

    files = list(text_dict.keys())

    for topic in topic_df["Topic"]:
        yearly_scores = []

        for file in files:
            count = text_dict[file].count(topic)
            yearly_scores.append(count)

        trend_data.append({
            "Topic": topic,
            "Trend Score": sum(yearly_scores),
            "Recent Weight": yearly_scores[-1] * 2 if yearly_scores else 0
        })

    trend_df = pd.DataFrame(trend_data)
    trend_df["Final Score"] = trend_df["Trend Score"] + trend_df["Recent Weight"]

    max_score = trend_df["Final Score"].max()
    trend_df["Probability (%)"] = (trend_df["Final Score"] / max_score) * 100

    return trend_df.sort_values(by="Probability (%)", ascending=False)