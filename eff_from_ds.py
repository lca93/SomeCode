import ROOT
import numpy as np
import math
import json
from collections import OrderedDict
from classes.eff_from_ds_c import FittR

ROOT.gStyle.SetOptFit(1111)
ROOT.gStyle.SetOptStat(1000000001)
#ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kFatal;")

## variables
den = 'ds_hasphi & mu1_muonid_soft & mu2_muonid_soft & sv_prob>0.1 & sv_ls>2 & sv_cos>0.999 & hlt_dimuon0_phi_barrel & pi_pt>1.2 & ds_pt>8'
num = 'hlt_doublemu3_trk_tau3mu'
run = 'run > 274954'
bng ='(40, 1.8, 2.1)'

mass = ROOT.RooRealVar('mass', 'mass', 1.8, 2.02, 'GeV')

iFile = ROOT.TFile.Open('/afs/cern.ch/work/l/lguzzi/samples/ds_onia2016.root')

ptBins  = np.array( [8, 20, 35, 1000])
etaBins = np.array( [0., 0.7, 1.5])

eFittR = FittR( iFile   = iFile    , 
                mainVar = 'ds_mass', 
                RooVar  = mass     ,
                binning = bng      ,
                den = den, 
                num = num,
                run = run, 
    )

## define the fit functions variables
    ## signal
pGausDp = eFittR.BuildGaussian( 'pGausDp', 'pMeanDp[1.87, 1.83, 1.89]', 'pSigmaDp[0.012, 0.0001, 0.02]')
pGausDs = eFittR.BuildGaussian( 'pGausDs', 'pMeanDs[1.97, 1.93, 1.99]', 'pSigmaDs[0.012, 0.0001, 0.02]')

fGausDp = eFittR.BuildGaussian( 'fGausDp', 'fMeanDp[1.87, 1.83, 1.89]', 'fSigmaDp[0.012, 0.0001, 0.02]')
fGausDs = eFittR.BuildGaussian( 'fGausDs', 'fMeanDs[1.97, 1.93, 1.99]', 'fSigmaDs[0.012, 0.0001, 0.02]')

pSignal = eFittR.Sum2PDFs('pSignal', pGausDp, pGausDs)
fSignal = eFittR.Sum2PDFs('fSignal', fGausDp, fGausDs)
    ## background
pBack = eFittR.BuildPolynomial1('pBkg', ('pA[-1, -10, 10]', 'pB[0.5, 0, 1]'))
fBack = eFittR.BuildPolynomial1('fBkg', ('fA[-1, -10, 10]', 'fB[0.5, 0, 1]'))
    ## pdfs using for fit
tPassing = eFittR.Sum2PDFs('tPassing', pSignal, pBack)
tFailing = eFittR.Sum2PDFs('tFailing', fSignal, fBack)
    ## total events
tTotal = eFittR.Sum2PDFs('tTotal', tPassing, tFailing, 0.5)

fram = mass.frame() ; frem = fram.Clone() ; frim = frem.Clone()
ddHisto = eFittR.load_histo('ddHisto', den)
pnHisto = eFittR.load_histo('pnHisto', '%s & %s'    % (den, num))
fnHisto = eFittR.load_histo('fnHisto', '%s & %s==0' % (den, num))

tPassing.fitTo(pnHisto)
tFailing.fitTo(fnHisto)
#tTotal.fitTo(ddHisto)

cc = ROOT.TCanvas()
cc.Divide(2,2)

cc.cd(1) ; pnHisto.plotOn(fram) ; tPassing.plotOn(fram) ; fram.Draw()
cc.cd(2) ; fnHisto.plotOn(frem) ; tFailing.plotOn(frem) ; frem.Draw()
cc.cd(3) ; ddHisto.plotOn(frim) ; tTotal.plotOn(frim)   ; frim.Draw()

cc.Update()
import pdb ; pdb.set_trace()