from copasi_model import yaml2model
from util import setup_logger

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="YAML configuration file")
    parser.add_argument("--output", "-o", help="Copasi-readable XML file", default="result.cps")
    parser.add_argument("--verbose", "-v", action="count", default=0, help="Amount of debugging information")

    args = parser.parse_args()
    logger = setup_logger(args)

    logger.info(f"Reading from {args.input}")
    with open(args.input) as f:
        data = f.read()
    model = yaml2model(data, logger)

    logger.info(f"Model has {len(model.species_list)} species")
    logger.info(f"Model has {len(model.reactions)} reactions")

    logger.info(f"Writing to {args.output}")
    model.dump(args.output)
