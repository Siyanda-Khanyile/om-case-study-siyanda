#!/usr/bin/env python3

from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def list_json_files(directory=SCRIPT_DIR):
  
    directory = Path(directory).resolve()
    return sorted(
        (
            entry
            for entry in directory.iterdir()
            if entry.is_file() and entry.suffix.lower() == ".json"
        ),
        key=lambda entry: entry.name,
    )


if __name__ == "__main__":
    for json_file in list_json_files():
        print(json_file.name)
