import argparse
from core.data_pipeline import generate_data
from pathlib import Path

def main():
    """
        hello :3
        we generate data using this. that is all
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="templates/config.yaml", help="Path to the config file. Can be either absolute or relative path")
    parser.add_argument("--json", default="assets/data/jsonlogs.jsonl", help="path where json file will be saved")
    parser.add_argument("--log", default="assets/logs/logs.log", help="path to where the raw logs will be saved.")

    args = parser.parse_args()

    generate_data(
        config_path=args.config,
        json_out=args.json,
        log_out=args.log
    )

    print("Log data generated successfully...")

if __name__ == "__main__":
    main()

