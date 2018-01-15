import ROOT
import json

from collections import OrderedDict

def getXvalue(label):
    return 0.5*( float( label.split(',')[0]) + float( label.split(',')[1]))

def getXerror(index, keys):
    keys = [str(kk) for kk in keys]
    ret =  getXvalue(keys[index]) - getXvalue(keys[index-1]) - getXerror(index-1, keys) if index != 0  else getXvalue(keys[index])
    return ret

mainKey = 'iLumi'

bfFile = open('results/BF.json', 'r')
ghFile = open('results/GH.json', 'r')

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
    bfGraph.SetPoint(jj, getXvalue(kk), jsonBF[kk]['value'])
    bfGraph.SetPointError(jj, getXerror(jj, jsonBF.keys()), jsonBF[kk]['error'])

for jj, kk in enumerate(jsonGH.keys()):
    kk = str(kk)
    ghGraph.SetPoint(jj, getXvalue(kk), jsonGH[kk]['value'])
    ghGraph.SetPointError(jj, getXerror(jj, jsonGH.keys()), jsonGH[kk]['error'])

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
