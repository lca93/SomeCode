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
den = '1'
num = 'pass'
oth = 'run > -1'

mainVar  = 'bMass'
fileName = 'allStat_eta_data'

## pdf's settings
fitRangeNum = (5.0, 5.6)
fitRangeDen = fitRangeNum
nBins = 30

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

etaBinsGH = np.array([0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4])
etaBinsBF = np.array([0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4])
lumiBinsGH= np.array( [0, 4000, 6500, 7000, 9000, 10000, 20000])
lumiBinsBF= np.array( [0, 4000, 6500, 7000, 9000, 10000, 20000])

backgroundFitFunctionNUM  = '[0] * TMath::Erf( ([1]-x) / [2]) + expo(3)'
#backgroundFitFunctionNUM  = 'expo(0)'
backgroundFitFunctionDEN  = backgroundFitFunctionNUM
signalFitFunnctionNUM     = '[0] * exp( -0.5 * (x-[1]) * (x-[1]) / ([2]*[2])) + [3] * exp( -0.5*(x - [1]) * (x - [1]) / ([4]*[4])) '
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

#fitter.AddBinnedVar('bp_eta'               , etaBins)
#fitter.AddBinnedVar('bp_pt'             , ptBins            )
fitter.AddBinnedVar('bp_eta'            , etaBinsGH           )
#fitter.AddBinnedVar('iLumi'             , lumiBinsBF         )
#fitter.AddBinnedVar('bp_pt__VS__bp_eta' , (ptBins, etaBins) )

fitter.SetOptions(
            fitAttNo = 2, 
            pdbFit = False, 
            useGausSignal = False, 
            DrawResidual = True
)

fitter.CalculateEfficiency()
