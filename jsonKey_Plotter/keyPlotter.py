import ROOT
import sys
import numpy as np
from classes.keyPlotter_c import keyPlotter

ROOT.gStyle.SetOptFit(1111)
ROOT.gStyle.SetOptStat(1000000001)
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kFatal;")

iName = 'results/%s.json' % str(sys.argv[1])
iFile = open(iName, 'r')
oName = '%s_plot' % str(sys.argv[1])

xArrayLumiBF = np.array([2951, 5303, 6706, 7772, 9323, 10390])
xArrayLumiGH = np.array([2972, 5493, 6701, 7879, 9455, 11220])


plotter = keyPlotter(   iFile = iFile,
                        oName = oName,
)

#plotter.AddKey( keyName = 'bp_pt'  , is2D = False)
plotter.AddKey( keyName = 'bp_eta' , is2D = False)
#plotter.AddKey( keyName = 'iLumi'  , is2D = False, xArray = xArrayLumiGH)
#plotter.AddKey( keyName = 'ds_pt__VS__ds_eta', is2D = True)

plotter.Plot()  