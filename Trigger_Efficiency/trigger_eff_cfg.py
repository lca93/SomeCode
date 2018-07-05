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

tight2016 = '   Glb == 1                    && \
                PF == 1                     && \
                glbChi2 < 10                && \
                glbValidMuHits > 0          && \
                numberOfMatchedStations > 1 && \
                dB < 0.2                    && \
                dzPV < 0.5                  && \
                tkValidPixelHits > 0        && \
                tkTrackerLay > 5'

mediumRUN = '(Medium2016 && run<278810) || (Medium && run>278810)'

loose = 'Loose == 1'

soft2016 =  '   TMOST == 1 && \
                tkTrackerLay > 5 && \
                tkPixelLay > 0 && \
                abs(dzPV) < 20. && \
                abs(dB) < 0.3'


filelist = [
    '/afs/cern.ch/work/l/lguzzi/CMSSW_8_0_25/src/MuonAnalysis/skimmed_data/with_cuts/skimmed_skim_data_2016B_ReReco_addBDT.root',
    '/afs/cern.ch/work/l/lguzzi/CMSSW_8_0_25/src/MuonAnalysis/skimmed_data/with_cuts/skimmed_skim_data_2016C_ReReco_addBDT.root',
    '/afs/cern.ch/work/l/lguzzi/CMSSW_8_0_25/src/MuonAnalysis/skimmed_data/with_cuts/skimmed_skim_data_2016D_ReReco_addBDT.root',
    '/afs/cern.ch/work/l/lguzzi/CMSSW_8_0_25/src/MuonAnalysis/skimmed_data/with_cuts/skimmed_skim_data_2016E_ReReco_addBDT.root',
    '/afs/cern.ch/work/l/lguzzi/CMSSW_8_0_25/src/MuonAnalysis/skimmed_data/with_cuts/skimmed_skim_data_2016F_ReReco_addBDT.root',
    '/afs/cern.ch/work/l/lguzzi/CMSSW_8_0_25/src/MuonAnalysis/skimmed_data/with_cuts/skimmed_skim_data_2016G_ReReco_addBDT.root',
    '/afs/cern.ch/work/l/lguzzi/CMSSW_8_0_25/src/MuonAnalysis/skimmed_data/with_cuts/skimmed_skim_data_2016H_addBDT.root',
]

iFile = ROOT.TChain('iFile')
for ff in filelist: iFile.Add(ff)

tree  = iFile.Get('tpTree/fitterTree')

## fitter settings
den = ' tag_pt > 7.5                    && \
        pt > 2                          && \
        abseta < 2.5                    && \
        tag_abseta < 2.4                && \
        pair_drM1 > 0.5                 && \
        pair_probeMultiplicity == 1     && \
        tag_Mu7p5_MU  == 1              && \
        tag_Mu7p5_Track2_Jpsi_MU == 1   && \
        Mu7p5_Track2_Jpsi_TK == 1       && \
        '
num = tight2016
oth = '1'

mainVar  = 'mass'
fileName = 'data_tight2016'

## pdf's settings
fitRangeNum = (2.9, 3.3)
fitRangeDen = fitRangeNum
nBins = 50

numParB = [ 
            #('Norm'         , 5000      , (0, 10000))   ,
            #('Edge'         , 5.13      , (5.12, 5.2))  ,
            #('Den'          , 0.05      , (0.02, 0.2))  ,
            ('A'            , 10        , (0, 50))      ,
            ('B'            , -1        , (-10, 0))     ,
]
numParS = [
            ('N'        , 100      , (0, 100000))     ,
            ('#mu'      , 3.1      , (3.0, 3.2))      ,
            ('#sigma'   , 0.02     , (0.01, 0.1 ))    ,
            ('N2'       , 100      , (0, 100000))     ,
            ('#sigma2'  , 0.02     , (0.01, 0.1 ))    ,
]
denParB = numParB
denParS = numParS

ptBins  = np.array( [3.25, 3.5, 3.75, 4])
etaBins = np.array( [1.2, 2.1, 2.4])

backgroundFitFunctionNUM  = 'expo(0)'
signalFitFunnctionNUM     = '[0]*exp(-0.5*(x-[1])**2/[2]**2) + [3]*exp(-0.5**(x-[1])**2/[4]**2)'

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
