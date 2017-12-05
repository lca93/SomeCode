#######################################################################
## 5 Dec. 2017
## 
## the codes reads the root files created by the CMS TnP code
## and calculates the SFs 1D from the efficiencies saved in those fils
##
## OUTPUT:
## -SFs json 
## -MC eff. json
## -Data eff. json
######
import sys, os
import ROOT
import numpy as np
import json

from collections import OrderedDict

sys.path.insert(0, os.environ['HOME'] + '/.local/lib/python2.6/site-packages')
import uncertainties as unc

## get binning tags
def getBinRange (i, bins):
    return str(bins[i])+","+str(bins[i+1])

## convert graph to histo and fill histogram of errors
def GraphToHisto (graph, histo, histoE):
    for i in range(graph.GetN()):
        histo.Fill(graph.GetX()[i], graph.GetY()[i])
        histoE.Fill(graph.GetX()[i], max(graph.GetErrorYhigh(i), graph.GetErrorYlow(i)))

##print the graphs
def PrintGraphs (daGraph, mcGraph, sfList, varName):
    ##root sucks
    daGraph.SetPointEXhigh(daGraph.GetN()-1, 0)
    daGraph.SetPointEXlow(daGraph.GetN()-1, 0)
    mcGraph.SetPointEXhigh(mcGraph.GetN()-1, 0)
    mcGraph.SetPointEXlow(mcGraph.GetN()-1, 0)

    daGraph.SetPointEXhigh(0, 0)
    daGraph.SetPointEXlow(0, 0)
    mcGraph.SetPointEXhigh(0, 0)
    mcGraph.SetPointEXlow(0, 0)
    logx = False
    if varName == "pt": logx = True
    ## root sucks
    supportEff = ROOT.TH1F("suppE", "", len(sfList), sfList[0][1], sfList[-1][1]*1.1)
    supportRat = ROOT.TH1F("suppR", "", len(sfList), sfList[0][1], sfList[-1][1]*1.1)
    ## create the legend
    legPad = ROOT.TLegend(0.7, 0.35, 0.85, 0.25)
    legPad.AddEntry(daGraph, "Data", "lp")
    legPad.AddEntry(mcGraph, "MC"  , "lp")
    ## set up the gaphs
    multiG = ROOT.TMultiGraph()
    multiG.SetTitle("SFs - %s muon ID; %s; efficiency" % (str(sys.argv[1]), varName))
    multiG.Add(daGraph)
    multiG.Add(mcGraph)
    mcGraph.SetLineColor(ROOT.kBlue)
    daGraph.SetLineColor(ROOT.kRed)
    mcGraph.SetMarkerStyle(20)
    daGraph.SetMarkerStyle(22)
    mcGraph.SetMarkerColor(ROOT.kBlue)
    daGraph.SetMarkerColor(ROOT.kRed)
    ## create the SF graph
    sfGraph = ROOT.TGraphErrors()
    sfGraph.SetMarkerColor(ROOT.kBlack)
    sfGraph.SetLineColor(ROOT.kBlack)
    sfGraph.SetMarkerStyle(8)    
    sfGraph.SetFillStyle(3004)
    sfGraph.SetFillColor(ROOT.kBlack)
    for i in range(len(sfList)):
        sfGraph.SetPoint( i, 
                          sfList[i][1],
                          sfList[i][0].nominal_value
        )
        sfGraph.SetPointError( i, 
                               0,
                               sfList[i][0].std_dev
        )
    ## draw 
    outCan = ROOT.TCanvas("outCan", "", 700, 1000)
    outCan.Draw()
    outCan.cd()

    supPad = ROOT.TPad('effPad', 'effPad', 0., 0.3, 1., 1., 0, 0)
    supPad.Draw()
    supPad.cd()
    supPad.SetGridy(True)
    supPad.SetBottomMargin(0.2)
    supPad.SetLogx(logx)
    
    
    supportEff.Draw()
    multiG.SetMaximum(1.1*ROOT.TMath.MaxElement( mcGraph.GetN(), mcGraph.GetY())) 
    multiG.SetMinimum(0)
    multiG.Draw("same p")
    multiG.GetXaxis().SetLimits(sfList[0][1], sfList[-1][1]*1.1)
    legPad.Draw("same")

    supPad.Update()

    outCan.cd()

    infPad = ROOT.TPad('ratioPad', 'ratioPad', 0., 0.32, 1, .0, 0, 0)
    infPad.Draw()
    infPad.cd()
    infPad.SetGridx(True)
    infPad.SetGridy(True)
    infPad.SetBottomMargin(0.2)
    infPad.SetLogx(logx)

    supportRat.Draw()

    supportRat.GetYaxis().SetRangeUser( 0.9*min(sfList)[0].nominal_value,
                                        1.1*max(sfList)[0].nominal_value
    )
    sfGraph.GetXaxis().SetLimits(sfList[0][1], sfList[-1][1]*1.1)
    sfGraph.Draw("PLE3")

    infPad.Update()

    outCan.Update()
    import pdb ; pdb.set_trace()

## set up root
ROOT.gStyle.SetOptStat(0)
#ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")
ROOT.TH1.SetDefaultSumw2()

## debug canvas
pdbCan = ROOT.TCanvas(); pdbCan.cd()

## get the input files
fileDA = ROOT.TFile.Open("../root_files/data/data_%s.root" % str(sys.argv[1]))
fileMC = ROOT.TFile.Open("../root_files/mc/mc_%s.root"     % str(sys.argv[1]))

## some definitions
mainKey = "%s_muonID" % str(sys.argv[1])

printGraphs = False if len(sys.argv)>2                  and\
                        (str(sys.argv[2]) == "False"    or \
                         str(sys.argv[2]) == "false"      )\
                    else True

ptBins     = np.array([2., 2.5, 2.75, 3., 3.25, 3.5, 3.75, 4., 4.5, 5., 6., 8., 10., 15., 20., 30.])
etaBins    = np.array([-2.4, -2.1, -1.6, -1.2, -0.9, -0.3, -0.2, 0.2, 0.3, 0.9, 1.2, 1.6, 2.1, 2.4])
nVtxBins   = np.array([0.5,2.5,4.5,6.5,8.5,10.5,12.5,14.5,16.5,18.5,20.5,22.5,24.5,26.5,28.5,30.5,32.5,34.5,36.5,38.5,40.5,42.5,44.5,46.5,48.5,50.5])

varList =[  ("pt"   , ptBins  ),
            ("eta"  , etaBins ),
            ("nVtx" , nVtxBins),
]

## json files
jsonFileSF  = open("ScaleFactors_%s.json"      % mainKey, "w")
jsonFileDA  = open("Efficiencies_%s_DATA.json" % mainKey, "w")
jsonFileMC  = open("Efficiencies_%s_MC.json"   % mainKey, "w")

## create json structures
jsonStrucSF = OrderedDict()
jsonStrucDA = OrderedDict()
jsonStrucMC = OrderedDict()
jsonStrucSF[mainKey] = OrderedDict()
jsonStrucDA[mainKey] = OrderedDict()
jsonStrucMC[mainKey] = OrderedDict()

def getSFs (var, bins):
    ## directory containing the efficiency plots
    plotDirDA = fileDA.GetDirectory("tpTree/eff_%s/fit_eff_plots" % var)
    plotDirMC = fileMC.GetDirectory("tpTree/eff_%s/fit_eff_plots" % var)

    ##get the graphs from the canvas inside the directories
    ## NOTE works only with 1 canvas, i.e. 1D SFs
    graphDA = plotDirDA.Get( plotDirDA.GetListOfKeys()[0].GetName() ).GetPrimitive('hxy_fit_eff')
    graphMC = plotDirMC.Get( plotDirMC.GetListOfKeys()[0].GetName() ).GetPrimitive('hxy_fit_eff')

    ## histos for SFs and errors
    effHistoDA = ROOT.TH1F("hDA"  , "", len(bins)-1    , bins  )
    errHistoDA = ROOT.TH1F("eDA"  , "", len(bins)-1    , bins  )

    effHistoMC = ROOT.TH1F("hMC"  , "", len(bins)-1    , bins  )
    errHistoMC = ROOT.TH1F("eMC"  , "", len(bins)-1    , bins  )

    ## convert to histo
    GraphToHisto(graphDA, effHistoDA, errHistoDA)
    GraphToHisto(graphMC, effHistoMC, errHistoMC)

    ## create a structure for the json
    jStrucSF = {}
    jStrucDA = {}
    jStrucMC = {}

    ## SFs list
    SFs = [
    ]

    ## get the SFs and their uncertanties
    for i in range(len(bins)-1):
        num = unc.ufloat(effHistoDA.GetBinContent(i+1), errHistoDA.GetBinContent(i+1))
        den = unc.ufloat(effHistoMC.GetBinContent(i+1), errHistoMC.GetBinContent(i+1))
        sf  = num/den

        SFs.append((sf, effHistoDA.GetXaxis().GetBinCenter(i+1)))

        ## fill the json structures
        jStrucSF[getBinRange(i, bins)] = {}
        jStrucSF[getBinRange(i, bins)]['value'] = str(sf.nominal_value)   
        jStrucSF[getBinRange(i, bins)]['error'] = str(sf.std_dev)   

        jStrucDA[getBinRange(i, bins)] = {}
        jStrucDA[getBinRange(i, bins)]['value'] = str(num.nominal_value)    
        jStrucDA[getBinRange(i, bins)]['error'] = str(num.std_dev)  

        jStrucMC[getBinRange(i, bins)] = {}
        jStrucMC[getBinRange(i, bins)]['value'] = str(den.nominal_value)    
        jStrucMC[getBinRange(i, bins)]['error'] = str(den.std_dev)  
 
    ## print the graphs
    if printGraphs: PrintGraphs(graphDA, graphMC, SFs, var)

    return jStrucSF, jStrucDA, jStrucMC

## <MAIN LOOP>
for vv in varList:
    struc = getSFs(vv[0], vv[1])
    jsonStrucSF[mainKey][vv[0]] = struc[0]
    jsonStrucDA[mainKey][vv[0]] = struc[1]
    jsonStrucMC[mainKey][vv[0]] = struc[2]

##create the json object
jsonObjSF = json.dumps(jsonStrucSF, indent=4, sort_keys=False)
jsonObjDA = json.dumps(jsonStrucDA, indent=4, sort_keys=False)
jsonObjMC = json.dumps(jsonStrucMC, indent=4, sort_keys=False)

## write the json object to file
jsonFileSF.write(jsonObjSF)
jsonFileDA.write(jsonObjDA)
jsonFileMC.write(jsonObjMC)