from copasi_model import yaml2model
from util import setup_logger
from to_python import to_python
from time_course import simulate_and_store_results
from yaml import safe_load
import os

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="YAML configuration file")
    parser.add_argument("--output", "-o", help="file to write to")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--to-python", "-p", help="create Python executable for dynamic analysis", action="store_true")
    group.add_argument("--to-copasi", "-c", help="create COPASI-readable file", action="store_true")
    group.add_argument("--simulate", "-t", help="run COPASI time course and create resulting csv file", action="store_true")
    parser.add_argument("--duration", "-d", type=int, help="Number of seconds to run this simulation")
    parser.add_argument("--steps", "-s", type=int, help="Number of steps to run this simulation", default=100)
    parser.add_argument("--verbose", "-v", action="count", default=0, help="Amount of debugging information")

    args = parser.parse_args()
    logger = setup_logger(args)

    logger.info(f"Reading from {args.input}")
    with open(args.input) as f:
        data = safe_load(f.read())

    if args.to_python:
        output = to_python(data)
        default_outfile = os.path.splitext(os.path.basename(args.input))[0] + ".py"
    elif args.to_copasi:
        model = yaml2model(data, logger)
        logger.info(f"Model has {len(model.species_list)} species")
        logger.info(f"Model has {len(model.reactions)} reactions")
        template_path = os.path.dirname(__file__)
        output = model.dump_s(template_path=template_path)
        default_outfile = os.path.splitext(os.path.basename(args.input))[0] + ".cps"
    else:  # elif args.simulate:
        args.output="result.csv" if args.output is None else args.output
        simulate_and_store_results(args, logger)
        exit()

    outfile = args.output if args.output is not None else default_outfile

    logger.info(f"Writing to {outfile}")
    with open(outfile, "wb") as f:
        f.write(output.encode("utf-8"))
