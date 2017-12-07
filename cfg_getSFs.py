import numpy as np
import ROOT
import sys


## some variablesS
ptBins     = np.array([2., 2.5, 2.75, 3., 3.25, 3.5, 3.75, 4., 4.5, 5., 6., 8., 10., 15., 20., 30.])
etaBins    = np.array([-2.4, -2.1, -1.6, -1.2, -0.9, -0.3, -0.2, 0.2, 0.3, 0.9, 1.2, 1.6, 2.1, 2.4])
nVtxBins   = np.array([0.5,2.5,4.5,6.5,8.5,10.5,12.5,14.5,16.5,18.5,20.5,22.5,24.5,26.5,28.5,30.5,32.5,34.5,36.5,38.5,40.5,42.5,44.5,46.5,48.5,50.5])
absetaBins = np.array([0, 0.9, 1.2, 2.1, 2.4])

## varuables
varList =[  #("pt"   , ptBins  ),
            #("eta"  , etaBins ),
            #("nVtx" , nVtxBins),
            ("pt_abseta", (ptBins, absetaBins)),
]

##input files
fileDA = ROOT.TFile.Open("../root_files/data/data_%s.root" % str(sys.argv[1]))
fileMC = ROOT.TFile.Open("../root_files/mc/mc_%s.root"     % str(sys.argv[1]))

## main directory
MAINDIR = "./%s" % str(sys.argv[1])

## booleans
    ## separate json and graphs for 2D only to aoid an unknown crash
printGraphs = False
useLogXforPt= True