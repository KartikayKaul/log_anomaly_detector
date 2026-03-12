import argparse
from core.data_pipeline import generate_data
from pathlib import Path
from core.Factory import generateLogFileFromJSON
import jsonlines
from sklearn.model_selection import train_test_split

def main():
    """
        hello :3
        we generate data using this. that is all
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="templates/config.yaml", help="Path to the config file. Can be either absolute or relative path")
    parser.add_argument("--json", default="assets/data/jsonlogs.jsonl", help="path where json file will be saved")
    parser.add_argument("--log", default="assets/logs/logs.log", help="path to where the raw logs will be saved.")
    parser.add_argument("--split", type=float, help="split dataset into train/test (example: 0.2)")
    parser.add_argument("--train-save-name", default="trains", help="name of train file. without file extension")
    parser.add_argument("--test-save-name", default="tests", help="test file save name. without file extension.")
    args = parser.parse_args()

    generate_data(
        config_path=args.config,
        json_out=args.json,
        log_out=args.log
    )

    if args.split:
        logs = []
        json_path = Path(args.json)
        with jsonlines.open(json_path) as reader:
            for row in reader:
                logs.append(row)

        train, test = train_test_split(
            logs,
            test_size=args.split
        ) 

        train_path = json_path.with_name(args.train_save_name+".jsonl")
        test_path = json_path.with_name(args.test_save_name+".jsonl")

        with jsonlines.open(train_path, "w") as w:
            w.write_all(train)

        with jsonlines.open(test_path, "w") as w:
            w.write_all(test)
        
        generateLogFileFromJSON(str(train_path), str(Path(args.log).with_name(args.train_save_name+".log")))
        generateLogFileFromJSON(str(test_path), str(Path(args.log).with_name(args.test_save_name+".log")))

        print("\nDataset Split Complete")
        print(f"Train dataset --> {train_path}")
        print(f"Test dataset  --> {test_path}")

    print("Log data generated successfully...")

if __name__ == "__main__":
    main()

