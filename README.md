# General description
CopasiTool provides scripts that help bootstrap and verify COPASI models.
It was developed during another project that involved working with COPASI when it became apparent that finding errors in the reactions and/or species configuration or making adaptions in a later stage would be highly prone to errors if one was only using the COPASI GUI.

Specifically, CopasiTool supports fulfilling the following task: **Given a mathematical formula that consists of the four basic arithmetic operations and square roots** (note that this allows Taylor approximation of general functions)**, create a biochemical network description that can be read by and simulated with COPASI.**

# Setup
In order to run these scripts you need Python3 installed and also install the dependencies via
```bash
pip install -r requirements.txt
```
In addition (if not already happened) you probably want to install COPASI from their [project page](https://github.com/copasi/COPASI).

# How to use
The format that CopasiTool expects the formula to be in is SSA form operations.
In short, any variable may only be written to once.
CopasiTool converts this SSA form in a YAML file to a COPASI-compatible .cps file.
If this sounds confusing, you may want to start with a simple [example](examples/average.yaml).
```bash
# create a Python script to test the defined model
$ python CopasiTool.py examples/average.yaml --to-python
$ python average.py # this is the default outfile name pattern
  TWO : 2
  a :   6
  avg : 3
  b :   0
  sum : 6
# everything alright; let's create the COPASI file
$ python CopasiTool.py examples/average.yaml --to-copasi
  # creates average.cps that can be simulated with COPASI
$ python CopasiTool.py --simulate average.cps
  # creates result.csv that contains the values for all species for each time step
$ head result.csv -n2; tail result.csv -n2
time,null,a,b,TWO,sum,avg
0,0,6,0,2,0,0
98.9899,53.3942,6,0,2,5.9997,2.9997
100,54.0003,6,0,2,5.99973,2.99973
```

The file format for YAML file associated with CopasiTool is as follows:

```yaml
name: Name of the project
duration: 100  # seconds to run this model; mandatory
input:  # List of species (roughly equivalent to constant values in programming languages)
 - name: a  # Name of the species; mandatory
   initial_concentration: 4  # initial value; defaults to 0
functions:  # A list of prefix notated, ssa form-like instruction. So far, only ADD, SUB, MUL, DIV, and SQRT are supported.
 # format:
 # prefix notation
 - a2 = MUL a a
#- a2 = ADD a2 a2  # forbidden; only static single-assignment instructions allowed
 - x = SUB a2 a  # note that SUB is only well-defined if the first argument is greater than or equal to the second

plots:  # List of plots that show species concentrations plotted against time
  - name: Main plot  # title of the plot
    species: [a, a2, x] # list of species to plot; each species will be one graph
```

# License
This project is licensed under the [MIT license](LICENSE).
From it, the "no warranty" part is especially important, as this project does not guarantee any correctness whatsoever.
It was created as a quick-and-dirty solution to a problem during an own project, not as a library or sophisticated program, and it will most likely be archived as soon as the aforementioned project is over.
