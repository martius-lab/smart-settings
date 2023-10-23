import os
import collections


def _replace_inside_brackets(string, replace_from, replace_to):
    index = string.find("{")
    if index == -1:
        yield string
        return
    yield string[: index + 1]
    new_index = string[index + 1 :].find("}")
    if new_index == -1:
        yield from string[index:]
        return
    new_index += index + 1
    yield string[index + 1 : new_index].replace(replace_from, replace_to)
    yield from _replace_inside_brackets(string[new_index:], replace_from, replace_to)


def replace_inside_brackets(string, replace_from, replace_to):
    return "".join(list(_replace_inside_brackets(string, replace_from, replace_to)))


def fstring_in_json(format_string, namespace):
    if not isinstance(format_string, str):
        return format_string

    replaced_dollar_signs = replace_inside_brackets(format_string, "$", "ENV_")
    env_dict = {"ENV_" + key: value for key, value in os.environ.items()}
    try:
        formatted = eval('f"' + replaced_dollar_signs + '"', {**env_dict, **namespace})
    except BaseException as e:
        return format_string

    if formatted == format_string:
        return format_string

    try:
        return eval(formatted, dict(__builtins__=None))
    except BaseException as e:
        return formatted


def recursive_dynamic_json(nested_dict_or_list, namespace):
    "Evaluates each key in nested dict as an f-string within a given namespace"
    if isinstance(nested_dict_or_list, collections.abc.Mapping):
        for k, v in nested_dict_or_list.items():
            if isinstance(v, collections.abc.Mapping) or isinstance(v, list):
                recursive_dynamic_json(v, namespace)
            else:
                nested_dict_or_list[k] = fstring_in_json(v, namespace)
    elif isinstance(nested_dict_or_list, list):
        for i, item in enumerate(nested_dict_or_list):
            if isinstance(item, collections.abc.Mapping) or isinstance(item, list):
                recursive_dynamic_json(item, namespace)
            else:
                nested_dict_or_list[i] = fstring_in_json(item, namespace)
