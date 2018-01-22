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


## B+ arrays
xArrayLumiBF = np.array([3076, 5370, 6742, 7667, 9396, 10440])
xArrayLumiGH = np.array([3587, 5476, 6733, 7901, 9473, 10750])
xArrayLumiAl = np.array([4670, 6657, 8623, 10580])

xArrayEtaBF = np.array([0.2115, 0.6140, 0.9983, 1.349, 1.853])
xArrayEtaGH = np.array([0.2135, 0.6151, 1.0010, 1.375, 1.862])

xArrayEtaAll= np.array([0.2111, 0.6137, 0.9983, 1.352, 1.855])

plotter = keyPlotter(   iFile = iFile,
                        oName = oName,
)

plotter.SetOptions( useXerror = True)
plotter.SetAttributes( separator2D = '_')

#plotter.AddKey( keyName = 'pt'  , is2D = False)
plotter.AddKey( keyName = 'bp_eta' , is2D = False)
#plotter.AddKey( keyName = 'pt_eta', is2D = True)
#plotter.AddKey( keyName = 'ds_pt__VS__ds_eta', is2D = True)
#plotter.AddKey( keyName = 'iLumi'  , is2D = False, xArray = xArrayLumiAl)

plotter.Plot()  