from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import re

def is_valid_phrase(phrase):
    # remove phrases with repeated words
    words = phrase.split()
    if len(set(words)) != len(words):
        return False
    
    # remove phrases containing roman numerals
    if re.search(r'\b(i|ii|iii|iv|v)\b', phrase):
        return False
    
    # remove very generic short words
    if any(len(word) < 3 for word in words):
        return False
    
    return True

def extract_topics(text_dict, top_n=10):
    corpus = list(text_dict.values())
    doc_count = len(corpus)

    min_df_value = 2 if doc_count > 2 else 1

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(2,2),
        max_features=500,
        min_df=min_df_value
    )

    X = vectorizer.fit_transform(corpus)

    feature_names = vectorizer.get_feature_names_out()
    scores = X.sum(axis=0).A1

    topic_df = pd.DataFrame({
        "Topic": feature_names,
        "Score": scores
    }).sort_values(by="Score", ascending=False)

    # Apply smart filtering
    topic_df = topic_df[topic_df["Topic"].apply(is_valid_phrase)]

    return topic_df.head(top_n).reset_index(drop=True)