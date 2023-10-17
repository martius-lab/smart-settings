from .file_editing import change_key_name
import argparse
import glob

parser = argparse.ArgumentParser(description="Changing a key name in JSON file(s).")
parser.add_argument(dest="files", type=str, help="Input file(s)")
parser.add_argument(
    dest="key_name",
    type=str,
    help="Name of the key to change (with '.' syntax for nesting)",
)
parser.add_argument(
    dest="new_name",
    type=str,
    help="New name of the key (only the suffix -- no '.' expected)",
)
parser.add_argument(
    "--override", action="store_true", help="Override value if key present"
)


if __name__ == "__main__":
    args = parser.parse_args()

    matching_files = glob.glob(args.files, recursive=True)
    if not matching_files:
        print(f"No files matching {args.files}")
        exit(2)

    *prefixes, old_key = args.key_name.split(".")
    for setting_file in matching_files:
        change_key_name(
            setting_file,
            prefixes=prefixes,
            old_name=old_key,
            new_name=args.new_name,
            conditions=None,
        )
