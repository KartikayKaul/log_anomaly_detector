# Log Anomaly Detector
welcome welcome! We use an ML approach to detect anomalies in log files. We incorporate both supervised and unsupervised models with high recall rate to detect anomalies. THe project is divided into three major packages/modules:-
- core - with most of  the core logic and functionalities
- cli - this contains scripts to allow user to run workflows
- webapp - this package contains the django project that exposes some APIs on the frontend such as uploading config file to generate data and also test a log line or bunch of lines from a file.

## Folder structure
```bash
log_anomaly_detector/
│
├── README.md  [you are here. henlo :3]
├── requirements.txt 
│
├── assets/
│   ├── configs/   
│   ├── data/
│   ├── logs/
│   ├── model_saves/
│   └── temp/
│
├── core/
│   ├── load_config.py
│   ├── dataloader.py
│   ├── Factory.py
│   ├── data_pipeline.py
│   └── utils.py
│
├── cli/
│   ├── detect.py
│   ├── train.py
│   └── generate_data.py
│
└── webapp/ (Django)
    ├── manage.py
    │
    ├── ...
    ...
```

- **core**: contains the core modules and functionalities
- **assets**: the underlying folder structure can be used to save different kinds of persistent data. However, it is primarily dedicated for saving files using the django webpage implementations.
- **cli**: CLI scripts that integrate workflows such as `data generation`, `model training/testing` and `detection`
- **webapp**: django. :3

## Installation Guide
- Create a python virtual environment in the root folder, `python -m venv <foldername>`
- Activate the environment, `source ./<foldername>/bin/activate`
- Install requirements `pip install -r requirements.txt`
- Install project's modules (core, cli), `pip install -e .`
- You have installed the core and cli modules successfully. Now you can start your work.

## Modules
- Both core and cli modules have some important functionalities and logic implemented in both. From loading config files to synthetic data generation pipeline.
- `core` contains all the functionalities that are essential ot the project
- `cli` contains modules that allow a human to generate data, train/test models and detect anomalies using command line interface but it does have some functions that are used by the webapp to run some stuff
- `webapp` is not part of the log_anomaly_detector library, it is present in root just to expose some APIs to users using a web interface- detection, upload config files to generate data.

## CLI usage guide
- to generate data
    `python -m cli.generate_data  --config <path/to/config.yaml> --json <savepath/for/jsonl> --log <path/to/rawlogfile.log>`

  this command is used to generate the JSONL file data (for training supervised models) and raw log files.

- to train or test, a simple command looks like
    ``python -m cli.modelling train --data <location> --model-path <path/to/serializedmodel> --model-save-name <savenamemodel> --tune-threshold`

   This invokes training for the model. the data is retrieved using `data` flag, model-path will store the location of where the serialized model will be saved, model-save-name tells what the name of the serialized save file will be. tune-threshold is the property to adjust the threshold of the logistic regression model.

   you can always call `python -m cli.modelling -h` to know what each flag does
- For detection you call `cli.detect` module. 
    example, ``python -m cli.detect logreg --model-path "assets/model_saves/logreg.joblib" --log-line "2026-02-01Z12:15:32.2345T [INFO] ...."`

Planning to add more refined guide to this soon. ASAP no ROCKY.
    
## Running Django
Currently, you can deploy this django server locally and work with two of the exposes APIs through the given frontend. Steps are given below.

- Navigate to the webapp folder from root folder `cd webapp`
- Migration first! `python -m manage migrate`. This will set some necessary things up.
- Now you can run the server. `python -m manage runserver`. You will get the URI to view the webpage to use the APIs in the command line itself.


# Contributors
- [Kartikay kaul](https://github.com/KartikayKaul)
- [Harsh Padiyar](https://github.com/H4rryC0d3)