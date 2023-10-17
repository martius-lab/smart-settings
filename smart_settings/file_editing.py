import glob
import json


def get_all_jsons():
    return glob.glob(f"settings/**/*.json", recursive=True)


def change_key_name(setting_file, prefixes, old_name, new_name, conditions=None):
    conditions = conditions or {}

    with open(setting_file) as f:
        try:
            orig_dict = json.load(f)
        except Exception as e:
            print(f"{setting_file}: loading failed with error {e}... skipping")
            return False
    if not check_correct_conditions(orig_dict, conditions):
        print(f"{setting_file}: Conditions {conditions} not met ... skipping")
        return False
    as_dict = orig_dict
    try:
        for dict_key in prefixes:
            as_dict = as_dict[dict_key]
    except KeyError:
        print(f"{setting_file}: Not all prefixes {prefixes} present ... skipping")
        return False  # Prefixes not present in JSON file

    if old_name in as_dict:
        old_val = as_dict[old_name]
        as_dict[new_name] = old_val
        print(
            f"{setting_file}: Key {'.'.join(prefixes+[old_name])} renamed to {'.'.join(prefixes+[new_name])}"
        )
        del as_dict[old_name]
        with open(setting_file, "w") as f:
            json.dump(orig_dict, f, indent=4)
        return True

    return False


def check_correct_conditions(dct, conditions):
    for lhs, rhs in conditions.items():
        if not rhs == dct.get(
            lhs, float("nan")
        ):  # using that 'nan' is not equal to ANYTHING in Python
            return False
    return True


def add_key(
    setting_file, prefixes, new_key, default_value, override=False, conditions=None
):
    conditions = conditions or {}

    with open(setting_file) as f:
        try:
            orig_dict = json.load(f)
        except Exception as e:
            print(f"{setting_file}: loading failed with error {e}... skipping")
            return False
    if not check_correct_conditions(orig_dict, conditions):
        print(f"{setting_file}: Conditions {conditions} not met ... skipping")
        return False
    as_dict = orig_dict
    try:
        for dict_key in prefixes:
            as_dict = as_dict[dict_key]
    except KeyError:
        print(f"{setting_file}: Not all prefixes {prefixes} present ... skipping")
        return False  # Prefixes not present in JSON file

    if new_key in as_dict:
        if override:
            print(
                f"{setting_file}: Overwrote {'.'.join(prefixes+[new_key])}={default_value} (from {as_dict[new_key]})"
            )
            as_dict[new_key] = default_value
        else:
            print(f"{setting_file}: Key {new_key} already present, not overwriting...")
            return False
    else:
        as_dict[new_key] = default_value
        print(f"{setting_file}: added {'.'.join(prefixes+[new_key])}={default_value}")

    with open(setting_file, "w") as f:
        json.dump(orig_dict, f, indent=4)
    return True
