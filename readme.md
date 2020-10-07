# Smart JSON

A nifty little wrapper around the standard JSON format. Particularly useful for cluster utils

## Run to install:

``python3 -m pip install git+https://gitlab.tuebingen.mpg.de/mrolinek/smart-json.git``


## Main features


* **Duplicate check**. Duplicate keys are caught and raise an exception.

* **Objectification** The resulting objects support dot access. By default they are immutable (but a mutable copy can be exported).

* **Imports** It allows for importing other JSON files with arbitrary level of nesting and recursion. Imports are carried out from the most nested and NEVER overwrite present values.

* **Dynamic values** Some values may be "computed" dynamically based on other content of the JSON (after all imports are performed). This includes access to environmental variables (present in `os.environ`).

## Examples

See the `examples` folder