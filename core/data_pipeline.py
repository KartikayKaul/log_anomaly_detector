from pathlib import Path
from core.load_config import load_config
from core.Dataloader import dataloader
from core.Factory import LogFieldEngine, generateLogFileFromJSON, timestomper
import jsonlines
from string import Formatter

def generate_data(config_path: str, json_out: str, log_out: str):

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


