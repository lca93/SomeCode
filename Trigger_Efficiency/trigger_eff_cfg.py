import ROOT
import json
import math
import numpy as np

from classes.Trg_fitter import TrgFitter 

ROOT.gStyle.SetOptFit(1111)
ROOT.gStyle.SetOptStat(1000000001)
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kFatal;")

iFile = ROOT.TFile('/afs/cern.ch/work/l/lguzzi/samples/bp_allstat.root')
tree  = iFile.Get('mTree')


## fitter settings
den = ## denominator bool string
num = ## numerator bool string
oth = ## other bool

mainVar  = ## e.g. mass variable name
fileName = ## outfile name

## pdf's settings
fitRangeNum = ## fit range num
fitRangeDen = ## fit range den
nBins = ## bin number

numParB = [ 
            ('Norm'         , 5000      , (0, 10000))   ,
            ('Edge'         , 5.13      , (5.12, 5.2))  ,
            ('Den'          , 0.05      , (0.02, 0.2))  ,
            ('A'            , 10        , (0, 50))      ,
            ('B'            , -1        , (-10, 0))     ,
]
numParS = [
            ('N'     , 10000     , (0, 100000))     ,
            ('#mu'   , 5.28      , (5.22    , 5.30)),
            ('#sigma', 0.02      , (0.01, 0.1 ))    ,
            ('N2'     , 10000    , (0, 100000))     ,
            ('#sigma2', 0.02     , (0.01, 0.1 ))    ,
]
denParB = numParB
denParS = numParS

ptBins  = np.array( [5, 15 , 35, 1000])
etaBins = np.array( [0, 0.4, 0.8, 1.2, 1.6, 2.0,  2.4])
lumiBins= np.array( [0, 6000, 8000, 10000, 20000])

backgroundFitFunctionNUM  = 'expo(0)'
signalFitFunnctionNUM     = 'gaus(0)'

backgroundFitFunctionDEN  = backgroundFitFunctionNUM
signalFitFunnctionDEN     = signalFitFunnctionNUM

fitter = TrgFitter( tree     =  tree    , 
                    mainVar  =  mainVar , 
                    den      =  den     , 
                    num      =  num     , 
                    oth      =  oth     ,   
                    fitRangeNum =  fitRangeNum,
                    fitRangeDen =  fitRangeDen,
                    nBins    =  nBins   ,
                    fileName =  fileName,
)

fitter.SetPDFs( numPDFs = signalFitFunnctionNUM    ,
                numPDFb = backgroundFitFunctionNUM ,
                denPDFs = signalFitFunnctionDEN    ,
                denPDFb = backgroundFitFunctionNUM ,
                numParS = numParS, 
                numParB = numParB, 
                denParS = denParS, 
                denParB = denParB, 
)

fitter.AddBinnedVar('eta'            , etaBins  )
fitter.AddBinnedVar('pt'             , ptBins   )

fitter.SetOptions(
            fitAttNo = 2, 
            pdbFit = False, 
            useGausSignal = False, 
            DrawResidual = True
)

fitter.CalculateEfficiency()
