import ROOT
import sys
import numpy as np
from classes.keyPlotter import keyPlotter

ROOT.gStyle.SetOptFit(1111)
ROOT.gStyle.SetOptStat(1000000001)
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kFatal;")

iName =                     ## json file to read
iFile = open(iName, 'r')    ## open the input file
oName =                     ## root file to write

xArrayVar = np.array([3076, 5370, 6742, 7667, 9396, 10440]) ## variable of the x coordiante for Var

plotter = keyPlotter(   iFile = iFile,
                        oName = oName,
) ## init the plotter with input and output ifles

plotter.SetOptions( useXerror = False)      ## set plotter options
plotter.SetAttributes( separator2D = '_')   ## set plotter attributes

plotter.AddKey( keyName = 'iLumi'  , is2D = False, xArray = xArrayLumiBF) ## add key to plot

plotter.Plot()  ## run the code
