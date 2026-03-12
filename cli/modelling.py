import argparse
import jsonlines
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from core.models import TfIdfIsolationModel, TfIdfLogRegModel

DEFAULT_SAVE_DIR = Path("assets/model_saves")

def load_data(path: Path) -> tuple[list]:
    """
        returns a tuple of logs and its corresponding labels
    """
    logs = []
    labels = []
    with jsonlines.open(path) as reader:
        for log in reader:
            logs.append(log["log_message"])
            labels.append(1 if log['category'] == 'anomaly' else 0)

    return logs, labels

def train_model(args):
    """
        train your model based on the arguments provided in CLI
    """
    logs, labels = load_data(args.data)

    if args.verbose:
        print("\n==============================")
        print("Dataset Information")
        print("==============================")
        print(f"Total logs: {len(logs)}")
        print(f"Anomalies: {sum(labels)}")
        print(f"Normal: {len(labels) - sum(labels)}")
        print("==============================\n")

    X_train, X_test, y_train, y_test = train_test_split(
        logs,
        labels,
        test_size=args.test_size,
        stratify=labels,
        random_state=args.random_state
    )

    if args.verbose:
        print("Train/Test Split")
        print(f"Train size: {len(X_train)}")
        print(f"Test size : {len(X_test)}\n")

    if args.model == "logreg":
        model = TfIdfLogRegModel(verbose=args.verbose==True)
        model.train(X_train, y_train)
        if args.tune_threshold:
            model.tune_threshold(X_test, y_test)
        
        if args.threshold_grid and not args.tune_threshold:
           
            if args.verbose:
                print("\nThreshold tuning...")

            best_score = -float("inf")
            best_threshold = None

            for t in args.threshold_grid:
                model.threshold = t
                result = model.evaluate(X_test, y_test, verbose=False)
                score = result['f1']

                if args.verbose:
                    print(f"Threshold {t} --> F1: {score}")

                if score > best_score:
                    best_score = score
                    best_threshold = t
            
            model.threshold = best_threshold
            print(f"\nBest threshold: {best_threshold}")
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
    
    model.save(save_path)
    print(f"\nModel saved at: {save_path}")


def test_model(args):
    """
        test your saved model based on the CLI arguments
    """
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
    """
        bossman function right here :3
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("mode", choices=["train", "test"], help="train or test mode")
    parser.add_argument("--model", required=True, choices=["logreg", "isolation"], help="Model choices to pick from. Currently there are two options.")
    parser.add_argument("--data", required=True, help="path to the JSON data for training or testing")
    parser.add_argument("--model-path", default="assets/model_saves", help="path to the model")
    parser.add_argument("--model-save-name", help="name of the joblib file to saved the model. Note: exclude .joblib extension from the name")
    parser.add_argument("--contamination", type=float, default=0.1, help="contamination value for anomalies present. Only use with isolation model.")
    parser.add_argument("--test-size", type=float, default=0.2, help="use with train mode for testi")
    parser.add_argument("--random-state", type=int, default=None, help="set value to be able to repeat your experiments.")
    parser.add_argument("--tune-threshold", action="store_true", help="Used with logreg. The ML model will adjust the threshold value itself based on given data.")
    parser.add_argument("--threshold", type=float, help="manual threshold value for logistic regression model.")
    parser.add_argument("--threshold-grid", nargs="+", type=float, help="Try out multiple threshold forl ogistic regression model training.")
    parser.add_argument("--verbose", type=float, help="print results from test mode. classification report and confusion matrix")

    args = parser.parse_args()

    if args.mode == "train":
        train_model(args)
    else:
        test_model(args)

if __name__ == "__main__":
    main()