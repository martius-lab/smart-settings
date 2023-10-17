from .file_editing import change_key_name
import argparse
import glob

parser = argparse.ArgumentParser(
    description="Porting JSON file(s) to Cluster utils >=3.0"
)
parser.add_argument(dest="files", type=str, help="Input file(s)", nargs="+")


if __name__ == "__main__":
    args = parser.parse_args()

    for setting_file in args.files:
        change_key_name(
            setting_file, prefixes=[], old_name="model_dir", new_name="working_dir"
        )
        change_key_name(
            setting_file, prefixes=[], old_name="default_json", new_name="__import__"
        )
        change_key_name(
            setting_file,
            prefixes=["fixed_params"],
            old_name="default_json",
            new_name="__import_promise__",
        )
