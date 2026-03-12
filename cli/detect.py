import argparse
from pathlib import Path

from core.models import TfIdfIsolationModel, TfIdfLogRegModel

def load_model(model_type, model_path):
    if model_type == "logreg":
        model = TfIdfLogRegModel()
    elif model_type == "isolation":
        model = TfIdfIsolationModel()
    else:
        raise ValueError("Unknown model type")
    
    model.load(model_path)
    return model

def detect_logs(model, model_type, logs):
    results = []

    if model_type == "logreg":
        probs = model.score_samples(logs)
        preds = (probs >= model.threshold).astype(int)

        for log, prob, pred in zip(logs, probs, preds):
            results.append({
                "log": log,
                "score": float(prob),
                "prediction": int(pred),
                "label": "anomaly" if pred == 1 else "normal"
            })

    else:  # isolation
        scores = model.score_samples(logs)
        preds = model.predict(logs)

        for log, score, pred in zip(logs, scores, preds):
            binary = 1 if pred == -1 else 0
            results.append({
                "log": log,
                "score": float(score),
                "prediction": binary,
                "label": "anomaly" if binary == 1 else "normal"
            })

    return results

def main():
    parser = argparse.ArgumentParser(description="Detect anomalies in logs")

    parser.add_argument("--model", required=True, choices=["logreg", "isolation"], help="Pick your choice of ML model to detect with.")
    parser.add_argument("--model-path", required=True, help="path to where persistent model parameters")
    parser.add_argument("--input-file" help="path to the log file")
    parser.add_argument("--log-line", help="single line log input")
    parser.add_argument("--output-file", help="path to where results will be posted")

    args = parser.parse_args()

    if not args.input_file and not args.log_line:
        raise ValueError("Provide either --input-file or --log-line")

    model = load_model(args.model, args.model_path)

    if args.log_line:
        logs = [args.log_line]
    else:
        with open(args.input_file, "r") as f:
            logs = [line.strip() for line in f if line.strip()]

    results = detect_logs(model, args.model, logs)

    # Console output
    if not args.output_file:
        for r in results:
            print("=" * 70)
            print(f"Log: {r['log']}")
            print(f"Prediction: {r['label']}")
            print(f"Score: {r['score']}")
    else:
        with open(args.output_file, "w") as f:
            for r in results:
                f.write(str(r) + "\n")

        print(f"Results written to {args.output_file}")


if __name__ == "__main__":
    main()