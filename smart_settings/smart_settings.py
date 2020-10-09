from datetime import datetime
import json
from .param_classes import NoDuplicateDict, recursive_objectify, update_recursive
from .dynamic import recursive_dynamic_json
import collections.abc

IMPORT_KEY = '__import__'


def load_raw_json_from_file(filename):
    """ Safe load of a json file (doubled entries raise exception)"""
    with open(filename, 'r') as f:
        data = json.load(f, object_pairs_hook=NoDuplicateDict)
    return data


def load(filename, dynamic=True, make_immutable=True, recursive_imports=True,
         pre_unpack_hooks=None, post_unpack_hooks=None):
    """ Read from a bytestream and deserialize to a settings object"""
    pre_unpack_hooks = pre_unpack_hooks or []
    post_unpack_hooks = post_unpack_hooks or []
    orig_json = load_raw_json_from_file(filename)

    for hook in pre_unpack_hooks:
        hook(orig_json)

    if recursive_imports:
        unpack_imports_full(
            orig_json,
            import_string=IMPORT_KEY,
            used_filenames=[filename])
    return _post_load(orig_json, dynamic, make_immutable,
                      post_unpack_hooks)


def loads(s, *, dynamic=True, make_immutable=False, recursive_imports=True,
          pre_unpack_hooks=None, post_unpack_hooks=None):
    """ Deserialize string to a settings object"""
    pre_unpack_hooks = pre_unpack_hooks or []
    post_unpack_hooks = post_unpack_hooks or []

    orig_json = json.loads(s, object_pairs_hook=NoDuplicateDict)

    for hook in pre_unpack_hooks:
        hook(orig_json)

    if recursive_imports:
        unpack_imports_full(
            orig_json,
            import_string=IMPORT_KEY,
            used_filenames=[])
    return _post_load(orig_json, dynamic, make_immutable, post_unpack_hooks)


def _post_load(current_dict, dynamic, make_immutable, post_unpack_hooks):
    if dynamic:
        objectified = recursive_objectify(current_dict, make_immutable=False)
        timestamp = datetime.now().strftime('%H:%M:%S-%d%h%y')
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
    if import_string in orig_dict:
        new_file = orig_dict[import_string]
        del orig_dict[import_string]
        if new_file in used_filenames:
            raise ValueError(
                f"Cyclic dependency of JSONs, {new_file} already unpacked")
        loaded_dict = load_raw_json_from_file(new_file)
        unpack_imports_full(
            loaded_dict,
            import_string,
            used_filenames +
            [new_file])
        update_recursive(orig_dict, loaded_dict, overwrite=False)


if __name__ == '__main__':
    import sys

    def check_import_in_fixed_params(setting_dict):
        if "fixed_params" in setting_dict:
            if "__import__" in setting_dict['fixed_params']:
                raise ImportError("Cannot import inside fixed params. Did you mean __import_promise__?")
    params = load(sys.argv[1], pre_unpack_hooks=[check_import_in_fixed_params])
    print(params)
