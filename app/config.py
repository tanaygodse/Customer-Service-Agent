import json
import os


def load_config():
    # Get the path to this config.py file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")

    with open(config_path, "r") as f:
        return json.load(f)


config = load_config()
