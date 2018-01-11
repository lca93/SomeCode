import ROOT
import json
import sys

from collections import OrderedDict

ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gStyle.SetPaintTextFormat(".3f")
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kFatal;")
ROOT.TH1.SetDefaultSumw2()

def getXvalue(label):
    return 0.5*( float( label.split(',')[0]) + float( label.split(',')[1]))

def getXerror(index, keys):
    return getXvalue(keys[index]) - getXvalue(keys[index-1]) + getXerror(index-1, keys) if index != 0  else getXvalue(keys[index])

period = str(sys.argv[1])
mainKey= 'pt_eta'
etaKeys= [  '0.0,0.7',
            '0.7,1.5',
            '1.5,2.4',
]
ptKeys = [  '5,15'   ,
            '15,35'  ,
            '35,1000',
]

rFile = ROOT.TFile('%s.root' % period, 'RECREATE')

lowLumi = open('results/%s_lowLumi.json'    % period, 'r')
higLumi = open('results/%s_highLumi.json'   % period, 'r')
midLumi = open('results/%s_midLumi.json'    % period, 'r')

jsonLowLumi = json.load(lowLumi, object_pairs_hook=OrderedDict)[mainKey]
jsonHigLumi = json.load(higLumi, object_pairs_hook=OrderedDict)[mainKey]
jsonMidLumi = json.load(midLumi, object_pairs_hook=OrderedDict)[mainKey]

TH2List = []
for ii, pp in enumerate(ptKeys): 
    TH2List.append(ROOT.TH2F('pt_%s' % pp, 'pt range: %s'% pp, len(etaKeys), 0, len(etaKeys), 3, 0, 3))
    TH2List[ii].GetYaxis().SetBinLabel(1, 'L')
    TH2List[ii].GetYaxis().SetBinLabel(2, 'M')
    TH2List[ii].GetYaxis().SetBinLabel(3, 'H')
    for jj, ee in enumerate(etaKeys):
        TH2List[ii].GetXaxis().SetBinLabel(jj+1, ee)


rFile.cd()

for jj, ee in enumerate(etaKeys):
    rFile.cd() ; rFile.mkdir(ee) ; rFile.cd(ee)
    
    i = 0

    c1 = ROOT.TCanvas('mainCvas', '')

    lowGraph = ROOT.TGraphErrors()
    higGraph = ROOT.TGraphErrors()
    midGraph = ROOT.TGraphErrors()

    lowGraph.SetName('LOW__%s' % ee) 
    higGraph.SetName('HIG__%s' % ee) 
    midGraph.SetName('MID__%s' % ee)

    leg = ROOT.TLegend(0.7, 0.25, 0.85, 0.15)
    
    leg.AddEntry(lowGraph, 'iLumi < 4000', "lp")
    leg.AddEntry(higGraph, 'iLumi > 8000', "lp")
    leg.AddEntry(midGraph, 'iLumi in (4000, 8000)', "lp")

    lowGraph.SetMarkerStyle(21)
    higGraph.SetMarkerStyle(21)
    midGraph.SetMarkerStyle(21)

    lowGraph.SetMarkerColor(ROOT.kRed)
    higGraph.SetMarkerColor(ROOT.kBlue)
    midGraph.SetMarkerColor(ROOT.kGreen)
    
    lowGraph.SetLineColor(ROOT.kRed)
    higGraph.SetLineColor(ROOT.kBlue)
    midGraph.SetLineColor(ROOT.kGreen)

    for ii, pp in enumerate(ptKeys):
        lowGraph.SetPoint(ii, getXvalue(pp), jsonLowLumi[ee][pp]['value'])
        higGraph.SetPoint(ii, getXvalue(pp), jsonHigLumi[ee][pp]['value'])
        midGraph.SetPoint(ii, getXvalue(pp), jsonMidLumi[ee][pp]['value'])

        lowGraph.SetPointError(ii, getXerror(ii, ptKeys), jsonLowLumi[ee][pp]['error'])
        higGraph.SetPointError(ii, getXerror(ii, ptKeys), jsonHigLumi[ee][pp]['error'])
        midGraph.SetPointError(ii, getXerror(ii, ptKeys), jsonMidLumi[ee][pp]['error'])

        TH2List[ii].SetBinContent(jj+1, 1, jsonLowLumi[ee][pp]['value'])
        TH2List[ii].SetBinContent(jj+1, 2, jsonMidLumi[ee][pp]['value'])
        TH2List[ii].SetBinContent(jj+1, 3, jsonHigLumi[ee][pp]['value'])

        TH2List[ii].SetBinError(jj+1, 1, jsonLowLumi[ee][pp]['error'])
        TH2List[ii].SetBinError(jj+1, 2, jsonMidLumi[ee][pp]['error'])
        TH2List[ii].SetBinError(jj+1, 3, jsonHigLumi[ee][pp]['error'])

    mGraph = ROOT.TMultiGraph('%smG', '')
    
    mGraph.SetTitle('Efficiency comparison - eta range: %s; pt [GeV]; efficiency' % ee)
    
    mGraph.Add(lowGraph)
    mGraph.Add(higGraph)
    mGraph.Add(midGraph)

    c1.cd() ; mGraph.Draw("AP")
    leg.Draw('same')

    lowGraph.Write()
    midGraph.Write()
    higGraph.Write()
    mGraph.Write()
    c1.SetLogx()
    c1.Write()

rFile.cd() ; rFile.mkdir('2D_lumiVSeta') ; rFile.cd('2D_lumiVSeta')
for hh in TH2List: 
    hh.Write()
    c2 = ROOT.TCanvas() ; c2.cd()
    hh.Draw('colz2 text error')
    c2.Write()


rFile.Close()
