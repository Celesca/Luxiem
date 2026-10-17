import argparse
import importlib

STAGES = ["collect", "extract", "normalize", "features", "model", "evaluate"]


def main() -> None:
    parser = argparse.ArgumentParser(prog="lexiem")
    parser.add_argument("stage", choices=STAGES)
    parser.add_argument("--config", default="configs/pipeline.yaml")
    parser.add_argument(
        "--from-processed",
        action="store_true",
        help="model stage: use committed data/processed/ instead of rerunning earlier stages",
    )
    args = parser.parse_args()
    stage = importlib.import_module(f"lexiem.{args.stage}")
    stage.run(config_path=args.config, from_processed=args.from_processed)
