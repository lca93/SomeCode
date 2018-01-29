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

iFile = ROOT.TFile('/afs/cern.ch/work/l/lguzzi/samples/bp_allstat.root')
tree  = iFile.Get('mTree')


## fitter settings
den = '1'
num = 'pass'
oth = '1'

mainVar  = 'bMass'
fileName = 'allStat'

## pdf's settings
fitRange = (5.1, 5.4)
nBins = 28

numParB = [ ('a'     , None     , None)             ,
            ('b'     , None     , None)             ,
]
numParS = [
            ('N'     , 10000    , (0, 100000))      ,
            ('#mu'   , 5.28     , (5.25, 5.30))     ,
            ('#sigma', 0.02     , (0.005, 0.1 ))    ,
]
denParB = [ ('a'     , None     , None)             ,
            ('b'     , None     , None)             ,
]
denParS = [
            ('N'     , 10000    , (0, 100000))      ,
            ('#mu'   , 5.28     , (5.25, 5.30))     ,
            ('#sigma', 0.02     , (0.005, 0.1 ))    ,
]

ptBins  = np.array( [5, 15 , 35, 1000])
etaBins = np.array( [0, 0.7, 1.5, 2.4])
lumiBins= np.array( [0, 6000, 8000, 10000, 20000])

etaBinsBF = np.array([0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4])
etaBinsGH = np.array([0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4])
lumiBinsGH= np.array( [0, 4000, 6500, 7000, 9000, 10000, 20000])
lumiBinsBF= np.array( [0, 4000, 6500, 7000, 9000, 10000, 20000])

fitter = TrgFitter( tree     =  tree    , 
                    mainVar  =  mainVar , 
                    den      =  den     , 
                    num      =  num     , 
                    oth      =  oth     ,   
                    fitRange =  fitRange,
                    nBins    =  nBins   ,
                    fileName =  fileName,
)

fitter.SetPDFs( numPDFs = 'gaus', 
                numPDFb = 'pol1', 
                denPDFs = 'gaus', 
                denPDFb = 'pol1', 
                numParS = numParS, 
                numParB = numParB, 
                denParS = denParS, 
                denParB = denParB, 
)

#fitter.AddBinnedVar('bp_pt'             , ptBins            )
fitter.AddBinnedVar('bp_eta'            , etaBinsGH           )
#fitter.AddBinnedVar('iLumi'             , lumiBinsGH         )
#fitter.AddBinnedVar('bp_pt__VS__bp_eta' , (ptBins, etaBins) )

fitter.SetOptions(fitAttNo = 2, pdbFit = True)

fitter.CalculateEfficiency()
