# log_anomaly_detector


## Installation Guide
- Create a python virtual environment in the root folder, `python -m venv <foldername>`
- Install requirements `pip install -r requirements.txt`
- Install project's modules (core, cli), `pip install -e .`
- You have installed the core and cli modules successfully. Now you can start your work.

## Modules
- Both core and cli modules have some important functionalities and logic implemented in both. From loading config files to synthetic data generation pipeline.
- `core` contains all the functionalities that are essential ot the project
- `cli` contains modules that allow a human to generate data, train/test models and detect anomalies using command line interface but it does have some functions that are used by the webapp to run some stuff
- `webapp` is not part of the log_anomaly_detector library, it is present in root just to expose some APIs to users using a web interface- detection, upload config files to generate data.

## CLI guide
- to generate data
    `python -m cli.generate_data  --config <path/to/config.yaml> --json <savepath/for/jsonl> --log <path/to/rawlogfile.log>`

  this command is used to generate the JSONL file data (for training supervised models) and raw log files.

- to train or test, a simple command looks like
    ``python -m cli.modelling train --data <location> --model-path <path/to/serializedmodel> --model-save-name <savenamemodel> --tune-threshold`

   This invokes training for the model. the data is retrieved using `data` flag, model-path will store the location of where the serialized model will be saved, model-save-name tells what the name of the serialized save file will be. tune-threshold is the property to adjust the threshold of the logistic regression model.

   you can always call `python -m cli.modelling -h` to know what each flag does
- For detection you call `cli.detect` module. 
    example, ``python -m cli.detect logreg --model-path "assets/model_saves/logreg.joblib" --log-line "2026-02-01Z12:15:32.2345T [INFO] ...."`
    