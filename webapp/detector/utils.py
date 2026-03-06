from cli.detect import load_model, detect_logs
from pathlib import Path

def detect(log_line, model_type="logreg"):
    model = load_model(model_type, "../assets/model_saves/"+model_type+".joblib")
    
    results = detect_logs(model, model_type, [log_line] if isinstance(log_line, str) else log_line)
    print("running model...")
    return [result['label'] for result in results]

