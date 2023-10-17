from .file_editing import add_key
import argparse
import glob

parser = argparse.ArgumentParser(description="Adding a key to many JSON files.")
parser.add_argument(dest="files", type=str, help="Input file(s)")
parser.add_argument(dest="key_name", type=str, help="Name of the key to add")
parser.add_argument(dest="default_value", type=str, help="Default value to assign")
parser.add_argument(
    "--override", action="store_true", help="Override value if key present"
)


if __name__ == "__main__":
    args = parser.parse_args()

    matching_files = glob.glob(args.files, recursive=True)
    if not matching_files:
        print(f"No files matching {args.files}")
        exit(2)

    *prefixes, new_key = args.key_name.split(".")
    for setting_file in matching_files:
        add_key(
            setting_file,
            prefixes=prefixes,
            new_key=new_key,
            default_value=eval(args.default_value),
            override=args.override,
            conditions=None,
        )
