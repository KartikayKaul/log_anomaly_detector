from pathlib import Path
from core.load_config import load_config
from core.Dataloader import dataloader
from core.Factory import LogFieldEngine, generateLogFileFromJSON, timestomper
import jsonlines
import re
from string import Formatter
import random

def generate_data(config_path: str, json_out: str, log_out: str):
    """
        data generation pipeline function. It generates JSON train/test data file
        as well as raw log file

        PARAMETERS
            config_path: path to YAML configuration file
            json_out: path where JSON output will be saved
            log_out: path where raw log output will be saved
        RETURNS
            None
    """

    config = load_config(config_path)
    start_time, end_time, n_logs, normal_prob = config['generation'].values()

    log_format = config['log_format']['structure']
    ts_format = config['log_format']['timestamp_format']

    timestamps = timestomper(n_logs, start_time, end_time, ts_format)

    template_list = config['templates']
    fields = config['fields']

    logs = dataloader(n_logs, template_list, normal_prob)
    
    fields_engine = LogFieldEngine(fields)

    # writing to json file
    with jsonlines.open(json_out, mode='w') as writer:
        for log in logs:
            # populate message field str with values
            msg_names = [field_name for _, field_name, _, _ in  Formatter().parse(log['message']) if field_name]
            msg_spec = { msg_name:fields_engine.generate_field(msg_name) for msg_name in msg_names}
            message = log['message']
            message = message.format(**msg_spec)

            ts_val = next(timestamps)
            # populate logs with values
            log_spec = {
                'timestamp': ts_val,
                'level': log['level'],
                'service':log['service'],
                'ip': fields_engine.generate_field('ip'),
                'message': message
            }
            log_line = log_format.format(**log_spec)
        
            json_line = {
                'event_name': log['name'], 
                'category': log['category'], 
                'log_message': log_line
            }

            writer.write(json_line)

    # rawdog logs :3
    generateLogFileFromJSON(json_out, log_out)


def generate_data_GPIO(input_file: str, output_file: str, test_size: float=0.0, shuffle: bool=True):
    """
    Produce JSON train/test file for models from the raw GPIO sensor data. This function
    will successfully generate data only for the GPIO project data (https://github.com/vishnugi/new_gpio)
        PARAMETERS
            input_file: str, path(abs or rel) to the location of GPIO sensor data
            output_file: str, path(abs or rel) where JSON file will be saved
    """

    input_file, output_file = Path(input_file), Path(output_file)
    if not input_file.exists():
        raise FileNotFoundError(f"input file does not exists at given path: `{input_file}`")
    

    # patterns
    temp_pattern = re.compile(
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+ - Temperature: .* °C, Humidity: .*%"
    )
    device_pattern = re.compile(
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+ - INFO - device_\d+ - .*°C - .*%"
    )

    # enclosed function
    def is_anomaly(line: str) -> bool:
        if "ERROR" in line:
            return True
        if temp_pattern.match(line):
            return False

        if device_pattern.match(line):
            return False
        return True

    if test_size > 0.:
        train_file = output_file.with_stem(f"{output_file.stem}_train")
        test_file = output_file.with_stem(f"{output_file.stem}_test")

        records = []
        with open(input_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record = {
                    "log_message": line,
                    "category": "anomaly" if is_anomaly(line) else "normal"
                }
                records.append(record)
        
        if shuffle:
            random.shuffle(records) 
        
        with jsonlines.open(train_file, "w") as train_writer, jsonlines.open(test_file, "w") as test_writer:
            split_index = int(len(records) * test_size)
            test_writer.write_all(records[:split_index])
            train_writer.write_all(records[split_index:])

    else:
        with open(input_file) as f, jsonlines.open(output_file, "w") as out:
            for line in f:
                line = line.strip()
                if not line:
                    continue
            
                record = {
                    "log_message": line,
                    "category": "anomaly" if is_anomaly(line) else "normal"
                }

                out.write(record)
    print(f"GPIO sensor training data generated successfully from the logs.")
    
    
    

