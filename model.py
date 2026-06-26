# model.py
# Responsibility: Load data, train model, return predictions
# No UI code belongs here

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report


def load_and_prepare_data(filepath: str) -> pd.DataFrame:
    """
    Load the spam dataset and prepare it for training.
    Supports both spam.csv (Kaggle) and sms.tsv formats.
    """
    if filepath.endswith(".tsv"):
        # TSV version: tab separated, no header, two columns
        df = pd.read_csv(
            filepath,
            sep="\t",
            header=None,
            names=["label", "message"]
        )
    else:
        # CSV version from Kaggle
        df = pd.read_csv(filepath, encoding="latin-1")
        df = df[["v1", "v2"]]
        df.columns = ["label", "message"]

    # Remove duplicate messages to avoid data leakage
    df = df.drop_duplicates(subset="message")

    # Convert labels to binary integers
    # spam = 1, ham = 0
    df["label_num"] = df["label"].map({"spam": 1, "ham": 0})

    return df


def train_model(df: pd.DataFrame):
    """
    Train a Naive Bayes classifier on the prepared dataset.

    Returns:
        vectorizer  - fitted TfidfVectorizer
        model       - trained MultinomialNB model
        accuracy    - float, accuracy on test set
        report      - string, full classification report
    """
    X = df["message"]
    y = df["label_num"]

    # Split before vectorizing to prevent data leakage
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=42,
        stratify=y        # keeps spam/ham ratio consistent in both splits
    )

    # TF-IDF converts raw text into numerical features
    # sublinear_tf dampens the effect of very frequent words
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000,
        sublinear_tf=True
    )

    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)   # transform only, not fit

    # MultinomialNB is the standard choice for text classification
    model = MultinomialNB(alpha=0.1)
    model.fit(X_train_vec, y_train)

    # Evaluate
    y_pred = model.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(
        y_test, y_pred, target_names=["Ham", "Spam"]
    )

    return vectorizer, model, accuracy, report


def predict_message(message: str, vectorizer, model) -> dict:
    """
    Predict whether a single message is spam or ham.

    Returns a dictionary:
        label       - "Spam" or "Ham"
        confidence  - float between 0 and 1
        spam_prob   - raw spam probability
        ham_prob    - raw ham probability
    """
    # Transform using the already-fitted vectorizer
    message_vec = vectorizer.transform([message])

    prediction = model.predict(message_vec)[0]
    probabilities = model.predict_proba(message_vec)[0]

    ham_prob = probabilities[0]
    spam_prob = probabilities[1]

    label = "Spam" if prediction == 1 else "Ham"
    confidence = spam_prob if prediction == 1 else ham_prob

    return {
        "label": label,
        "confidence": round(float(confidence), 4),
        "spam_prob": round(float(spam_prob), 4),
        "ham_prob": round(float(ham_prob), 4),
    }