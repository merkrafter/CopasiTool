from copasi_model import yaml2model

import logging


def setup_logger(args):
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if args.verbose >= 2:
        logger.setLevel(logging.DEBUG)
    elif args.verbose == 1:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)
    return logger


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
