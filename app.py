# app.py
# Responsibility: User interface only
# No ML training, no dataset loading belongs here

import streamlit as st
from model import load_and_prepare_data, train_model, predict_message
from utils import (
    get_risk_level,
    find_suspicious_keywords,
    format_confidence_percentage,
    summarize_keywords,
)

# ======== Page Configuration==========================

st.set_page_config(
    page_title="AI Spam & Phishing Detector",
    page_icon="🛡️",
    layout="centered",
)

# ======= Load and Train (cached so it only runs once) =========

@st.cache_resource
def initialise_model():
    """Load data and train model once. Streamlit caches the result."""
    df = load_and_prepare_data("sms.tsv")
    vectorizer, model, accuracy, report = train_model(df)
    return vectorizer, model, accuracy, report


vectorizer, model, accuracy, report = initialise_model()

# ========= Sidebar ====================

with st.sidebar:
    st.title("🛡️ About This Tool")
    st.markdown(
        """
        This tool uses a **Naive Bayes** classifier trained on the 
        [UCI SMS Spam Collection](https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset).
        
        It analyses messages for:
        - Spam probability
        - Phishing language patterns
        - Suspicious keyword usage
        """
    )
    st.divider()
    st.metric(label="Model Accuracy", value=f"{accuracy * 100:.2f}%")
    st.caption("Measured on 20% held-out test data")

    with st.expander("View Classification Report"):
        st.text(report)

# ========= Main Interface =============

st.title("AI Phishing & Spam Detector")
st.markdown("Paste any message below to analyse it for spam or phishing content.")

user_input = st.text_area(
    label="Message to analyse",
    placeholder="Paste your SMS, email, or message here...",
    height=150,
)

analyse_button = st.button("🔍 Analyse Message", type="primary")

#============ Results =======================

if analyse_button:
    if not user_input.strip():
        st.warning("Please enter a message before analysing.")
    else:
        result = predict_message(user_input, vectorizer, model)
        risk_label, risk_color = get_risk_level(result["confidence"], result["label"])
        found_keywords = find_suspicious_keywords(user_input)

        st.divider()

        # Primary verdict
        if result["label"] == "Spam":
            st.error(f"⚠️ Verdict: **{result['label']}** — {risk_label}")
        else:
            st.success(f"✅ Verdict: **{result['label']}** — {risk_label}")

        # Confidence scores
        col1, col2, col3 = st.columns(3)
        col1.metric("Spam Probability", format_confidence_percentage(result["spam_prob"]))
        col2.metric("Ham Probability", format_confidence_percentage(result["ham_prob"]))
        col3.metric("Confidence", format_confidence_percentage(result["confidence"]))

        # Suspicious keywords
        st.subheader("Suspicious Keywords Found")
        keyword_summary = summarize_keywords(found_keywords)

        if found_keywords:
            st.warning(f"🚩 {keyword_summary}")
        else:
            st.info("✔️ No suspicious keywords detected.")