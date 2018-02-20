import ROOT
import json
import math
import numpy as np

from classes.Trg_fitter import TrgFitter 

## setup ROOT
ROOT.gStyle.SetOptFit(1111)
ROOT.gStyle.SetOptStat(1000000001)
#ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kFatal;")

## input file and tree
iFile = ROOT.TFile('/afs/cern.ch/work/l/lguzzi/samples/ds_onia2016_skimmed.root')
tree  = iFile.Get('tree')

## denominator and numerator definition. NOTE: no need to repeat the den in the num definition
## oth = other conditions (e.g. run number, lumi)
den = 'ds_hasphi & mu1_muonid_soft & mu2_muonid_soft & sv_prob>0.1 & sv_ls>2 & sv_cos>0.999 & hlt_dimuon0_phi_barrel & pi_pt>1.2 & ds_pt > 8'
num = 'hlt_doublemu3_trk_tau3mu'
oth = 'run < 278802'

## mainVar = variable to fit
## fileName = output file
mainVar  = 'ds_mass'
fileName = 'sample_fit'

## fit range defined over mainvar and number of bins used

fitRange = (    1.8, 
                2.1
)
nBins = 28

## parameter init as  (name, init. value, (boundaries))
## if None is filled, the init. will be skipped (don't use None as name tough)
## parameters are fed to the fitter as numerator signal pars (numParS), numerator background pars (numPasB), ...
## NOTE: ROOT doesn't keep the parameter order when summing PDFs. If defining new PDFs, check from fit panel that the function is defined correctly
numParB = [ 
            ('N+'     , 1000     , (0, 100000))      ,
            ('#mu+'   , 1.87     , (1.83, 1.90))     ,
            ('#sigma+', 0.02     , (0.005, 0.1 ))   ,
            ('a'     , None     , None)             ,
            ('b'     , None     , None)             ,
            ('N_{2}'     , 1000     , (0, 100000))      ,
            ('#mu_{2}'   , 1.87     , (1.85, 1.90))     ,
            ('#sigma_{2}', 0.02     , (0.01, 0.1 ))   ,
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
            ('N_{2}'     , 1000     , (0, 100000))      ,
            ('#mu_{2}'   , 1.87     , (1.85, 1.90))     ,
            ('#sigma_{2}', 0.02     , (0.01, 0.1 ))   ,
]
denParS = [
            ('Ns'     , 10000    , (0, 100000))      ,
            ('#mus'   , 1.97     , (1.93, 2.00))     ,
            ('#sigmas', 0.02     , (0.005, 0.1 ))    ,

]

## define the binning used
wholeStat = np.array([0, 1000000])
ptBins  = np.array( [8, 15])# , 35, 1000])
etaBins = np.array( [0, 0.7])#, 1.5])

## fitter object takes care of fit
fitter = TrgFitter( tree     =  tree    , 
                    mainVar  =  mainVar , 
                    den      =  den     , 
                    num      =  num     , 
                    oth      =  oth     ,   
                    fitRange =  fitRange,
                    nBins    =  nBins   ,
                    fileName =  fileName,
)

## set the fitter pdf
fitter.SetPDFs( numPDFs = 'gaus', 
                numPDFb = 'gaus(0)+pol1(3)', 
                denPDFs = 'gaus', 
                denPDFb = 'gaus(0)+pol1(3)', 
                numParS = numParS, 
                numParB = numParB, 
                denParS = denParS, 
                denParB = denParB, 
)

## add the variables to the fitter in the form (name, binning)
## 2D variables names must be separated by '__VS__' (NB two underscores per side)
#fitter.AddBinnedVar('ds_pt'             , ptBins   )
#fitter.AddBinnedVar('ds_eta'            , etaBins  )
fitter.AddBinnedVar('ds_pt__VS__ds_eta' , (ptBins, etaBins) )

##
## general options
##
##  fittAttNo = number of initial fit attempt before prompting pdb (NOTE: if == 1 may crash)
##  pdbFIt = start pdb after automatic fit for manual tweak
##  fitOpt = Fit() method option (default = RIMQ)
##  useGausSignal = override the ROOT integral methods and use the gaussian integral definition. NOTE: if enabled, errors doesn't take into account the correlations between the parameters. Use default value (False) to use the ROOT Integral() method and the correct error propagation.

fitter.SetOptions(fitAttNo = 2, pdbFit = True)

fitter.CalculateEfficiency()
