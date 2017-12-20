import ROOT
import numpy as np
import math
import json
from collections import OrderedDict
from classes.eff_from_ds_c import FittR

ROOT.gStyle.SetOptFit(1111)
#ROOT.gStyle.SetOptStat(0)
#ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kFatal;")

## variables
den = 'ds_hasphi & mu1_muonid_soft & mu2_muonid_soft & sv_prob>0.1 & sv_ls>2 & sv_cos>0.999 & hlt_dimuon0_phi_barrel & pi_pt>1.2 & ds_pt>8'
num = 'hlt_doublemu3_trk_tau3mu'
run = 'run > 274954'
bbn = 28
varName = 'ds_mass'


iFile = ROOT.TFile.Open('/afs/cern.ch/work/l/lguzzi/samples/ds_onia2016.root')

ptBins  = np.array( [8, 15, 35, 1000])
etaBins = np.array( [0., 0.7, 1.5])

## define the fit functions
ws = ROOT.RooWorkspace('ws', ROOT.kTRUE)
ws.factory('Gaussian::pGausDs(%s[1.8, 2.02],pMeanDs[1.97, 1.93, 1.99],pSigmaDs[0.012, 0.0001, 0.02])' %varName)
ws.factory('Gaussian::pGausDp(%s[1.8, 2.02],pMeanDp[1.87, 1.83, 1.89],pSigmaDp[0.012, 0.0001, 0.02])' %varName)
ws.factory('Gaussian::fGausDs(%s[1.8, 2.02],fMeanDs[1.97, 1.93, 1.99],fSigmaDs[0.012, 0.0001, 0.02])' %varName)
ws.factory('Gaussian::fGausDp(%s[1.8, 2.02],fMeanDp[1.87, 1.83, 1.89],fSigmaDp[0.012, 0.0001, 0.02])' %varName)

ws.factory('SUM::signalPass(pDs_yield[0, 1]*pGausDs,pGausDp)')
ws.factory('SUM::signalFail(fDs_yield[0, 1]*fGausDs,fGausDp)')

ws.factory('Chebychev::backgroundPass(%s, chebPass[0,-1,1])' %varName)
ws.factory('Chebychev::backgroundFail(%s, chebFail[0,-1,1])' %varName)

eFittR = FittR( iFile     = iFile   , 
                nBins     = bbn     ,
                den       = den     , 
                num       = num     ,
                run       = run     , 
                workspace = ws      ,
                varName   = varName ,
    )

eFittR.AddVariable( ('ds_pt'      , ptBins ))
eFittR.AddVariable( ('abs(ds_eta)', etaBins))

## <<MAIN LOOP>>
eFittR.generateJson()
eFittR.saveResults('eff_from_ds.json')

    #eFittR.FillJson(ef_er)