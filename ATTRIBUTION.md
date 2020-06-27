This project contains work derived from the COPASI sources (in particular, `COPASI/copasi/bindings/python/examples/example3.py`) that was licensed under the Artistic license 2.0.
It was modified the following way:
```bash
$ diff example3.py time_course.py
16a17,18
> from COPASI import *
> from util import setup_logger
17a20
> dataModel = CRootContainer.addDatamodel()
19a23
> def main(args, logger):
21,43d24
< 
< # This is an example on how to import an sbml file
< # create a report for a time course simulation 
< # and run a time course simulation
< # 
< 
< from COPASI import *
< import sys
< 
< # create a datamodel
< try:
<     dataModel = CRootContainer.addDatamodel()
< except:
<     dataModel = CCopasiRootContainer.addDatamodel()
< 
< 
< def main(args):
<   # the only argument to the main routine should be the name of an SBML file
<   if len(args) != 1:
<       sys.stderr.write("Usage: example3 SBMLFILE\n")
<       return 1;
< 
<   filename = args[0]
45,48c26,28
<       # load the model
<       if  not dataModel.importSBML(filename):
<           print("Couldn't load {0}:".format(filename))
<           print(CCopasiMessage.getAllMessageText())
---
>       if not dataModel.loadModel(args.infile):
>           logger.critical("Couldn't load {0}:".format(args.infile))
>           logger.critical(CCopasiMessage.getAllMessageText())
50c30
<       sys.stderr.write("Error while importing the model from file named \"" + filename + "\".\n")
---
>       logger.critical("Error while importing the model from file named \"" + args.infile + "\".\n")
53a34,37
>   for species in model.getMetabolites():
>       if species.getObjectName()=="a":
>           logger.info("Set a=3")
>           species.setInitialValue(3)
56d39
<   # get the trajectory task object
58d40
<   assert (isinstance(trajectoryTask, CTrajectoryTask))
60d41
<   # run a deterministic time course
67d47
<   # create a new report that captures the time course result
69d48
<   # set the report for the task
71,72c50
<   # set the output filename
<   trajectoryTask.getReport().setTarget("example3.txt")
---
>   trajectoryTask.getReport().setTarget(args.outfile)
76d53
<   # get the problem for the task to set some parameters
80,82c57,61
<   # simulate 100 steps
<   problem.setStepNumber(100)
<   # start at time 0
---
>   if args.steps > 1:
>       problem.setStepNumber(args.steps-1)
>       problem.setAutomaticStepSize(False)
>   else:
>       problem.setAutomaticStepSize(True)
84,85c63
<   # simulate a duration of 10 time units
<   problem.setDuration(10)
---
>   problem.setDuration(args.duration)
88,90d65
<   # tell the problem, that we want exactly 100 simulation steps (not automatically controlled)
<   problem.setAutomaticStepSize(False)
<   # tell the problem, that we don't want additional output points for event assignments
102d76
<       # now we run the actual trajectory
105,106c79
<       sys.stderr.write("Error. Running the time course simulation failed.\n")
<       # check if there are additional error messages
---
>       logger.critical("Error. Running the time course simulation failed.\n")
108,109c81
<           # print the messages in chronological order
<           sys.stderr.write(CCopasiMessage.getAllMessageText(True))
---
>           logger.critical(CCopasiMessage.getAllMessageText(True))
112,113c84
<       sys.stderr.write("Error. Running the time course simulation failed.\n" )
<       # check if there are additional error messages
---
>       logger.critical("Error. Running the time course simulation failed.\n" )
115,116c86
<           # print the messages in chronological order
<           sys.stderr.write(CCopasiMessage.getAllMessageText(True))
---
>           logger.critical(CCopasiMessage.getAllMessageText(True))
119,120c89
<   # look at the timeseries
<   print_results(trajectoryTask)
---
>   log_results(trajectoryTask, logger)
123c92
< def print_results(trajectoryTask):
---
> def log_results(trajectoryTask, logger):
125,150c94,98
<     # we simulated 100 steps, including the initial state, this should be
<     # 101 step in the timeseries
<     assert timeSeries.getRecordedSteps() == 101
<     print ("The time series consists of {0} steps.".format(timeSeries.getRecordedSteps()))
<     print ("Each step contains {0} variables.".format(timeSeries.getNumVariables()))
<     print ("\nThe final state is: ")
<     iMax = timeSeries.getNumVariables()
<     lastIndex = timeSeries.getRecordedSteps() - 1
<     for i in range(0, iMax):
<         # here we get the particle number (at least for the species)
<         # the unit of the other variables may not be particle numbers
<         # the concentration data can be acquired with getConcentrationData
<         print ("  {0}: {1}".format(timeSeries.getTitle(i), timeSeries.getData(lastIndex, i)))
<     # the CTimeSeries class now has some new methods to get all variable titles
<     # as a python list (getTitles())
<     # and methods to get the complete time course data for a certain variable based on
<     # the variables index or the corresponding model object.
<     # E.g. to get the particle numbers of the second variable as a python list
<     # you can use getDataForIndex(1) and to get the concentration data you use
<     # getConcentrationDataForIndex(1)
<     # To get the complete particle number data for the second metabolite of the model
<     # you can use getDataForObject(model.getMetabolite(1)) and to get the concentration
<     # data you use getConcentrationDataForObject.
<     # print timeSeries.getTitles()
<     # print timeSeries.getDataForIndex(1)
<     # print timeSeries.getDataForObject(model)
---
>     logger.info("Ran {0} steps.".format(timeSeries.getRecordedSteps()))
>     logger.info("Final state:")
>     last_step = timeSeries.getRecordedSteps() - 1
>     for i in range(timeSeries.getNumVariables()):
>         logger.info("{0}:\t{1}".format(timeSeries.getTitle(i), timeSeries.getConcentrationData(last_step, i)))
154,155d101
<     # create a report with the correct filename and all the species against
<     # time.
157d102
<     # create a report definition object
159d103
<     # set the task type for the report definition to timecourse
161d104
<     # we don't want a table
163,168c106
<     # the entries in the output should be separated by a ", "
<     report.setSeparator(CCopasiReportSeparator(", "))
<     # we need a handle to the header and the body
<     # the header will display the ids of the metabolites and "time" for
<     # the first column
<     # the body will contain the actual timecourse data
---
>     report.setSeparator(CCopasiReportSeparator(","))
177,180c115
<     for i in range(0, iMax):
<         metab = model.getMetabolite(i)
<         assert metab is not None
<         # we don't want output for FIXED metabolites right now
---
>     for i, metab in enumerate(model.getMetabolites()):
182,184d116
<             # we want the concentration oin the output
<             # alternatively, we could use "Reference=Amount" to get the
<             # particle number
187,188c119
<             # add the corresponding id to the header
<             header.push_back(CRegisteredCommonName(CDataString(metab.getSBMLId()).getCN().getString()))
---
>             header.push_back(CRegisteredCommonName(CDataString(metab.getObjectDisplayName()).getCN().getString()))
197,200c128,138
<    main(sys.argv[1:]) 
< 
< 
< 
---
>    import argparse
>    parser = argparse.ArgumentParser()
>    parser.add_argument("infile", help=".cps file defining a model")
>    parser.add_argument("--duration", "-d", type=int, help="Number of seconds to run this simulation", default=200)
>    parser.add_argument("--steps", "-s", type=int, help="Number of steps to run this simulation", default=100)
>    parser.add_argument("--outfile", "-o", help="Resulting csv file", default="result.csv")
>    parser.add_argument("--verbose", "-v", action="count", default=0, help="Amount of debugging information")
> 
>    args = parser.parse_args()
>    logger = setup_logger(args)
>    main(args, logger)
```
