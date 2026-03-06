"""
    FACTORY
        The whole Bakery is here.
        :3 I am a factory! meow!
""";

from datetime import datetime, timedelta
import numpy as np
from faker import Faker
import random
from pathlib import Path
import jsonlines

def timestomper(n: int,
                start: str,
                end: str,
                fmt: str="%Y-%m-%dT%H:%M:%SZ"
            ):
    """
        
    """

    start = datetime.strptime(start, fmt)
    end = datetime.strptime(end, fmt)
    total_seconds = (end - start).total_seconds()

    # random gaps
    offsets = sorted(random.uniform(0, total_seconds) for _ in range(n))

    for offset in offsets:
        yield (start + timedelta(seconds=offset)).isoformat()

def generateLogFileFromJSON(json_file_path: str, log_file_path: str='.'):
    """
        Generates raw log file from the processed
        jsonl file generated from YAML config file

        PARAMETERS:
            json_file_path: relative/absolute  path to JSON file along with name
            log_file_path: relative/absolute path to where you want to save log file

        RETURNS
            Nothing
    """
    assert isinstance(json_file_path, (Path,str)), "`json_file_path` has to be a str object"
    assert isinstance(log_file_path, (Path, str)), "`log_file_path` has to be either str or Path object"

    json_path = Path(json_file_path)
    log_path = Path(log_file_path)

    if not json_path.exists():
        raise FileNotFoundError(f"File is not present at given location `{json_path}`")
    
    with jsonlines.open(json_path, mode="r") as reader, open(log_path, mode="w") as writer:
        for log_line in reader:
            writer.write(log_line['log_message'] + '\n')

    

# a wittle abstraction hurt nobody
class FieldGenerator:
    """

    """

    def __init__(self, config):
        self.config = config
    
    def generate(self):
        raise NotImplementedError
    

class FakerField(FieldGenerator):
    def __init__(self, config, faker_instance):
        super().__init__(config)
        self.faker = faker_instance

    def generate(self):
        provider = self.config['provider']
        return getattr(self.faker, provider)()

class StringField(FieldGenerator):
    def generate(self):
        values = self.config['values']
        return random.choice(values)
    
class IntCField(FieldGenerator):
    def generate(self):
        values = self.config['values']
        return random.choice(values)
    
class IntDField(FieldGenerator):
    def generate(self):
        distribution = self.config.get("distribution", "uniform")
        if distribution == "normal":
            mean = self.config["mean"]
            std = self.config["std"]

            value = np.random.normal(mean, std)
            return max(0, int(round(value)))
        
        elif distribution == "uniform":
            min_val = self.config["min"]
            max_val = self.config["max"]
            return random.randint(min_val, max_val)
        else:
            raise NotImplementedError
        
class FloatField(FieldGenerator):
    def generate(self):
        distribution = self.config.get("distribution", "uniform")

        if distribution == "normal":
            mean = self.config['mean']
            std = self.config['std']
            value = np.random.normal(mean, std)

            return max(0, round(value, 2))
        
        elif distribution == "uniform":
            min_val = self.config["min"]
            max_val = self.config["max"]
            return round(random.uniform(min_val, max_val), 2)

## FIELD FACTORY
FIELD_TYPE_REGISTRY = {
    "faker": FakerField,
    "str": StringField,
    "int_c": IntCField,
    "int_d": IntDField,
    "float": FloatField
}

class LogFieldEngine:
    """
        LogFieldEngine allows one to instantiate field
        data using their corresponding generators
    
    """

    def __init__(self, field_configs: dict):
        self.faker = Faker()
        self.generators = {}

        for field_name, config in field_configs.items():
            field_type = config["type"]
            generator_class = FIELD_TYPE_REGISTRY[field_type]

            if field_type == "faker":
                self.generators[field_name] = generator_class(config, self.faker)
            else:
                self.generators[field_name] = generator_class(config)

    
    def generate_field(self, field_name: str):
        return self.generators[field_name].generate()
    
    def generate_all(self):
        return {
            field: generator.generate()
            for field, generator in self.generators.items()
        }


