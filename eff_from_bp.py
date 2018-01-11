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

def pol2 (x, a, b, c):
    return a*x*x + pol1(x, b, c)

def pol3 (x, a, b, c, d):
    return a*x*x*x + pol2(x, b, c, d)

## functions used for fit
def fitFunc (x, par):
    return gauss(x[0], par[0], par[1], par[2]) + pol2(x[0], par[3], par[4], par[5])

## get bin interval condition
def BinRange(ind, bins, var):
    return 'abs(%s) >= %s && abs(%s) <= %s' % (var, bins[ind], var, bins[ind+1])

def getBinRange (i, bins, sep = ','):
    down =  str(bins[i])
    up   =  str(bins[i+1])
    return down+sep+up

def setBackgdParams(bacPdf, fitPdf):
    for i in range(3): bacPdf.FixParameter(i, fitPdf.GetParameter(i))
    bacPdf.Draw('same')

def SetParameters(fitFunc, setName = False):
    fitFunc.SetParameter(3, 2000.)  ; fitFunc.SetParLimits(3, 0, 100000)    ## norm gaus1
    fitFunc.SetParameter(4, 5.28 )  ; fitFunc.SetParLimits(4, 5.2, 5.5)    ## mean gaus1
    fitFunc.SetParameter(5, 0.05 )  ; fitFunc.SetParLimits(5, 0.0001, 0.2) ## sigm gaus1
    #fitFunc.SetParameter(3, 100 )  ; fitFunc.SetParLimits(3, 0, 10000)  
    #fitFunc.SetParameter(4, 5.28)   ; fitFunc.SetParLimits(4, 5.2, 5.5)
    #fitFunc.SetParameter(5, 0.05)   ; fitFunc.SetParLimits(5, 0.02, 0.2)
    #fitFunc.SetParameter(6, 1000)   #; 
    #fitFunc.SetParameter(7, 200)    #; 
    #fitFunc.SetParameter(8, -200)   #; 
    
    if setName: fitFunc.SetParName(3, 'N_{1}')    
    if setName: fitFunc.SetParName(4, '#mu_{1}')  
    if setName: fitFunc.SetParName(5, '#sigma_{1}')
    if setName: fitFunc.SetParName(0, 'a')              
    if setName: fitFunc.SetParName(1, 'b')              
    if setName: fitFunc.SetParName(2, 'c')              

## some objects
inFile    = ROOT.TFile.Open('/afs/cern.ch/work/l/lguzzi/samples/bp_allstat.root')
tree      = inFile.Get("mTree")
outFile   = ROOT.TFile.Open('BF_lumiBins.root', 'RECREATE')

## json output
jsonStruc = OrderedDict()
outJson   = open('BF_lumiBins.json', 'w')

## binning
ptBins  = np.array( [5, 15 , 35, 1000])
etaBins = np.array( [0, 0.7, 1.5, 2.4])
lumiBins= np.array( [0, 6000, 8000, 10000, 20000])
varList = [ #('bp_pt' , ptBins ),
            #('bp_eta', etaBins),
            ('iLumi', lumiBins),
            #('pt_eta', (ptBins, etaBins))
]

## efficiencies graphs
ptGraph   = ROOT.TGraphErrors()
etaGraph  = ROOT.TGraphErrors()
effGraphs = [ptGraph, etaGraph]

## event selection
##      run > 274954 all stat with tau trigger
##      run > 278802 final F + GH
##      run < 278810 BF period
##      run > 278810 GH period
## lumiBins: 6000-8000-10000-++
## see test/readTree_Bp.C from https://github.com/sarafiorendi/MuMuTrkHLT/tree/tau3mu
aux = 'run < 278810'
den = '1'
num = '%s && pass' % den 

c1 = ROOT.TCanvas()
c1.cd()

## 2D eff
eff_2D = ROOT.TH2F('2Deff', '', len(ptBins)-1, 0, len(ptBins)-1, len(etaBins)-1, 0, len(etaBins)-1)

def getEff( varName, bins, is2D = False, indx = -1):
    jsonOut = OrderedDict()

    if is2D: bins1 = bins[0] ; bins2 = bins[1]
    else: bins1 = bins

    for i in range( len(bins1)-1):
        ## fitfunctions
        #fitFuncN = ROOT.TF1('fitFnum', fitFunc, 5.13, 5.38, 6 )
        #fitFuncD = ROOT.TF1('fitFden', fitFunc, 5.13, 5.38, 6 )
        signalN = ROOT.TF1('sigN', 'gaus', 5.13, 5.38)
        signalD = ROOT.TF1('sigD', 'gaus', 5.13, 5.38)
        backgdN = ROOT.TF1('bacN', 'pol2', 5.13, 5.38) ; backgdN.SetLineColor(ROOT.kGreen)
        backgdD = ROOT.TF1('bacD', 'pol2', 5.13, 5.38) ; backgdD.SetLineColor(ROOT.kGreen)

        fitFuncN = ROOT.TF1('fitFnum', 'sigN+bacN', 5.13, 5.38)
        fitFuncD = ROOT.TF1('fitFden', 'sigD+bacD', 5.13, 5.38)
        SetParameters (fitFuncN, setName = True)
        SetParameters (fitFuncD, setName = True)

        ##get the bin range
        if is2D:
            var1 = 'bp_'+varName.split('_')[0]
            var2 = 'bp_'+varName.split('_')[1]
            binR = '%s & %s' % (BinRange(i, bins1, var1), BinRange(indx, bins2, var2))
        else: binR = BinRange(i, bins1, varName)
        
        ## get the histos
        tree.Draw("bMass>>histoN(36, 5, 5.4)", '%s & %s & %s' % (num, binR, aux))
        tree.Draw("bMass>>histoD(36, 5, 5.4)", '%s & %s & %s' % (den, binR, aux))

        histoN = ROOT.gDirectory.Get('histoN') ; histoN.SetName('bin%s NUM' % (i))
        histoD = ROOT.gDirectory.Get('histoD') ; histoD.SetName('bin%s DEN' % (i))

        ## fit the histos
        histoN.Fit(fitFuncN, "RIMQ") ; histoN.Fit(fitFuncN, "RIMQ") ; setBackgdParams(backgdN, fitFuncN) ; c1.Update()
        import pdb ; pdb.set_trace()
        histoD.Fit(fitFuncD, "RIMQ") ; histoD.Fit(fitFuncD, "RIMQ") ; setBackgdParams(backgdD, fitFuncD) ; c1.Update()
        import pdb ; pdb.set_trace()

        ## update the fit function to the fit panel results
        fitFuncN = histoN.GetFunction(fitFuncN.GetName())
        fitFuncD = histoD.GetFunction(fitFuncD.GetName())

        ## write in file
        histoN.Write()
        histoD.Write()

        ## get the integral
        intD = GetGausIntegral( fitFuncD.GetParameter(0), fitFuncD.GetParameter(2),
                                fitFuncD.GetParError (0), fitFuncD.GetParError (2))
               #GetGausIntegral( fitFuncD.GetParameter(4), fitFuncD.GetParameter(6),
               #                 fitFuncD.GetParError (4), fitFuncD.GetParError (6))

        intN = GetGausIntegral( fitFuncN.GetParameter(0), fitFuncN.GetParameter(2),
                                fitFuncN.GetParError (0), fitFuncN.GetParError (2))
               #GetGausIntegral( fitFuncN.GetParameter(4), fitFuncN.GetParameter(6),
               #                 fitFuncN.GetParError (4), fitFuncN.GetParError (6))
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
