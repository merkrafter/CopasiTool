from copasi_model import yaml2model
from util import setup_logger
from to_python import to_python
from yaml import safe_load

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="YAML configuration file")
    parser.add_argument("--output", "-o", help="file to write to")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--to-python", "-p", help="create Python executable for dynamic analysis", action="store_true")
    group.add_argument("--to-copasi", "-s", help="create COPASI-readable file", action="store_true")
    parser.add_argument("--verbose", "-v", action="count", default=0, help="Amount of debugging information")

    args = parser.parse_args()
    logger = setup_logger(args)

    logger.info(f"Reading from {args.input}")
    with open(args.input) as f:
        data = safe_load(f.read())

    if args.to_python:
        output = to_python(data)
    elif args.to_copasi:
        model = yaml2model(data, logger)

        logger.info(f"Model has {len(model.species_list)} species")
        logger.info(f"Model has {len(model.reactions)} reactions")
        output = model.dump_s()

    logger.info(f"Writing to {args.output}")
    with open(args.output, "wb") as f:
        f.write(output.encode("utf-8"))
