###############################################
##
## compare SFs obtained by getSFs.py
##

import ROOT
import numpy as np
import os, sys
from cfg.cfg_getSFs     import varList
from itertools import product
from libs.getSFs_libs   import GraphToHisto, HistoToGraph
import math

##set up root
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gStyle.SetPaintTextFormat(".3f")
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kFatal;")
ROOT.TH1.SetDefaultSumw2()

global muonID
global muonID_BF
global MAINDIR

## input arg
muonID    = str(sys.argv[1])
muonID_BF = muonID.replace("medium", "medium2016")

## directory
MAINDIR = "comparison/%s" % muonID
if not os.path.exists(MAINDIR): os.makedirs(MAINDIR)

## outFile
outFile = ROOT.TFile.Open("%s/%s.root" % (MAINDIR, muonID), "RECREATE")

## input files
file1 = ROOT.TFile.Open("BCDEF/BCDEF_%s/BCDEF_%s_muonID.root" % (muonID_BF, muonID_BF))
file2 = ROOT.TFile.Open("GH/GH_%s/GH_%s_muonID.root"          % (muonID, muonID))

def compare1D (key1, key2, varName, bins, outFile, etaRange = ""):
    ## set logx
    logx = True if varName[:2] == "pt" else False

    ## get the graphs: key->canvas->pad->multigrpah->graph
    DAgraph1 = key1.ReadObj().GetListOfPrimitives()[0].GetListOfPrimitives()[1].GetListOfGraphs()[0]
    MCgraph1 = key1.ReadObj().GetListOfPrimitives()[0].GetListOfPrimitives()[1].GetListOfGraphs()[1]
    SFgraph1 = key1.ReadObj().GetListOfPrimitives()[1].GetListOfPrimitives()[2]
    DAgraph2 = key2.ReadObj().GetListOfPrimitives()[0].GetListOfPrimitives()[1].GetListOfGraphs()[0]
    MCgraph2 = key2.ReadObj().GetListOfPrimitives()[0].GetListOfPrimitives()[1].GetListOfGraphs()[1]
    SFgraph2 = key2.ReadObj().GetListOfPrimitives()[1].GetListOfPrimitives()[2]

    ## multigraphs
    multiG1 = ROOT.TMultiGraph()
    multiG2 = ROOT.TMultiGraph()

    multiG1.Add(DAgraph1)
    multiG1.Add(MCgraph1)
    multiG1.Add(DAgraph2)
    multiG1.Add(MCgraph2)

    multiG2.Add(SFgraph1)
    multiG2.Add(SFgraph2)

    multiG1.SetTitle("SFs comparison  %s %s; %s; efficiency" % (muonID, etaRange, varName))
    multiG2.SetTitle(";%s; SF"                               % varName)
    ## set the graphs
    DAgraph1.SetMarkerStyle(22)
    MCgraph1.SetMarkerStyle(20)
    SFgraph1.SetMarkerStyle(20)

    DAgraph2.SetMarkerStyle(26)
    MCgraph2.SetMarkerStyle(24)
    SFgraph2.SetMarkerStyle(23)

    DAgraph1.SetMarkerColor(4) ## blue
    MCgraph1.SetMarkerColor(2) ## red
    SFgraph1.SetMarkerColor(1) ## black

    DAgraph2.SetMarkerColor(36) ## pale blue
    MCgraph2.SetMarkerColor(46) ## pale red
    SFgraph2.SetMarkerColor(8)  ## pale green

    DAgraph1.SetLineColor(4)
    MCgraph1.SetLineColor(2)
    SFgraph1.SetLineColor(1)

    DAgraph2.SetLineColor(36)
    MCgraph2.SetLineColor(46)
    SFgraph2.SetLineColor(8)

    SFgraph2.SetFillColor(8)
    SFgraph1.SetFillStyle(3004)
    SFgraph2.SetFillStyle(3004)


    ## auxiliary TH1
    supportEff = ROOT.TH1F("suppE", "", len(bins)-1, bins)
    supportRat = ROOT.TH1F("suppR", "", len(bins)-1, bins)
    supportDif = ROOT.TH1F("suppD", "", len(bins)-1, bins)

    ## SFs difference
    aux1 = GraphToHisto(SFgraph1, bins)
    aux2 = GraphToHisto(SFgraph2, bins)

    aux1.Add( aux2, -1)
    for i in range(aux1.GetSize()-1):
        aux1.SetBinContent( i+1, 
                            abs( aux1.GetBinContent(i+1) )
            )

    diffG = HistoToGraph(aux1)
    diffG.SetMarkerStyle(20)
    diffG.SetFillStyle(3004)

    multiG3 = ROOT.TMultiGraph()
    multiG3.Add(diffG)
    multiG3.SetTitle("; %s; SFs difference" % varName)

    ##set the canvas
    outCan = ROOT.TCanvas("outCan", "SFs comparison %s %s  -  %s muonID" % (varName, etaRange, muonID), 700, 1000)
    outCan.Divide(1, 3)
    outCan.GetListOfPrimitives()[0].SetPad('effPad%s'   % varName, 'effPad'  , 0., 0.50, 1., 1., 0, 0)
    outCan.GetListOfPrimitives()[1].SetPad('ratioPad%s' % varName, 'ratioPad', 0., 0.52, 1., .2, 0, 0)
    outCan.GetListOfPrimitives()[2].SetPad('diffPad%s'  % varName, 'diffPad' , 0., 0.22, 1., .0, 0, 0)
    outCan.GetListOfPrimitives()[0].SetLogx(logx)
    outCan.GetListOfPrimitives()[1].SetLogx(logx)
    outCan.GetListOfPrimitives()[2].SetLogx(logx)

    outCan.GetListOfPrimitives()[0].SetGridy(True)
    outCan.GetListOfPrimitives()[1].SetGridy(True)
    outCan.GetListOfPrimitives()[2].SetGridy(True)
    outCan.GetListOfPrimitives()[0].SetGridx(True)
    outCan.GetListOfPrimitives()[1].SetGridx(True)
    outCan.GetListOfPrimitives()[2].SetGridx(True)

    outCan.GetListOfPrimitives()[0].SetBottomMargin(0.2)
    outCan.GetListOfPrimitives()[1].SetBottomMargin(0.2)
    outCan.GetListOfPrimitives()[2].SetBottomMargin(0.2)
    
    ## legend
    leg = ROOT.TLegend(0.7, 0.5, 0.85, 0.25)
    leg.AddEntry(DAgraph1, "BCDEF Data", "lp")
    leg.AddEntry(DAgraph2, "GH Data", "lp")
    leg.AddEntry(MCgraph1, "BCDEF MC", "lp")
    leg.AddEntry(MCgraph2, "GH MC", "lp")

    leg2 = ROOT.TLegend(0.7, 0.5, 0.85, 0.25)
    leg2.AddEntry(SFgraph1, "BCDEF SFs", "lp")
    leg2.AddEntry(SFgraph2, "GH SFs", "lp")

    ## print on same canvas
    outCan.cd(1)
    supportEff.Draw()
    multiG1.Draw("same P")
    leg.Draw("same")
    multiG1.GetXaxis().SetLimits(bins[0]-0.2*abs(bins[0]), 1.1*bins[-1])

    outCan.cd(2)
    supportRat.Draw()
    multiG2.Draw("same PLE3")
    leg2.Draw("same")
    multiG2.GetYaxis().SetRangeUser(0.5, 1.2)
    multiG2.GetXaxis().SetLimits(bins[0]-0.2*abs(bins[0]), 1.1*bins[-1])

    outCan.cd(3)
    supportDif.Draw()
    multiG3.Draw("same PLE3")
    multiG3.GetYaxis().SetRangeUser( 0, 1.1*ROOT.TMath.MaxElement(diffG.GetN(), diffG.GetY()))
    multiG3.GetXaxis().SetLimits(bins[0]-0.2*abs(bins[0]), 1.1*bins[-1])

    outCan.Update()
    outCan.Write()
    outCan.Print("%s/%s/SF_comparison_%s_%s_%smuonID.pdf" % (MAINDIR, varName, etaRange, varName, muonID), "pdf")

def hasTH2( key):
    pList = key.ReadObj().GetListOfPrimitives()
    for pp in pList:
        if pp.ClassName() == "TH2F": return True
    return False

def compareTH2(TH21, TH22, varName, bins, outFile):
    outFile.cd()
    outFile.mkdir(varName)
    outFile.cd(varName)

    diffTH2 = ROOT.TH2F()
    diffTH2 = TH21.Clone()
    diffTH2.Add(TH22, -1)

    ## set abs. value
    for i, j in product( range(len(bins[0])-1), range(len(bins[1])-1) ):
        diffTH2.SetBinContent( i+1, j+1,
                               abs(diffTH2.GetBinContent(i+1, j+1))
        )

    diffTH2.SetTitle("2D SFs difference %s_muonID" % muonID)
    diffTH2.GetZaxis().SetRangeUser(0, 1)

    outCan = ROOT.TCanvas()
    outCan.cd()
    diffTH2.Draw("colz text error")
    outCan.Write()
    outCan.Print("%s/%s/2DSF_comparison_%s_%smuonID.pdf" % (MAINDIR, varName, varName, muonID), "pdf")
    

def compare2D(keys1, keys2, varName, bins, outFile):
    for kk1, kk2 in zip(keys1, keys2):
        if hasTH2(kk1):
            histo1 = kk1.ReadObj().GetListOfPrimitives()[1]
            histo2 = kk2.ReadObj().GetListOfPrimitives()[1]
            if not histo1.GetName()[:2] == "SF": continue
            compareTH2( TH21    = histo1 ,
                        TH22    = histo2 , 
                        varName = varName, 
                        bins    = bins   , 
                        outFile = outFile
            )
        else:
            etaRange = kk1.ReadObj().GetName()[ kk1.ReadObj().GetName().find("("):kk1.ReadObj().GetName().find(")")+1]
            etaRange = "|#eta| in %s" % etaRange
            compare1D( key1    = kk1 , 
                       key2    = kk2 , 
                       varName = varName, 
                       bins    = bins[0], 
                       outFile = outFile,
                       etaRange= etaRange
            )
## <<MAIN LOOP>>

for var in varList:
    ## get the keys
    try:
        keys1 = file1.GetDirectory(var[0]).GetListOfKeys()
        keys2 = file2.GetDirectory(var[0]).GetListOfKeys()
    except: continue    
    ##mkdirs
    if not os.path.exists(MAINDIR+"/"+var[0]): os.makedirs(MAINDIR+"/"+var[0])
    outFile.cd()
    outFile.mkdir(var[0])
    outFile.cd(var[0])
    ## 1D comparison
    if len(keys1) ==     1:
        compare1D( key1    = keys1[0], 
                   key2    = keys2[0], 
                   varName = var[0]  , 
                   bins    = var[1]  , 
                   outFile = outFile
        )
    else: 
        compare2D( keys1   = keys1 , 
                   keys2   = keys2 , 
                   varName = var[0], 
                   bins    = var[1], 
                   outFile = outFile
        )
outFile.Close()
