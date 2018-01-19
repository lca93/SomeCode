import ROOT
import json
import math
import numpy as np

from classes.Trg_fitter import TrgFitter 

ROOT.gStyle.SetOptFit(1111)
ROOT.gStyle.SetOptStat(1000000001)
#ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kFatal;")

def integFunc (func, binSize):
    norm  = func.GetParameter(2)
    sigma = func.GetParameter(4)

    errNorm  = func.GetParError(2)
    errSigma = func.GetParError(4)
 
    area = norm * sigma * math.sqrt(2.*math.pi)/binSize
    error= (2.*math.pi) * ( (norm*errSigma)**2 + (sigma*errNorm)**2 ) / (binSize**2)

    return np.array([area, error])

iFile = ROOT.TFile('/afs/cern.ch/work/l/lguzzi/samples/bp_allstat.root')
tree  = iFile.Get('mTree')


## fitter settings
den = '1'
num = 'pass'
oth = 'run < 278810'

mainVar  = 'bMass'
fileName = 'BF_eta'

## pdf's settings
rLo = 5.1
rUp = 5.4
nBins = 28

##pdf's declarations
pdfSignalN = ROOT.TF1('pdfSignalN', 'gaus', rLo, rUp)
pdfBackgdN = ROOT.TF1('pdfBackgdN', 'pol1', rLo, rUp)
pdfSignalD = ROOT.TF1('pdfSignalD', 'gaus', rLo, rUp)
pdfBackgdD = ROOT.TF1('pdfBackgdD', 'pol1', rLo, rUp)

pdfN = ROOT.TF1('NumPDF', 'pdfSignalN+pdfBackgdN', rLo, rUp)
pdfD = ROOT.TF1('DenPDF', 'pdfSignalD+pdfBackgdD', rLo, rUp)

numPars = [ ('a'     , None     , None)             ,
            ('b'     , None     , None)             ,
            ('N'     , 10000    , (0, 100000))      ,
            ('#mu'   , 5.28     , (5.25, 5.30))   ,
            ('#sigma', 0.02     , (0.0001, 0.1 ))   ,
]

denPars = [ ('a'     , None     , None)             ,
            ('b'     , None     , None)             ,
            ('N'     , 10000    , (0, 100000))      ,
            ('#mu'   , 5.28     , (5.25, 5.30))   ,
            ('#sigma', 0.02     , (0.0001, 0.1 ))   ,
]

ptBins  = np.array( [5, 15 , 35, 1000])
#etaBins = np.array( [0, 0.7, 1.5, 2.4])
etaBins = np.array( [0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4])
lumiBins= np.array( [0, 6000, 8000, 10000, 20000])
#lumiBins= np.array( [0, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000,20000])

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

#fitter.AddBinnedVar('bp_pt'             , ptBins            )
fitter.AddBinnedVar('bp_eta'            , etaBins           )
#fitter.AddBinnedVar('iLumi'             , lumiBins          )
#fitter.AddBinnedVar('bp_pt__VS__bp_eta' , (ptBins, etaBins) )

fitter.InitializeParameters( numPars = numPars, denPars = denPars)

fitter.SetOptions(fitAttNo = 2)



fitter.CalculateEfficiency()
