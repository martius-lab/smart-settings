# Smart settings

A nifty little wrapper around settings files. Particularly useful for cluster utils

## Run to install:

``python3 -m pip install git+https://gitlab.tuebingen.mpg.de/mrolinek/smart-json.git``


## Main features

* **JSON/YAML support** Both file formats are supported.

* **Duplicate check**. Duplicate keys in JSONs are caught and raise an exception.

* **Objectification** The resulting objects support dot access. By default they are immutable (but a mutable copy can be exported).

* **Imports** It allows for importing other JSON files with arbitrary level of nesting and recursion. Imports are carried out from the most nested and NEVER overwrite present values.

* **Dynamic values** Some values may be "computed" dynamically based on other content of the JSON (after all imports are performed). This includes access to environmental variables (present in `os.environ`).

## API for changing keys in many files

``
python3 -m smart_settings.change_key settings/*.json train_params.opt_params optimizer_params
``

--> Changes `train_params.opt_params` to `train_params.optimizer_params` in every file matching the wildcard

``
python3 -m smart_settings.add_key settings/*.json  train_params.num_epochs 10 --override
``

--> Adds key `train_params.num_epochs` with value `10`. `--override` controls overwriting of present values

``
python3 -m smart_settings.port_cluster_utils_3 settings/**/*.json
``

--> Performs all name changes required for porting to `cluster_utils >=3.0`

## Examples

See the `examples` folder