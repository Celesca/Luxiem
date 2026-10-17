from pathlib import Path

import yaml


def load(path: str | Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)
