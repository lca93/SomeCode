## NOTE: pt(eta) means first bin over pt and, in each pt bin, bin over eta (that is abseta list)
##       eta(pt) means first bin over eta and, in each eta bin, bin over pt (that is pt list)

import ROOT
import numpy as np
import sys, os
import json

from collections    import OrderedDict
from drawRatioPlot  import PrintGraphs

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

## calculate 1D SFs
def getSFs_1D(plotDirDA, plotDirMC, bins, var, printGraphs):
    ## get the graphs from the canvas inside the directories
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
    if printGraphs: 
        print "     printing graphs"
        PrintGraphs(graphDA, graphMC, SFs, var)

    return jStrucSF, jStrucDA, jStrucMC

def getSFs_2D(daDir, mcDir, bins):
    ## define the bins
    ptBins     = bins[0]
    absetaBins = bins[1]

    ## get list of keys
    keysMC = list(daDir.GetListOfKeys())
    keysDA = list(mcDir.GetListOfKeys())

    ## the lists will contain the graphs 
    absetaGraphList =[
    ]
    ptGraphList = [
    ]

    ## fill the graphs
    for daK, mcK in zip(keysMC, keysDA):
        keyNameDA = daK.GetName()
        keyNameMC = mcK.GetName()

        ## get the graphs ad hoc
        if keyNameDA.split("_")[0] == "abseta" and keyNameDA.split("_")[1] == "PLOT":
            absetaGraphList.append(  (daDir.Get(keyNameDA).GetPrimitive("hxy_fit_eff"),
                                     mcDir.Get(keyNameMC).GetPrimitive("hxy_fit_eff"))
                            )
        elif keyNameDA.split("_")[0] == "pt" and keyNameDA.split("_")[1] == "PLOT":
            ptGraphList.append( (daDir.Get(keyNameDA).GetPrimitive("hxy_fit_eff"),
                                 mcDir.Get(keyNameMC).GetPrimitive("hxy_fit_eff"))
                        )
        else:
            pass

    ## define the matrix (TH2F) that will contain the SFs
    ## NOTE: pt(eta) means first bin over pt and, in each pt bin, bin over eta (that is abseta list)
    ##       eta(pt) means first bin over eta and, in each eta bin, bin over pt (that is pt list)
    pt_eta_H = ROOT.TH2F("pt(eta)", "SFs for pt(eta)  -  %s muonID" % str(sys.argv[1]), 15, 0, 15, 4, 0, 4)
    eta_pt_H = ROOT.TH2F("pt(eta)", "SFs for eta(pt)  -  %s muonID" % str(sys.argv[1]), 15, 0, 15, 4, 0, 4)

    pt_eta_H.GetXaxis().SetTitle("pt [GeV]")
    pt_eta_H.GetYaxis().SetTitle("abseta")
    eta_pt_H.GetXaxis().SetTitle("pt [GeV]")
    eta_pt_H.GetYaxis().SetTitle("abseta")

    ## fill the TH2 with the SFs
    ## couple[0] = data
    ## couple[1] = mc
        ## pt(eta)
    for i, couple in enumerate(absetaGraphList):
        ## define TH1s to correctly read the graphs
        daEffH = ROOT.TH1F("effDA", "", len(absetaBins)-1, absetaBins)
        mcEffH = ROOT.TH1F("effMC", "", len(absetaBins)-1, absetaBins)
            ## errors
        EdaEffH = ROOT.TH1F("EeffDA", "", len(absetaBins)-1, absetaBins)
        EmcEffH = ROOT.TH1F("EeffMC", "", len(absetaBins)-1, absetaBins)

        ## convert the graphs
        GraphToHisto(couple[0], daEffH, EdaEffH)
        GraphToHisto(couple[1], mcEffH, EmcEffH)

        ## get the SFs
        for j in range( len(absetaBins)-1):
            num = unc.ufloat(daEffH.GetBinContent(j+1), EdaEffH.GetBinContent(j+1))
            den = unc.ufloat(mcEffH.GetBinContent(j+1), EmcEffH.GetBinContent(j+1))
            sf  = num/den if den.nominal_value != 0 else unc.ufloat(0, 0)
            
            pt_eta_H.SetBinContent(i+1, j+1, sf.nominal_value)
            pt_eta_H.SetBinError(i+1, j+1, sf.std_dev)
        ## eta(pt)
    for i, couple in enumerate(ptGraphList):
        ## define TH1s to correctly read the graphs
        daEffH = ROOT.TH1F("effDA", "", len(ptBins)-1, ptBins)
        mcEffH = ROOT.TH1F("effMC", "", len(ptBins)-1, ptBins)
            ## errors
        EdaEffH = ROOT.TH1F("EeffDA", "", len(ptBins)-1, ptBins)
        EmcEffH = ROOT.TH1F("EeffMC", "", len(ptBins)-1, ptBins)

        ## convert the graphs
        GraphToHisto(couple[0], daEffH, EdaEffH)
        GraphToHisto(couple[1], mcEffH, EmcEffH)

        ## get the SFs
        for j in range( len(ptBins)-1):
            num = unc.ufloat(daEffH.GetBinContent(j+1), EdaEffH.GetBinContent(j+1))
            den = unc.ufloat(mcEffH.GetBinContent(j+1), EmcEffH.GetBinContent(j+1))
            sf  = num/den if den.nominal_value != 0 else unc.ufloat(0, 0)
                        
            eta_pt_H.SetBinContent(i+1, j+1, sf.nominal_value)
            eta_pt_H.SetBinError(i+1, j+1, sf.std_dev)

    import pdb ; pdb.set_trace()
