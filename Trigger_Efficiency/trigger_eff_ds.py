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

iFile = ROOT.TFile('/afs/cern.ch/work/l/lguzzi/samples/ds_onia2016_skimmed.root')
tree  = iFile.Get('tree')


## fitter settings
den = 'ds_hasphi & mu1_muonid_soft & mu2_muonid_soft & sv_prob>0.1 & sv_ls>2 & sv_cos>0.999 & hlt_dimuon0_phi_barrel & pi_pt>1.2 & ds_pt > 8'
num = 'hlt_doublemu3_trk_tau3mu'
oth = 'run < 278802'

mainVar  = 'ds_mass'
fileName = '1D_below_278802'

## pdf's settings
fitRange = (    1.8, 
                2.1
)
nBins = 28

numParB = [ 
            ('N+'     , 1000     , (0, 100000))      ,
            ('#mu+'   , 1.87     , (1.83, 1.90))     ,
            ('#sigma+', 0.02     , (0.005, 0.1 ))   ,
            ('a'     , None     , None)             ,
            ('b'     , None     , None)             ,
]
numParS = [
            ('Ns'     , 10000    , (0, 100000))      ,
            ('#mus'   , 1.97     , (1.93, 2.00))     ,
            ('#sigmas', 0.02     , (0.005, 0.1 ))    ,
]
denParB = [ 
            ('N+'     , 1000     , (0, 100000))      ,
            ('#mu+'   , 1.87     , (1.83, 1.90))     ,
            ('#sigma+', 0.02     , (0.005, 0.1 ))   ,
            ('a'     , None     , None)             ,
            ('b'     , None     , None)             ,
]
denParS = [
            ('Ns'     , 10000    , (0, 100000))      ,
            ('#mus'   , 1.97     , (1.93, 2.00))     ,
            ('#sigmas', 0.02     , (0.005, 0.1 ))    ,

]

ptBins  = np.array( [8, 15 , 35, 1000])
etaBins = np.array( [0, 0.7, 1.5])

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
                numPDFb = 'gaus(0)+pol1(3)', 
                denPDFs = 'gaus', 
                denPDFb = 'gaus(0)+pol1(3)', 
                numParS = numParS, 
                numParB = numParB, 
                denParS = denParS, 
                denParB = denParB, 
)

fitter.AddBinnedVar('ds_pt'             , ptBins   )
fitter.AddBinnedVar('ds_eta'            , etaBins  )
#fitter.AddBinnedVar('ds_pt__VS__ds_eta' , (ptBins, etaBins) )

fitter.SetOptions(fitAttNo = 2, pdbFit = True)

fitter.CalculateEfficiency()
