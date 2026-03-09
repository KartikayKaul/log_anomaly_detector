import argparse
import jsonlines
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from core.models import TfIdfIsolationModel, TfIdfLogRegModel

DEFAULT_SAVE_DIR = Path("assets/model_saves")

def load_data(path: Path):
    logs = []
    labels = []
    with jsonlines.open(path) as reader:
        for log in reader:
            logs.append(log["log_message"])
            labels.append(1 if log['category'] == 'anomaly' else 0)

    return logs, labels

def train_model(args):
    logs, labels = load_data(args.data)

    X_train, X_test, y_train, y_test = train_test_split(
        logs,
        labels,
        test_size=args.test_size,
        stratify=labels,
        random_state=args.random_state
    )

    if args.model == "logreg":
        model = TfIdfLogRegModel()
        model.train(X_train, y_train)
        if args.tune_threshold:
            model.tune_threshold(X_test, y_test)

        model.evaluate(X_test, y_test, args.verbose==True)

    elif args.model == "isolation":
        model = TfIdfIsolationModel(
            contamination=args.contamination,
            random_state=args.random_state
        )

        X_train_normal = [x for x, y in zip(X_train, y_train) if y == 0]
        model.train(X_train_normal)
        model.evaluate(X_test, y_test, args.verbose==True)

    else:
        raise ValueError("Unknown model")
    
    DEFAULT_SAVE_DIR.mkdir(parents=True, exist_ok=True)

    save_path = Path(args.model_path) if args.model_path else DEFAULT_SAVE_DIR
    save_path = save_path / (f"{args.model_save_name}.joblib" if args.model_save_name else f"{args.model}.joblib")
    
    print(save_path)
    model.save(save_path)
    print(f"\nModel saved at: {save_path}")


def test_model(args):
    logs, labels = load_data(args.data)

    if not args.model_path:
        raise ValueError("Testing requires --model-path")

    if args.model == "logreg":
        model = TfIdfLogRegModel()
        model.load(args.model_path)

        if args.threshold:
            model.threshold = args.threshold

        model.evaluate(logs, labels, args.verbose==True)

    elif args.model == "isolation":
        model = TfIdfIsolationModel()
        model.load(args.model_path)
        model.evaluate(logs, labels, args.verbose==True)

    else:
        raise ValueError("Unknown model")

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("mode", choices=["train", "test"], help="Pick your mode to either train or test")
    parser.add_argument("--model", required=True, choices=["logreg", "isolation"])
    parser.add_argument("--data")
    parser.add_argument("--model-path", default="assets/model_saves")
    parser.add_argument("--model-save-name")
    parser.add_argument("--contamination", type=float, default=0.1)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=None)
    parser.add_argument("--tune-threshold", action="store_true")
    parser.add_argument("--threshold", type=float)
    parser.add_argument("--verbose", type=float)
    
    args = parser.parse_args()

    if args.mode == "train":
        train_model(args)
    else:
        test_model(args)

if __name__ == "__main__":
    main()