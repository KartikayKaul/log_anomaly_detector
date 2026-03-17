"""
    MODELS
        all ML model architectures are to be defined here
        
""";
import numpy as np
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, roc_curve, roc_auc_score, confusion_matrix, classification_report


## CONSTANTS
LOG_STRUCTURE_PATTERN = re.compile(
r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z "
r"\[(INFO|WARN|ERROR|DEBUG)\] - "
r"[a-zA-Z\-]+ ∣ "
r"ip=\d{1,3}(?:\.\d{1,3}){3} - "
r".+"
)

## UTIL functions
def structure_valid(log: str) -> bool:
    """
        rule based structure filtering
    """
    return bool(LOG_STRUCTURE_PATTERN.match(log))

def add_structure_token(log: str) -> str:
    if structure_valid(log):
        return "STRUCT_OK " + log
    else:
         return "STRUCT_BAD " + log


## MODELS
class TfIdfIsolationModel:
    """
        IsolationForest Model with TFIDF vectorizer for representing the text of inputs in logs

    """
    def __init__(
            self,
            contamination=0.05,
            max_features=10000,
            ngram_range=(2, 3),
            n_estimators=100,
            random_state=None
    ):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            lowercase=True,
            analyzer="char_wb"
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
        # normalize timestamps
        log = re.sub(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z",
            "<TIME>",
            log
        )
        # normalize IP addresses
        log = re.sub(
            r"\b\d{1,3}(?:\.\d{1,3}){3}\b",
            "<IP>",
            log
        )
        # normalize file paths
        log = re.sub(
            r"/[A-Za-z0-9_\-./]+",
            "<PATH>",
            log
        )
        # normalize UUID-like tokens
        log = re.sub(
            r"\b[0-9a-f]{8}-[0-9a-f\-]{27}\b",
            "<ID>",
            log,
            flags=re.IGNORECASE
        )
        # normalize standalone numbers
        log = re.sub(
            r"\b\d+\b",
            "<NUM>",
            log
        )
        log = re.sub(
            r"\b[a-zA-Z0-9]{16,}\b",
            "<HASH>",
            log
        )
        return log
    
    def preprocess(self, logs):
        processed = []

        for log in logs:
            # log = add_structure_token(log) # structure awareness
            log = self._remove_timestamp_and_normalize(log)

            processed.append(log)

        return processed
    
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
    
    def predict_binary(self, logs):
        preds = self.predict(logs)
        return np.array([1 if p == -1 else 0 for p in preds])

    def score_samples(self, logs):
        """
            higher = normaler
            lower = more anomalous
        """
        logs = self.preprocess(logs)
        X = self.vectorizer.transform(logs)

        return self.model.decision_function(X)
    
    def evaluate(self, logs, labels, verbose=True):
        preds_binary = self.predict_binary(logs)

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
            max_features=5000,
            ngram_range=(2, 3),
            min_df=2,
            C=1.0,
            class_weight="balanced",
            random_state=None,
            max_iter=1000,
            verbose=False
    ):

        self.vectorizer = TfidfVectorizer(
            ngram_range=ngram_range,
            max_features=max_features,
            min_df=min_df,
            lowercase=True,
            analyzer="char_wb"
        )

        self.model = LogisticRegression(
            C=C,
            class_weight=class_weight,
            max_iter=max_iter,
            random_state=random_state,
            solver="liblinear",
            verbose=verbose
        )

        self.threshold = 0.5

    def _remove_timestamp_and_normalize(self, log: str) -> str:
        # normalize timestamps
        log = re.sub(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z",
            "<TIME>",
            log
        )
        # normalize IP addresses
        log = re.sub(
            r"\b\d{1,3}(?:\.\d{1,3}){3}\b",
            "<IP>",
            log
        )
        # normalize file paths
        log = re.sub(
            r"/[A-Za-z0-9_\-./]+",
            "<PATH>",
            log
        )
        # normalize UUID-like tokens
        log = re.sub(
            r"\b[0-9a-f]{8}-[0-9a-f\-]{27}\b",
            "<ID>",
            log,
            flags=re.IGNORECASE
        )
        # normalize standalone numbers
        log = re.sub(
            r"\b\d+\b",
            "<NUM>",
            log
        )
        log = re.sub(
            r"\b[a-zA-Z0-9]{16,}\b",
            "<HASH>",
            log
        )
        return log

    def preprocess(self, logs):
        processed = []
        for log in logs:
            # log = add_structure_token(log)
            log = self._remove_timestamp_and_normalize(log)
            processed.append(log)
        return processed
    
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
        f1 = f1_score(labels, preds)
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
            "f1": f1,
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

    