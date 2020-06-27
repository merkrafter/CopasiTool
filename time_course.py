# -*- coding: utf-8 -*-
# Copyright (C) 2017 - 2018 by Pedro Mendes, Virginia Tech Intellectual 
# Properties, Inc., University of Heidelberg, and University of 
# of Connecticut School of Medicine. 
# All rights reserved. 

# Copyright (C) 2010 - 2016 by Pedro Mendes, Virginia Tech Intellectual 
# Properties, Inc., University of Heidelberg, and The University 
# of Manchester. 
# All rights reserved. 

# Copyright (C) 2009 by Pedro Mendes, Virginia Tech Intellectual 
# Properties, Inc., EML Research, gGmbH, University of Heidelberg, 
# and The University of Manchester. 
# All rights reserved. 

from COPASI import *
from util import setup_logger

dataModel = CRootContainer.addDatamodel()


def simulate_and_store_results(args, logger):

  try:
      if not dataModel.loadModel(args.input):
          logger.critical("Couldn't load {0}:".format(args.input))
          logger.critical(CCopasiMessage.getAllMessageText())
  except:
      logger.critical("Error while importing the model from file named \"" + args.input + "\".\n")
      return 1

  model = dataModel.getModel()
  assert model is not None

  trajectoryTask = dataModel.getTask("Time-Course")

  trajectoryTask.setMethodType(CTaskEnum.Method_deterministic)

  # activate the task so that it will be run when the model is saved
  # and passed to CopasiSE
  trajectoryTask.setScheduled(True)

  report = create_report(model)
  trajectoryTask.getReport().setReportDefinition(report)
  trajectoryTask.getReport().setTarget(args.output)
  # don't append output if the file exists, but overwrite the file
  trajectoryTask.getReport().setAppend(False)

  problem = trajectoryTask.getProblem()
  assert (isinstance(problem, CTrajectoryProblem))

  if args.steps > 1:
      problem.setStepNumber(args.steps-1)
      problem.setAutomaticStepSize(False)
  else:
      problem.setAutomaticStepSize(True)
  dataModel.getModel().setInitialTime(0.0)
  problem.setDuration(args.duration)
  # tell the problem to actually generate time series data
  problem.setTimeSeriesRequested(True)
  problem.setOutputEvent(False)

  # set some parameters for the LSODA method through the method
  method = trajectoryTask.getMethod()

  parameter = method.getParameter("Absolute Tolerance")
  assert parameter is not None
  assert parameter.getType() == CCopasiParameter.Type_UDOUBLE
  parameter.setValue(1.0e-12)

  try:
      result=trajectoryTask.process(True)
  except:
      logger.critical("Error. Running the time course simulation failed.\n")
      if CCopasiMessage.size() > 0:
          logger.critical(CCopasiMessage.getAllMessageText(True))
      return 1
  if not result:
      logger.critical("Error. Running the time course simulation failed.\n" )
      if CCopasiMessage.size() > 0:
          logger.critical(CCopasiMessage.getAllMessageText(True))
      return 1

  log_results(trajectoryTask, logger)


def log_results(trajectoryTask, logger):
    timeSeries = trajectoryTask.getTimeSeries()
    logger.info("Ran {0} steps.".format(timeSeries.getRecordedSteps()))
    logger.info("Final state:")
    last_step = timeSeries.getRecordedSteps() - 1
    for i in range(timeSeries.getNumVariables()):
        logger.info("{0}:\t{1}".format(timeSeries.getTitle(i), timeSeries.getConcentrationData(last_step, i)))


def create_report(model):
    reports = dataModel.getReportDefinitionList()
    report = reports.createReportDefinition("Report", "Output for timecourse")
    report.setTaskType(CTaskEnum.Task_timeCourse)
    report.setIsTable(False)
    report.setSeparator(CCopasiReportSeparator(","))
    header = report.getHeaderAddr()
    body = report.getBodyAddr()
    body.push_back(
        CRegisteredCommonName(CCommonName(dataModel.getModel().getCN().getString() + ",Reference=Time").getString()))
    body.push_back(CRegisteredCommonName(report.getSeparator().getCN().getString()))
    header.push_back(CRegisteredCommonName(CDataString("time").getCN().getString()))
    header.push_back(CRegisteredCommonName(report.getSeparator().getCN().getString()))
    iMax = model.getMetabolites().size()
    for i, metab in enumerate(model.getMetabolites()):
        if metab.getStatus() != CModelEntity.Status_FIXED:
            body.push_back(
                CRegisteredCommonName(metab.getObject(CCommonName("Reference=Concentration")).getCN().getString()))
            header.push_back(CRegisteredCommonName(CDataString(metab.getObjectDisplayName()).getCN().getString()))
            # after each entry, we need a separator
            if i != iMax - 1:
                body.push_back(CRegisteredCommonName(report.getSeparator().getCN().getString()))
                header.push_back(CRegisteredCommonName(report.getSeparator().getCN().getString()))
    return report


if __name__ == '__main__':
   import argparse
   parser = argparse.ArgumentParser()
   parser.add_argument("input", help=".cps file defining a model")
   parser.add_argument("--duration", "-d", type=int, help="Number of seconds to run this simulation", default=200)
   parser.add_argument("--steps", "-s", type=int, help="Number of steps to run this simulation", default=100)
   parser.add_argument("--output", "-o", help="Resulting csv file", default="result.csv")
   parser.add_argument("--verbose", "-v", action="count", default=0, help="Amount of debugging information")

   args = parser.parse_args()
   logger = setup_logger(args)
   simulate_and_store_results(args, logger)
