from datetime import datetime
import json
from .param_classes import NoDuplicateDict, recursive_objectify, update_recursive
from .dynamic import recursive_dynamic_json
import collections.abc

try:
    import tomllib
except ImportError:
    # tomllib was added in Python 3.11.  Older versions can use tomli
    import tomli as tomllib
import yaml

from .utils import removesuffix

IMPORT_KEY = "__import__"


def load_raw_dict_from_file(filename):
    """Safe load of a json/yaml/toml file (doubled entries raise exception)."""
    if filename.endswith(".json"):
        with open(filename, "r") as f:
            data = json.load(f, object_pairs_hook=NoDuplicateDict)
    elif filename.endswith(".yaml") or filename.endswith(".yml"):
        with open(filename, "r") as f:
            data = yaml.safe_load(f)
    elif filename.endswith(".toml"):
        with open(filename, "rb") as f:
            data = tomllib.load(f)
    else:
        raise RuntimeError("Unsupported file type.")

    return data


def load(
    filename,
    dynamic=True,
    make_immutable=True,
    recursive_imports=True,
    pre_unpack_hooks=None,
    post_unpack_hooks=None,
):
    """Read from a bytestream and deserialize to a settings object"""
    pre_unpack_hooks = pre_unpack_hooks or []
    post_unpack_hooks = post_unpack_hooks or []
    orig_json = load_raw_dict_from_file(filename)

    for hook in pre_unpack_hooks:
        hook(orig_json)

    if recursive_imports:
        unpack_imports_full(
            orig_json, import_string=IMPORT_KEY, used_filenames=[filename]
        )
    return _post_load(orig_json, dynamic, make_immutable, post_unpack_hooks)


def loads(
    s,
    *,
    dynamic=True,
    make_immutable=False,
    recursive_imports=True,
    pre_unpack_hooks=None,
    post_unpack_hooks=None,
):
    """Deserialize string to a settings object"""
    pre_unpack_hooks = pre_unpack_hooks or []
    post_unpack_hooks = post_unpack_hooks or []

    try:
        orig_dict = json.loads(s, object_pairs_hook=NoDuplicateDict)
    except json.JSONDecodeError as e_json:
        try:
            orig_dict = yaml.safe_load(s)
        except yaml.YAMLError as e_yaml:
            raise SyntaxError(f"JSON and YAML parsing failed: {e_json}, {e_yaml}")

    for hook in pre_unpack_hooks:
        hook(orig_dict)

    if recursive_imports:
        unpack_imports_full(orig_dict, import_string=IMPORT_KEY, used_filenames=[])
    return _post_load(orig_dict, dynamic, make_immutable, post_unpack_hooks)


def _post_load(current_dict, dynamic, make_immutable, post_unpack_hooks):
    keys = list(
        current_dict.keys()
    )  # to avoid that list of keys gets updated during loop
    for key in keys:
        if key.endswith("*") and isinstance(
            current_dict[key], collections.abc.Sequence
        ):
            raw_key = removesuffix(key, "*")
            current_dict[raw_key] = current_dict.pop(key)

    if dynamic:
        objectified = recursive_objectify(current_dict, make_immutable=False)
        timestamp = datetime.now().strftime("%H:%M:%S-%d%h%y")
        namespace = dict(__timestamp__=timestamp, **objectified)
        recursive_dynamic_json(current_dict, namespace)

    for hook in post_unpack_hooks:
        hook(current_dict)

    return recursive_objectify(current_dict, make_immutable=make_immutable)


def dfs_on_dicts(orig_dict):
    for key, value in orig_dict.items():
        if isinstance(value, collections.abc.Mapping):
            yield from dfs_on_dicts(value)
    yield orig_dict


def unpack_imports_full(orig_dict, import_string, used_filenames):
    for current_dict in dfs_on_dicts(orig_dict):
        unpack_imports_fixed_level(current_dict, import_string, used_filenames)


def unpack_imports_fixed_level(orig_dict, import_string, used_filenames):
    """
    If new_files is a list with len(new_files) > 1, items later in the list take
    precedence over files earlier in the list, i.e. keys specified in files later
    in the list override keys specified in files earlier in the list. Keys specified
    in the file that imports the other files have the highest priority and override
    everything else.
    """

    if import_string in orig_dict:
        new_files = orig_dict[
            import_string
        ]  # type(orig_dict[import_string]) in [str, list]
        if isinstance(new_files, str):
            new_files = [new_files]
        del orig_dict[import_string]
        for new_file in reversed(new_files):
            if new_file in used_filenames:
                raise ValueError(
                    f"Cyclic dependency of JSONs, {new_file} already unpacked"
                )
            loaded_dict = load_raw_dict_from_file(new_file)
            unpack_imports_full(loaded_dict, import_string, used_filenames + [new_file])
            update_recursive(orig_dict, loaded_dict, overwrite=False)


if __name__ == "__main__":
    import sys

    def check_import_in_fixed_params(setting_dict):
        if "fixed_params" in setting_dict:
            if "__import__" in setting_dict["fixed_params"]:
                raise ImportError(
                    "Cannot import inside fixed params. Did you mean __import_promise__?"
                )

    params = load(sys.argv[1], pre_unpack_hooks=[check_import_in_fixed_params])
    print(params)
