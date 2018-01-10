import ROOT
import numpy as np
import math
import json
from collections import OrderedDict

ROOT.gStyle.SetOptFit(1111)
ROOT.gStyle.SetOptStat(1000000001)
#ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kFatal;")

global binsize
binsize = 0.0075

## return the gaus integral (NOTE needs bin width)
def GetGausIntegral(norm, sigma, errNorm, errSigma):
    area = norm*sigma*math.sqrt(2.*math.pi)/binsize
    error= (2.*math.pi) * ( (norm*errSigma)**2 + (sigma*errNorm)**2 ) / (binsize**2)
    res = np.array([area, error])

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

def SetParameters(fitFunc, setName = False):
    fitFunc.SetParameter(0, 2000.)  ; fitFunc.SetParLimits(0, 0, 10000)    ## norm gaus1
    fitFunc.SetParameter(1, 5.28 )  ; fitFunc.SetParLimits(1, 5.27, 5.29)  ## mean gaus1
    fitFunc.SetParameter(2, 0.001 ) ; fitFunc.SetParLimits(2, 0.0001, 0.02)## sigm gaus1
    fitFunc.SetParameter(3, 500. ) #; fitFunc.SetParLimits(6, 0, 2000)     ## norm pol1
    fitFunc.SetParameter(4, -1000) #; fitFunc.SetParLimits(7, -5000, 5000) ## ang. pol1

    if setName: fitFunc.SetParName(0, 'N_{1}')    
    if setName: fitFunc.SetParName(1, '#mu_{1}') 
    if setName: fitFunc.SetParName(2, '#sigma_{1}')
    if setName: fitFunc.SetParName(3, 'q')        
    if setName: fitFunc.SetParName(4, 'm')           

## some objects
inFile    = ROOT.TFile.Open('/afs/cern.ch/work/l/lguzzi/samples/ds_onia2016.root')
tree      = inFile.Get("tree")
outFile   = ROOT.TFile.Open('eff_from_ds.root', 'RECREATE')

## json output
jsonStruc = OrderedDict()
outJson   = open('eff_from_ds.json', 'w')

## binning
ptBins  = np.array( [8, 15 , 35, 1000])
etaBins = np.array( [0, 0.7, 1.5])
varList = [ ('pt' , ptBins ),
            ('eta', etaBins),
            ('pt_eta', (ptBins, etaBins))
]

## efficiencies graphs
ptGraph   = ROOT.TGraphErrors()
etaGraph  = ROOT.TGraphErrors()
effGraphs = [ptGraph, etaGraph]

## event selection
##      run > 274954 all stat with tau trigger
##      run > 278802 final F + GH
run = 'run > 274954'
den = 'ds_hasphi & mu1_muonid_soft & mu2_muonid_soft & sv_prob>0.1 & sv_ls>2 & sv_cos>0.999 & hlt_dimuon0_phi_barrel & pi_pt>1.2 & ds_pt>8'
num = '%s & hlt_doublemu3_trk_tau3mu' % den

## 2D eff
eff_2D = ROOT.TH2F('2Deff', '', len(ptBins)-1, 0, len(ptBins)-1, len(etaBins)-1, 0, len(etaBins)-1)

def getEff( varName, bins, is2D = False, indx = -1):
    jsonOut = OrderedDict()

    if is2D: bins1 = bins[0] ; bins2 = bins[1]
    else: bins1 = bins

    for i in range( len(bins1)-1):
        ## fitfunctions
        fitFuncN = ROOT.TF1('fitFnum', fitFunc, 1.8, 2.02, 8)
        fitFuncD = ROOT.TF1('fitFden', fitFunc, 1.8, 2.10, 8)
        SetParameters (fitFuncN, setName = True)
        SetParameters (fitFuncD, setName = True)

        ##get the bin range
        if is2D:
            var1 = varName.split('_')[0]
            var2 = varName.split('_')[1]
            binR = '%s & %s' % (BinRange(i, bins1, var1), BinRange(indx, bins2, var2))
        else: binR = BinRange(i, bins1, varName)
        
        ## get the histos
        tree.Draw("ds_mass>>histoN(40, 2.8, 3.2)", '%s & %s & %s' % (num, binR, run))
        tree.Draw("ds_mass>>histoD(40, 2.8, 3.2)", '%s & %s & %s' % (den, binR, run))

        histoN = ROOT.gDirectory.Get('histoN') ; histoN.SetName('bin%s NUM' % (i))
        histoD = ROOT.gDirectory.Get('histoD') ; histoD.SetName('bin%s DEN' % (i))

        ## fit the histos
        histoN.Fit(fitFuncN, "RIMQ") ; histoN.Fit(fitFuncN, "RIMQ")
        import pdb ; pdb.set_trace()
        histoD.Fit(fitFuncD, "RIMQ") ; histoD.Fit(fitFuncD, "RIMQ")
        import pdb ; pdb.set_trace()

        ## update the fit function to the fit panel results
        fitFuncN = histoN.GetFunction(fitFuncN.GetName())
        fitFuncD = histoD.GetFunction(fitFuncD.GetName())

        ## write in file
        histoN.Write()
        histoD.Write()

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
        jsonOut[getBinRange(i, bins1)] = OrderedDict()
        jsonOut[getBinRange(i, bins1)]['value'] = eff
        jsonOut[getBinRange(i, bins1)]['error'] = err

    return jsonOut

for vv in varList:
    jsonStruc[vv[0]] = OrderedDict()
    outFile.cd() ; outFile.mkdir(vv[0]) ; outFile.cd(vv[0])

    if not isinstance(vv[1], tuple):     ## 1D efficiencies 
        jsonStruc[vv[0]] = getEff(varName = vv[0], bins = vv[1])
    else:                                ## 2D efficiencies
        for j in range( len(vv[1][1])-1):
            outFile.GetDirectory(vv[0]).mkdir(getBinRange(j, vv[1][1])) ; outFile.GetDirectory(vv[0]).cd(getBinRange(j, vv[1][1]))
            
            jsonStruc[vv[0]][getBinRange(j, vv[1][1])] = OrderedDict()
            jsonStruc[vv[0]][getBinRange(j, vv[1][1])] = getEff(varName = vv[0], bins = vv[1], is2D = True, indx = j)

outJson.write(json.dumps(jsonStruc, indent=4, sort_keys=False))
outJson.close()
outFile.Close()
