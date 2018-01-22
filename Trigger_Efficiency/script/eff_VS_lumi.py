import ROOT
import json

from collections import OrderedDict

def getXvalue(label, idx, var):
    if var == 'BF': xVals = [4662, 6815, 8510, 10532]   ## BF
    if var == 'GH': xVals = [5272, 6892, 8883, 10873]   ## GH
    xVals = [4714, 6822, 8751, 10712]   ## allStat
    return 0.5*( float( label.split(',')[0]) + float( label.split(',')[1]))
    return xVals[idx]

def getXerror(index, keys, var):
    return 0
    keys = [str(kk) for kk in keys]
    ret =  getXvalue(keys[index], index, var) - getXvalue(keys[index], index-1, var) - getXerror(index-1, keys, var) if index != 0  else getXvalue(index, var)
    return ret

mainKey = 'bp_eta'

bfFile = open('results/BF_eta.json', 'r')
ghFile = open('results/GH_eta.json', 'r')

rFile = ROOT.TFile('effVSilumi.root', 'RECREATE') ; rFile.cd()

jsonBF = json.load(bfFile, object_pairs_hook=OrderedDict)[mainKey]
jsonGH = json.load(ghFile, object_pairs_hook=OrderedDict)[mainKey]

bfGraph = ROOT.TGraphErrors()
bfGraph.SetMarkerStyle(21)
bfGraph.SetMarkerColor(ROOT.kRed)
bfGraph.SetLineColor(ROOT.kRed)

ghGraph = ROOT.TGraphErrors()
ghGraph.SetMarkerStyle(21)
ghGraph.SetMarkerColor(ROOT.kBlue)
ghGraph.SetLineColor(ROOT.kBlue)

for jj, kk in enumerate(jsonBF.keys()):
    kk = str(kk)
    bfGraph.SetPoint(jj, getXvalue(kk, jj, 'BF'), jsonBF[kk]['value'])
    bfGraph.SetPointError(jj, getXerror(jj, jsonBF.keys(), 'BF'), jsonBF[kk]['error'])

for jj, kk in enumerate(jsonGH.keys()):
    kk = str(kk)
    ghGraph.SetPoint(jj, getXvalue(kk, jj, 'GH'), jsonGH[kk]['value'])
    ghGraph.SetPointError(jj, getXerror(jj, jsonGH.keys(), 'GH'), jsonGH[kk]['error'])

leg = ROOT.TLegend(0.7, 0.25, 0.85, 0.15)
    
leg.AddEntry(bfGraph, 'BF', "lp")
leg.AddEntry(ghGraph, 'GH', "lp")

mGraph = ROOT.TMultiGraph()
mGraph.SetTitle('efficiency VS iLuminosity; iLuminosity; efficiency')
mGraph.Add(bfGraph)
mGraph.Add(ghGraph)

c1 = ROOT.TCanvas() ; c1.cd()
mGraph.Draw('AP')
leg.Draw('same')

bfGraph.Write()
ghGraph.Write()
mGraph.Write()
c1.Write()

rFile.Close()
bfFile.close()
ghFile.close()
