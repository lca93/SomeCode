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

def gaussInteg (norm, sigma, eNorm, eSigma, binSize): 
    area = norm * sigma * math.sqrt(2.*math.pi)/binSize
    error= (2.*math.pi) * ( (norm*eSigma)**2 + (sigma*eNorm)**2 ) / (binSize**2)

    return np.array([area, error])

def integFunc(func, binSize):
    return  gaussInteg( norm    = func.GetParameter(0)  ,
                        sigma   = func.GetParameter(2)  ,
                        eNorm   = func.GetParError(0)   ,
                        eSigma  = func.GetParError(2)   ,
                        binSize = binSize               ,
    ) +\
            gaussInteg( norm    = func.GetParameter(3)  ,
                        sigma   = func.GetParameter(5)  ,
                        eNorm   = func.GetParError(3)   ,
                        eSigma  = func.GetParError(5)   ,
                        binSize = binSize               ,
    )




iFile = ROOT.TFile('/afs/cern.ch/work/l/lguzzi/samples/ds_onia2016_skimmed.root')
tree  = iFile.Get('tree')


## fitter settings
den = 'ds_hasphi & mu1_muonid_soft & mu2_muonid_soft & sv_prob>0.1 & sv_ls>2 & sv_cos>0.999 & hlt_dimuon0_phi_barrel & pi_pt>1.2 & ds_pt > 8'
num = 'hlt_doublemu3_trk_tau3mu'
oth = 'run > 278802'

mainVar  = 'ds_mass'
fileName = 'test_highRun'

## pdf's settings
rLo = 1.80
rUp = 2.1
nBins = 28

##pdf's declarations
pdfSignalN = ROOT.TF1('pdfSignalN', 'gaus(0)+gaus(3)', rLo, rUp)
pdfBackgdN = ROOT.TF1('pdfBackgdN', 'pol1', rLo, rUp)
pdfSignalD = ROOT.TF1('pdfSignalD', 'gaus(0)+gaus(3)', rLo, rUp)
pdfBackgdD = ROOT.TF1('pdfBackgdD', 'pol1', rLo, rUp)

pdfN = ROOT.TF1('NumPDF', 'pdfSignalN+pdfBackgdN', rLo, rUp)
pdfD = ROOT.TF1('DenPDF', 'pdfSignalD+pdfBackgdD', rLo, rUp)

numPars = [ 
            ('N_{1}'     , 10000    , (0, 100000))      ,
            ('#mu_{1}'   , 1.97     , (1.93, 2.00))     ,
            ('#sigma_{1}', 0.02     , (0.0001, 0.1 ))   ,
            ('N_{2}'     , 1000     , (0, 100000))      ,
            ('#mu_{2}'   , 1.87     , (1.93, 1.90))     ,
            ('#sigma_{2}', 0.02     , (0.0001, 0.1 ))   ,
            ('a'     , None     , None)             ,
            ('b'     , None     , None)             ,
]

denPars = [ 
            ('N_{1}'     , 10000    , (0, 100000))      ,
            ('#mu_{1}'   , 1.97     , (1.93, 2.00))     ,
            ('#sigma_{1}', 0.02     , (0.0001, 0.1 ))   ,
            ('N_{2}'     , 1000     , (0, 100000))      ,
            ('#mu_{2}'   , 1.87     , (1.93, 1.90))     ,
            ('#sigma_{2}', 0.02     , (0.0001, 0.1 ))   ,
            ('a'     , None     , None)             ,
            ('b'     , None     , None)             ,
]

ptBins  = np.array( [8, 15 , 35, 1000])
etaBins = np.array( [0, 0.7, 1.5])
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

fitter.AddBinnedVar('ds_pt'             , ptBins            )
fitter.AddBinnedVar('ds_eta'            , etaBins           )
#fitter.AddBinnedVar('iLumi'             , lumiBins          )
#fitter.AddBinnedVar('bp_pt__VS__bp_eta' , (ptBins, etaBins) )

fitter.InitializeParameters( numPars = numPars, denPars = denPars)

fitter.SetOptions(fitAttNo = 2)



fitter.CalculateEfficiency()
