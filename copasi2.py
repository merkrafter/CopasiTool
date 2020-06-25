from yaml import safe_load
import re

def _unary_op(result_name, func_name, arg_name):
    """
    Generates a function call to func_name with argument arg_name
    storing the result in result_name.
    """
    return f"{result_name} = {func_name}({arg_name})"

def _binary_op(result_name, func_name, arg1_name, arg2_name):
    """
    Generates a binary operator indicated by func_name in infix notation
    with arguments arg1_name and arg2_name storing the result in result_name.
    Supported func_names are add, sub, mul, and div.
    """
    funcs = {'add':'+', 'sub':'-', 'mul':'*', 'div':'/'}
    return f"{result_name} = {arg1_name} {funcs[func_name]} {arg2_name}"

def func2string(result_name, op_name, args):
    """
    Generates an expression that takes args and stores the result in result_name.
    """
    n_args = len(args)
    if n_args == 1:
        return _unary_op(result_name, op_name.lower(), args[0])
    elif n_args == 2:
        return _binary_op(result_name, op_name.lower(), args[0], args[1])

FUNC_NAME = "copasi_model"

def yaml2py_function(data):
    """
    Generates a python function from a data dict that was created from a
    COPASI yaml declaration.
    """
    params = ", ".join([f"{s['name']}={s['initial_concentration']}" for s in data["input"]])
    declaration = f"def {FUNC_NAME}({params}):\n"

    code = ""
    ws = re.compile(r"\s+")
    for function in data["functions"]:
        result_name, _, function_name, *args = ws.split(function)
        code += "  {}\n".format(func2string(result_name, function_name, args))

    return_statement = "  return locals()"

    return declaration + code + return_statement

def get_py_main():
    """
    Generates a main part of python code that calls the generated (from yaml)
    function and prints all variables.
    It also issues a warning if any of the variables has a negative value as
    this causes unpredictable behaviour in COPASI.
    """
    return \
f"""
if __name__ == "__main__":
  variables = {FUNC_NAME}()
  negative_vars = [variable for variable, value in variables.items() if value < 0]
  if negative_vars:
    logging.warning("Some variables seem to produce negative values which is problematic in COPASI.")
  for variable in sorted(variables.keys()):
    print(variable, ":\\t", variables[variable])
"""

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="YAML configuration file")
    parser.add_argument("output", help="Python executable that emulates the COPASI functions")

    args = parser.parse_args()

    pyimports = ""
    pyimports += "from math import sqrt\n"
    pyimports += "import logging\n"

    with open(args.input, "r") as f:
        pyfunc = yaml2py_function(safe_load(f))

    pymain = get_py_main()
    pycode = "\n".join([pyimports, pyfunc, pymain])

    with open(args.output, "w") as f:
        f.write(pycode)
