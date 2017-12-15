import ROOT
import numpy as np
import math
import json
from collections import OrderedDict

ROOT.gStyle.SetOptFit(1111)
ROOT.gStyle.SetOptStat(1000000001)
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kFatal;")

## return the gaus integral (NOTE needs bin width)
def GetGausIntegral(norm, sigma, errNorm, errSigma):
    area = norm*sigma*math.sqrt(2.*math.pi)
    error= math.sqrt(2.*math.pi) * (norm*errSigma + sigma*errNorm)
    res = np.array([area/0.0075, error**2])

    return  res

## gaussian function
def gauss (x, norm, mean, sigma):
    arg  = ((x - mean)/(2.*sigma))**2
    return norm*math.exp(-arg)

## polynomial function (1)
def pol1 (x, a, b):
    return a + x*b

## functions used for fit
def fitFunc (x, par):
    return gauss(x[0], par[0], par[1], par[2]) + gauss(x[0], par[3], par[4], par[5]) + pol1(x[0], par[6], par[7])

## get bin interval condition
def BinRange(ind, bins, var):
    return 'abs(ds_%s) >= %s && abs(ds_%s) <= %s' % (var, bins[ind], var, bins[ind+1])

def getBinRange (i, bins, sep = ','):
    down =  str(bins[i])
    up   =  str(bins[i+1])
    return down+sep+up

## some objects
inFile    = ROOT.TFile.Open('/afs/cern.ch/work/l/lguzzi/samples/ds_onia2016.root')
tree      = inFile.Get("tree")
outFile   = ROOT.TFile.Open('eff_from_ds.root', 'RECREATE')

## json output
jsonStruc = OrderedDict()
outJson   = open('eff_from_ds.json', 'w')

## binning
ptBins  = np.array( [8, 15 , 30, 1000])
etaBins = np.array( [0, 0.7, 1.5])
varList = [ ('pt' , ptBins ),
            ('eta', etaBins)
]

## efficiencies graphs
ptGraph   = ROOT.TGraphErrors()
etaGraph  = ROOT.TGraphErrors()
effGraphs = [ptGraph, etaGraph]

## event selection
den = 'ds_hasphi & mu1_muonid_soft & mu2_muonid_soft & sv_prob>0.1 & sv_ls>2 & sv_cos>0.999 & hlt_dimuon0_phi_barrel & pi_pt>1.2 & ds_pt>8'
num = '%s & hlt_doublemu3_trk_tau3mu' % den

## 2D eff
eff_2D = ROOT.TH2F('2Deff', '', len(ptBins)-1, 0, len(ptBins)-1, len(etaBins)-1, 0, len(etaBins)-1)

def getEff( varName, bins):
    jsonOut = OrderedDict()
    for i in range( len(bins)-1):
        ## fitfunctions
        fitFuncN = ROOT.TF1('fitFnum', fitFunc, 1.8, 2.02, 8)
        fitFuncD = ROOT.TF1('fitFden', fitFunc, 1.8, 2.10, 8)
        ## set the fit functions
        fitFuncD.SetParameter(0, 1000.) ; fitFuncD.SetParLimits(0, 0, 10000)    ; fitFuncD.SetParName(0, 'N_{1}')      ## norm gaus1
        fitFuncD.SetParameter(1, 1.97 ) ; fitFuncD.SetParLimits(1, 1.93, 2.0)   ; fitFuncD.SetParName(1, '#mu_{1}')    ## mean gaus1
        fitFuncD.SetParameter(2, 0.01 ) ; fitFuncD.SetParLimits(2, 0, 0.07)     ; fitFuncD.SetParName(2, '#sigma_{1}') ## sigm gaus1
        fitFuncD.SetParameter(3, 1000.) ; fitFuncD.SetParLimits(3, 0, 10000)    ; fitFuncD.SetParName(3, 'N_{2}')      ## norm gaus2
        fitFuncD.SetParameter(4, 1.87 ) ; fitFuncD.SetParLimits(4, 1.83, 1.9)   ; fitFuncD.SetParName(4, '#mu_{2}')    ## mean gaus2
        fitFuncD.SetParameter(5, 0.01 ) ; fitFuncD.SetParLimits(5, 0, 0.07)     ; fitFuncD.SetParName(5, '#sigma_{2}') ## sigm gaus2
        fitFuncD.SetParameter(6, 500. ) ; fitFuncD.SetParLimits(6, 0, 2000)     ; fitFuncD.SetParName(6, 'q')          ## norm pol1
        fitFuncD.SetParameter(7, -1000) ; fitFuncD.SetParLimits(7, -5000, 5000) ; fitFuncD.SetParName(7, 'm')          ## ang. pol1

        fitFuncN.SetParameter(0, 1000.) ; fitFuncN.SetParLimits(0, 0, 10000)    ; fitFuncN.SetParName(0, 'N_{1}')      ## norm gaus1
        fitFuncN.SetParameter(1, 1.97 ) ; fitFuncN.SetParLimits(1, 1.93, 2.0)   ; fitFuncN.SetParName(1, '#mu_{1}')    ## mean gaus1
        fitFuncN.SetParameter(2, 0.01 ) ; fitFuncN.SetParLimits(2, 0, 0.07)     ; fitFuncN.SetParName(2, '#sigma_{1}') ## sigm gaus1
        fitFuncN.SetParameter(3, 1000.) ; fitFuncN.SetParLimits(3, 0, 10000)    ; fitFuncN.SetParName(3, 'N_{2}')      ## norm gaus2
        fitFuncN.SetParameter(4, 1.87 ) ; fitFuncN.SetParLimits(4, 1.83, 1.9)   ; fitFuncN.SetParName(4, '#mu_{2}')    ## mean gaus2
        fitFuncN.SetParameter(5, 0.01 ) ; fitFuncN.SetParLimits(5, 0, 0.07)     ; fitFuncN.SetParName(5, '#sigma_{2}') ## sigm gaus2
        fitFuncN.SetParameter(6, 500. ) ; fitFuncN.SetParLimits(6, 0, 2000)     ; fitFuncN.SetParName(6, 'q')          ## norm pol1
        fitFuncN.SetParameter(7, -1000) ; fitFuncN.SetParLimits(7, -5000, 5000) ; fitFuncN.SetParName(7, 'm')          ## ang. pol1

        ##get the bin range
        binR = BinRange(i, vv[1], vv[0])
        
        ## get the histos
        tree.Draw("ds_mass>>histoN(40, 1.8, 2.1)", '%s & %s' % (num, binR))
        tree.Draw("ds_mass>>histoD(40, 1.8, 2.1)", '%s & %s' % (den, binR))
        
        histoN = ROOT.gDirectory.Get('histoN') ; histoN.SetName('%s_bin%s NUM' % (varName, i))
        histoD = ROOT.gDirectory.Get('histoD') ; histoD.SetName('%s_bin%s DEN' % (varName, i))

        ## fit the histos
        histoN.Fit(fitFuncN, "RIM")
        histoD.Fit(fitFuncD, "RIM")

        ## update the fit function to the fit panel results
        fitFuncN = histoN.GetFunction(fitFuncN.GetName())
        fitFuncD = histoD.GetFunction(fitFuncD.GetName())

        ## get the integral
        intD = GetGausIntegral( fitFuncD.GetParameter(0), fitFuncD.GetParameter(2),
                                fitFuncD.GetParError (0), fitFuncD.GetParError (2)) +\
               GetGausIntegral( fitFuncD.GetParameter(3), fitFuncD.GetParameter(5),
                                fitFuncD.GetParError (3), fitFuncD.GetParError (5))

        intN = GetGausIntegral( fitFuncN.GetParameter(0), fitFuncN.GetParameter(2),
                                fitFuncN.GetParError (0), fitFuncN.GetParError (2)) +\
               GetGausIntegral( fitFuncN.GetParameter(3), fitFuncN.GetParameter(5),
                                fitFuncN.GetParError (3), fitFuncN.GetParError (5))
        ## get the efficiency
        eff = intN[0]/intD[0]
        err = math.sqrt( ((1./intD[0])**2) * intN[1] + ((intN[0]/intD[0]**2)**2) * intD[1])

         ## results
        jsonOut[getBinRange(i, bins)] = OrderedDict()
        jsonOut[getBinRange(i, bins)]['value'] = eff
        jsonOut[getBinRange(i, bins)]['error'] = err

    return jsonOut

for vv in varList:
    jsonStruc[vv[0]] = OrderedDict()
    if not isinstance(vv[1], tuple): 
        jsonStruc[vv[0]] = getEff( vv[0], vv[1])
    else:
        var1 = vv[0].split('_')[1]
        var2 = vv[0].split('_')[0]
        for j in range( len(vv[1][1])-1):
            jsonStruc[vv[0]][getBinRange(j, vv[1][1])] = OrderedDict()
            jsonStruc[vv[0]][getBinRange(j, vv[1][1])] = getEff('%s_bin%s__%s_bin%s' % (var1, j, var2), vv[1][0])

outJson.write(json.dumps(jsonStruc, indent=4, sort_keys=False))
