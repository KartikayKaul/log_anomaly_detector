import yaml
from pathlib import Path

def load_config(file_name: str="config.yaml", path: Path=".") -> dict:
    """
     loads the configuration to generate data from YAML config file
        PARAMETERS:
            file_name: str, default value is config.yaml
            path: str/Path, directory path, default value is .
        
        RETURNS
            dictionary with configuration
    """
    
    assert isinstance(file_name, str), "`file_name` has to be a str object"
    assert isinstance(path, (Path, str)), "`path` has to be etiher str or Path object"

    file_path = Path(path) / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"File is not present at given location `{file_path}`")
    
    config_data = yaml.safe_load(open(file_path))


    # little wittle validation
    required_top_keys = {"version", "fields", "generation", "log_format", "templates"}
    missing_keys = required_top_keys - config_data.keys()

    if missing_keys:
        raise ValueError("Missing critical keys from config file: " + ", ".join(missing_keys))
    
    return config_data

## DEBUG
if __name__ == "__main__":
    pass