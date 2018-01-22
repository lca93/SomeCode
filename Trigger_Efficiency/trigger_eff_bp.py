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

def bUpFunc (pdf, bpdf):
    bpdf.SetParameter(0, pdf.GetParameter(0))
    bpdf.SetParameter(1, pdf.GetParameter(1))

iFile = ROOT.TFile('/afs/cern.ch/work/l/lguzzi/samples/bp_allstat.root')
tree  = iFile.Get('mTree')


## fitter settings
den = '1'
num = 'pass'
oth = 'run < 278810'

mainVar  = 'bMass'
fileName = 'test_b'

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
            ('#sigma', 0.02     , (0.005, 0.1 ))   ,
]

denPars = [ ('a'     , None     , None)             ,
            ('b'     , None     , None)             ,
            ('N'     , 10000    , (0, 100000))      ,
            ('#mu'   , 5.28     , (5.25, 5.30))     ,
            ('#sigma', 0.02     , (0.005, 0.1 ))   ,
]

ptBins  = np.array( [5, 15 , 35, 1000])
etaBins = np.array( [0, 0.7, 1.5, 2.4])
lumiBins= np.array( [0, 6000, 8000, 10000, 20000])

etaBinsBF = np.array([0, 0.4, 0.8, 1.2, 1.6, 2.4])
etaBinsGH = np.array([0, 0.4, 0.8, 1.2, 1.6, 2.4])
lumiBinsGH= np.array( [0, 4000, 6500, 7000, 9000, 10000, 20000])
lumiBinsBF= np.array( [0, 4000, 6500, 7000, 9000, 10000, 20000])

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

fitter.AddBinnedVar('bp_pt'             , ptBins            )
#fitter.AddBinnedVar('bp_eta'            , etaBinsGH           )
#fitter.AddBinnedVar('iLumi'             , lumiBinsGH         )
#fitter.AddBinnedVar('bp_pt__VS__bp_eta' , (ptBins, etaBins) )


## fitter setup
fitter.InitializeParameters( numPars = numPars, denPars = denPars)
fitter.SetBackgroundPdf( bpdfNum = pdfBackgdN, bpdfDen = pdfBackgdD)
fitter.SetBackgroundUpdateFunction( func = bUpFunc)
fitter.SetIntegratingFunction(func = integFunc)

fitter.SetOptions(fitAttNo = 2)



fitter.CalculateEfficiency()
