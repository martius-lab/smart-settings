from datetime import datetime
import json
from .param_classes import NoDuplicateDict, recursive_objectify, update_recursive
from .dynamic import recursive_dynamic_json
import collections.abc

IMPORT_KEY = '!import'


def load_raw_json_from_file(filename):
    """ Safe load of a json file (doubled entries raise exception)"""
    with open(filename, 'r') as f:
        data = json.load(f, object_pairs_hook=NoDuplicateDict)
    return data


def load(filename, dynamic=True, make_immutable=True, recursive_imports=True,
         suppress_invalid_identifier_exception=False):
    """ Read from a bytestream and deserialize to a settings object"""
    orig_json = load_raw_json_from_file(filename)
    if recursive_imports:
        unpack_imports_full(
            orig_json,
            import_string=IMPORT_KEY,
            used_filenames=[filename])
    return _post_load(orig_json, dynamic, make_immutable,
                      suppress_invalid_identifier_exception)


def loads(s, *, dynamic=True, make_immutable=False, recursive_imports=True,
          suppress_invalid_identifier_exception=False):
    """ Deserialize string to a settings object"""
    orig_json = json.loads(s, object_pairs_hook=NoDuplicateDict)
    if recursive_imports:
        unpack_imports_full(
            orig_json,
            import_string=IMPORT_KEY,
            used_filenames=[])
    return _post_load(orig_json, dynamic, make_immutable,
                      suppress_invalid_identifier_exception)


def _post_load(current_dict, dynamic, make_immutable,
               suppress_invalid_identifier_exception):
    if dynamic:
        objectified = recursive_objectify(current_dict, make_immutable=False)
        timestamp = datetime.now().strftime('%H:%M:%S-%d%h%y')
        namespace = dict(__timestamp__=timestamp, **objectified)
        recursive_dynamic_json(current_dict, namespace)

    return recursive_objectify(current_dict,
                               make_immutable=make_immutable,
                               suppress_invalid_identifier_exception=suppress_invalid_identifier_exception)


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
    params = load(sys.argv[1])
    print(params)
