import ROOT
import json
import math
import numpy as np

from classes.Tgr_fitter import TrgFitter 

ROOT.gStyle.SetOptFit(1111)
ROOT.gStyle.SetOptStat(1000000001)
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kFatal;")

def integFunc (func, binSize):
    norm  = func.GetParameter(0)
    sigma = func.GetParameter(2)

    errNorm  = func.GetParError(0)
    errSigma = func.GetParError(2)
 
    area = norm * sigma * math.sqrt(2.*math.pi)/binSize
    error= (2.*math.pi) * ( (norm*errSigma)**2 + (sigma*errNorm)**2 ) / (binSize**2)

    return np.array([area, error])

iFile = ROOT.TFile('/afs/cern.ch/work/l/lguzzi/samples/bp_allstat.root')
tree  = iFile.Get('mTree')


## fitter settings
den = '1'
num = 'pass'
oth = 'run > 278810'

mainVar  = 'bMass'
fileName = 'tempFile'

## pdf's settings
rLo = 5.1
rUp = 5.4
nBins = 28

##pdf's declarations
pdfSignalN = ROOT.TF1('pdfSignalN', 'gaus', rLo, rUp)
pdfBackgdN = ROOT.TF1('pdfBackgdN', 'pol2', rLo, rUp)
pdfSignalD = ROOT.TF1('pdfSignalD', 'gaus', rLo, rUp)
pdfBackgdD = ROOT.TF1('pdfBackgdD', 'pol2', rLo, rUp)

pdfN = ROOT.TF1('NumPDF', 'pdfSignalN+pdfBackgdN', rLo, rUp)
pdfD = ROOT.TF1('DenPDF', 'pdfSignalD+pdfBackgdD', rLo, rUp)

numParNames = ('a' , 'b' , 'c' , 'N'          , '#mu'         , '#sigma')
numInitVals = (None, None, None, 10000        , 5.27          , 0.02          )
numParLims  = (None, None, (0, 10000), (0, 100000)  , (5.270, 5.290), (0.0001, 0.05))

denParNames = ('a' , 'b' , 'c' , 'N'          , '#mu'         , '#sigma')
denInitVals = (None, None, None, 10000        , 5.27          , 0.02)
denParLims  = (None, None, (0, 10000), (0, 100000)  , (5.270, 5.290), (0.0001, 0.05))

ptBins  = np.array( [5, 15 , 35, 1000])
etaBins = np.array( [0, 0.7, 1.5, 2.4])
lumiBins= np.array( [0, 6000, 8000, 10000, 20000])

fitter = TrgFitter( pdfNum   =  pdfN    , 
                    pdfDen   =  pdfD    , 
                    tree     =  tree    , 
                    mainVar  =  mainVar , 
                    den      =  den     , 
                    num      =  num     , 
                    oth      =  oth     ,  
                    rLo      =  rLo     ,
                    rUp      =  rUp     ,
                    nBins    =  nBins   ,
                    fileName =  fileName
        )

fitter.SetIntegratingFunction(integFunc)

fitter.AddBinnedVar('bp_pt'             , ptBins            )
fitter.AddBinnedVar('bp_eta'            , etaBins           )
fitter.AddBinnedVar('iLumi'             , lumiBins          )
fitter.AddBinnedVar('bp_pt__VS__bp_eta' , (ptBins, etaBins) )

fitter.SetParNames( numParNames = numParNames,
                    denParNames = denParNames
)
fitter.SetParInitVals( numInitVals = numInitVals,
                       denInitVals = denInitVals
)
fitter.SetParLimits( numParLims = numParLims,
                     denParLims = denParLims
)

fitter.SetOptions(pdbFit = False)



fitter.CalculateEfficiency()


