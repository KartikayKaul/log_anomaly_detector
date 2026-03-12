"""
    MODELS
        saare chikne models idhar hai
""";
import numpy as np
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, roc_auc_score, confusion_matrix, classification_report


class TfIdfIsolationModel:
    """
        IsolationForest Model with TFIDF vectorizer for representing the text of inputs in logs

    """
    def __init__(
            self,
            contamination=0.05,
            max_features=5000,
            ngram_range=(1, 2),
            n_estimators=100,
            random_state=None
    ):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            lowercase=True
        )

        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=n_estimators
        )

    def _remove_timestamp_and_normalize(self, log: str) -> str:
        """
            Assumes timestamp is at the beginning of the log line.
            Example:
                2026-03-01T10:21:11Z ...

            devnote: can change later to customize on the basis of location
                     in log line
        """
        # timestamp removal
        log = re.sub(r"^\S+\s+", "", log)

        # IP address
        log = re.sub(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", "<IP>", log)

        # usernames
        log = re.sub(r"User\s+\w+", "User <USER>", log)

        # file paths
        log = re.sub(r"/[A-Za-z0-9_\-./]+", "<PATH>", log)

        # response time
        log = re.sub(r"response_time=\d+(\.\d+)?ms", "response_time=<NUM>ms", log)

        return log
    
    def preprocess(self, logs):
        return [self._remove_timestamp_and_normalize(log) for log in logs]


    def train(self, logs):
        logs = self.preprocess(logs)

        X = self.vectorizer.fit_transform(logs)
        self.model.fit(X)


    def predict(self, logs):
        """
            normal  :  1
            anomaly : -1
        """
        logs = self.preprocess(logs)
        X = self.vectorizer.transform(logs)
        return self.model.predict(X)
    
    def score_samples(self, logs):
        """
            higher = normaler
            lower = more anomalous
        """
        logs = self.preprocess(logs)
        X = self.vectorizer.transform(logs)

        return self.model.decision_function(X)
    
    def evaluate(self, logs, labels, verbose=True):
        preds = self.predict(logs)
        preds_binary = np.array([1 if p == -1 else 0 for p in preds])

        conf_matrix = confusion_matrix(labels, preds_binary)
        class_report = classification_report(labels, preds_binary)

        if verbose:
            print("Confusion Matrix:")
            print(conf_matrix)
            print("\nClassification Report:")
            print(class_report)

        return {
            "confusion_matrix": conf_matrix,
            "classification_report": class_report
        }

    def save(self, path):
        joblib.dump((self.vectorizer, self.model), path)

    def load(self, path):
        self.vectorizer, self.model = joblib.load(path)


class TfIdfLogRegModel:
    """
        Logistic Regression model for classifying normal vs anomalous logs
        TFIDF vectorizer used to represent log text into numerical format
    """
    def __init__(
            self,
            max_features=10000,
            ngram_range=(1, 2),
            min_df=2,
            C=1.0,
            class_weight="balanced",
            random_state=None
    ):

        self.vectorizer = TfidfVectorizer(
            ngram_range=ngram_range,
            max_features=max_features,
            min_df=min_df,
            lowercase=True
        )

        self.model = LogisticRegression(
            C=C,
            class_weight=class_weight,
            max_iter=1000,
            random_state=random_state,
            solver="liblinear"
        )

        self.threshold = 0.5

    def _remove_timestamp_and_normalize(self, log: str) -> str:
        log = re.sub(r"^\S+\s+", "", log)
        log = re.sub(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", "<IP>", log)
        log = re.sub(r"User\s+\w+", "User <USER>", log)
        return log

    def preprocess(self, logs):
        return [self._remove_timestamp_and_normalize(log) for log in logs]

    def train(self, logs, labels):
        logs = self.preprocess(logs)
        X = self.vectorizer.fit_transform(logs)
        self.model.fit(X, labels)

    def score_samples(self, logs):
        logs = self.preprocess(logs)
        X = self.vectorizer.transform(logs)
        return self.model.predict_proba(X)[:, 1]

    def predict(self, logs):
        probs = self.score_samples(logs)
        return (probs >= self.threshold).astype(int)

    def tune_threshold(self, logs, labels):
        probs = self.score_samples(logs)
        fpr, tpr, thresholds = roc_curve(labels, probs)
        optimal_idx = np.argmax(tpr - fpr)
        self.threshold = thresholds[optimal_idx]
        return self.threshold

    def evaluate(self, logs, labels, verbose=True):
        probs = self.score_samples(logs)
        preds = (probs >= self.threshold).astype(int)

        roc_auc = roc_auc_score(labels, probs)
        conf_matrix = confusion_matrix(labels, preds)
        class_report = classification_report(labels, preds)

        if verbose:
            print("ROC-AUC:", roc_auc)
            print("=" * 80)
            print("Threshold:", self.threshold)
            print("=" * 80)
            print("Confusion Matrix:")
            print(conf_matrix)
            print("\nClassification Report:")
            print(class_report)

        return {
            "roc_auc": roc_auc,
            "confusion_matrix": conf_matrix,
            "classification_report": class_report
        }

    def save(self, path):
        joblib.dump((self.vectorizer, self.model, self.threshold), path)

    def load(self, path):
        self.vectorizer, self.model, self.threshold = joblib.load(path)

## DEBUG
if __name__ == "__main__":
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.metrics import roc_auc_score, roc_curve
    import numpy as np

    import jsonlines

    cuh = []
    with jsonlines.open("../logs_data_train.jsonl") as reader:
        for log in reader:
            cuh.append((log['log_message'], log['category']))

    from sklearn.model_selection import train_test_split


    X = [x[0] for x in cuh]
    y = [1 if x[1] == "anomaly" else 0 for x in cuh]

    X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                       test_size=0.2, 
                                                        stratify=y,
                                                        random_state=42)
    
    model = TfIdfLogRegModel()
    model.train(X_train, y_train)
    model.tune_threshold(X_test, y_test)
    model.evaluate(X_test, y_test, verbose=True)


    
    ### testing the isolationforest model
   
    X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                       test_size=0.2, 
                                                        stratify=y,
                                                        random_state=42)
    
    X_train_normal = [i for i,j in zip(X_train, y_train) if j == 0]
    y_train_normal= [j for j in y_train if j == 0]

    print(len(X_train_normal), len(y_train_normal))
    model = TfIdfIsolationModel(contamination=0.5)
    model.train(X_train_normal)

    y_test_preds = [1 if value == -1 else 0 for value in model.predict(X_test)]
    y_test_true = [1 if value == 'anomaly' else 0 for value in y_test]

    model.evaluate(X_test, y_test)

    