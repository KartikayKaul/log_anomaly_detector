# Log Anomaly Detector
welcome welcome! We use an ML approach to detect anomalies in log files. We incorporate both supervised and unsupervised models with high recall rate to detect anomalies. THe project is divided into three major packages/modules:-
- core - with most of  the core logic and functionalities
- cli - this contains scripts to allow user to run workflows
- webapp - this package contains the django project that exposes some APIs on the frontend such as uploading config file to generate data and also test a log line or bunch of lines from a file.

## Folder structure
```bash
log_anomaly_detector/
│
├── README.md  [you are here. :3]
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
The three CLI package commands are explained below with 1 or 2 usage examples. One can also call `-h` or `--help` argument like `python -m cli.modelling -h` to get the use of each command or look at the reference below.

- **`cli.generate_data`**: This CLI command can be called using `python -m cli.generate_data` followed by the arguments. The command allows one to generate data from the given YAML configuration file. if argument not provided, it will look for `config.yaml` in `templates` folder. There is a default server log config file present which is sample data to work with.
   
   Below is the table describing each argument. All arguments are optional.
   |  argument  |  value type  |  default value |                 description | 
   | --------- | ------------ | ---------------------------- | ------------ |
   |  `--config`|  string      | `'templates/config.yaml'` |  path to the config file. can be either absolute or relative path |
   |  `--json` | string   | `'assets/data/jsonlogs.jsonl'` | path where json file will be saved |
   |  `--log` |  string   | `'assets/logs/logs.log'`  |  path to where the raw logs will be saved |
   | `--split`  |   float  |  :x:  | test size split percentage value  |
   | `--train-save-name` | string  | `'trains'` | name of the train data file. without file extension |
   | `--test-save-name` | string | `'tests'` | name of test data file. without file extension |
   | `--GPIO` | boolean flag | :x: | if this flag is enabled then workflow will change. Log file input at `--log` path will be processed to generate GPIO training and testing data |

    

- **`cli.modelling`**: This command can be called using `python -m cli.modelling` followed by the arguments. This command allows one to train a model and evaluate it in test mode. Below is table describing each argument.

   |  argument  |  value type  |  default value |                 description |  optional/required? |
   | --------- | ------------ | ---------------------------- | ------------ |  ------------|
   |  `mode`   |    <details><summary>choice</summary><ul><li>train</li><li>test</li></ul></details>    |      :x: <small> it defaults to test </small>  |   positional argument. pick train or test mode. |  optional |
   |  `--model` |   <details><summary>choice</summary><ul><li>logreg</li><li>isolation</li></ul></details>   | :x: | choices of models to pick from to train or evaluate. currently there are only two options | required |
   | `--data` | string |  :x: | path to the JSONL file for training or testing | reqruired |
   | `--model-path` | string | `'assets/model_saves'` | path to where the model is saved or to be saved | optional |
   | `--model-save-name` | string |  :x: | name of the file that saves model state on disk. If not given, value interpreted from default model save location and name. | optional |
   | `--contamination` | float | 0.1 | contamination value for anomalies present in the given data. This is to be used only with training of isolation model. | optional |
   | `--test-size` | float | 0.2 | this value can be set in `train` mode for the validation set size to set the test(validation) dataset size. | optional |
   | `--random-state` | int | `None` | seeding for repeatable results/experiments. default set to `None` to disable seeding. | optional |
   | `--tune-threshold` | boolean flag | `False` | if added in command, it allows the ML model of logistic regression to tune it's boundary threshold based on F1 ROC_AUC scores. | optional |
   | `--threshold` | float | :x: | setting manual threshold value. this bypasses `tune-threshold` | optional |
   | `--threshold-grid` | float+ | :x: | multiple threshold values can be provided as inputs and the one that produces best F1 score will be selected as best model. | optional |
   | `--verbose` | boolean flag | `False`| this argument allows to print extra information for evaluation or training phase | optional


- **`cli.detect`**: This small workflow command allows one to detect anomaly in a log. Can be called using `python -m cli.detect` followed by the arguments.

    |  argument  |  value type  |  default value |description |  optional/required? |
   | --------- | ------------ | ---------------------------- | ------------ |  ------------|
   | `--model` |  <details><summary>choice</summary><ul><li>logreg</li><li>isolation</li></ul></details> | :x: | pick your choice of ML model to detect anomaly | reqruired |
   | `--model-path` | string | :x: | path to where the serialized model is | required |
   | `--input-file` | string | :x: | path to the log file to perform detection on. If this flag is missing along with `--log-line` flag we will get error. | optional |
   | `--log-line` | "string" | :x: | single input log line within double quotes for detection | optional |
   | `--output-file` | string | :x: | where output from the detection will be saved. if not provided, results will be displayed on the console. beware when using large log files for detection. | optionl |


## Running Django
Currently, you can deploy this django server locally and work with two of the exposed APIs on the frontend. Steps are given below.

- Navigate to the webapp folder from project root folder `cd webapp`
- Migration first! `python -m manage migrate`. This will set some necessary things up.
- Now you can run the server. `python -m manage runserver`. You will get the URI to view the webpage to use the APIs in the command line itself.


# Contributors
- [Kartikay kaul](https://github.com/KartikayKaul)
- [Harsh Padiyar](https://github.com/H4rryC0d3)