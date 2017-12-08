## NOTE: pt(eta) means first bin over pt and, in each pt bin, bin over eta (that is abseta list)
##       eta(pt) means first bin over eta and, in each eta bin, bin over pt (that is pt list)
import ROOT
import numpy as np
import sys, os
import json

from collections    import OrderedDict
from itertools      import product
from libs.drawRatioPlot  import printRatioGraphs
from cfg.cfg_getSFs import MAINDIR, useLogXforPt


sys.path.insert(0, os.environ['HOME'] + '/.local/lib/python2.6/site-packages')
import uncertainties as unc

## get binning tags
def getBinRange (i, bins):
    down =  str(bins[i])
    up   =  str(bins[i+1]) if (bins[i+1]) != 30.1234 else "1200"
    return down+","+up
def getBinLabel (i, bins):
    down =  str(bins[i])
    up   =  str(bins[i+1]) if (bins[i+1]) != 30.1234 else "1200"
    return down+"-"+up

## convert graph to histo and fill histogram of errors
def GraphToHisto (graph, histo, histoE):
    for i in range(graph.GetN()):
        histo.Fill(graph.GetX()[i], graph.GetY()[i])
        histoE.Fill(graph.GetX()[i], max(graph.GetErrorYhigh(i), graph.GetErrorYlow(i)))

## calculate 1D SFs
def getSFs_1D(daDir, mcDir, bins, var, outFile):
    logx = useLogXforPt if var == "pt" else False
    ## make the dir
    DIR = MAINDIR+"/%s" % var
    if not os.path.exists(DIR): os.makedirs(DIR)

    ## get the graphs from the canvas inside the directories

    graphDA = daDir.Get( daDir.GetListOfKeys()[0].GetName() ).GetPrimitive('hxy_fit_eff')
    graphMC = mcDir.Get( mcDir.GetListOfKeys()[0].GetName() ).GetPrimitive('hxy_fit_eff')

    ## histos for SFs and errors
    effHistoDA = ROOT.TH1F("hDA"  , "", len(bins)-1    , bins  )
    errHistoDA = ROOT.TH1F("eDA"  , "", len(bins)-1    , bins  )

    effHistoMC = ROOT.TH1F("hMC"  , "", len(bins)-1    , bins  )
    errHistoMC = ROOT.TH1F("eMC"  , "", len(bins)-1    , bins  )

    ## convert to histo
    GraphToHisto(graphDA, effHistoDA, errHistoDA)
    GraphToHisto(graphMC, effHistoMC, errHistoMC)

    ## create a structure for the json
    jStrucSF = OrderedDict()
    jStrucDA = OrderedDict()
    jStrucMC = OrderedDict()

    ## SFs list
    SFs = [
    ]

    ## get the SFs and their uncertanties
    for i in range(len(bins)-1):
        num = unc.ufloat(effHistoDA.GetBinContent(i+1), errHistoDA.GetBinContent(i+1))
        den = unc.ufloat(effHistoMC.GetBinContent(i+1), errHistoMC.GetBinContent(i+1))
        sf  = num/den if den.nominal_value != 0 else unc.ufloat(0, 0)

        SFs.append((sf, effHistoDA.GetXaxis().GetBinCenter(i+1)))

        ## fill the json structures
        jStrucSF[getBinRange(i, bins)] = {}
        jStrucSF[getBinRange(i, bins)]['value'] = sf.nominal_value  if sf.nominal_value != 0    else None
        jStrucSF[getBinRange(i, bins)]['error'] = sf.std_dev        if sf.std_dev != 0          else None

        jStrucDA[getBinRange(i, bins)] = {}
        jStrucDA[getBinRange(i, bins)]['value'] = num.nominal_value if num.nominal_value != 0   else None
        jStrucDA[getBinRange(i, bins)]['error'] = num.std_dev       if num.std_dev != 0         else None

        jStrucMC[getBinRange(i, bins)] = {}
        jStrucMC[getBinRange(i, bins)]['value'] = den.nominal_value if den.nominal_value != 0   else None
        jStrucMC[getBinRange(i, bins)]['error'] = den.std_dev       if den.std_dev != 0         else None
 
    ## print the graphs
    printRatioGraphs( daGraph = graphDA, 
                      mcGraph = graphMC, 
                      sfList  = SFs    , 
                      varName = var    ,
                      printDir= DIR    ,
                      logx    = logx   ,
    )

    return jStrucSF, jStrucDA, jStrucMC

def getSFs_2D(daDir, mcDir, bins, var, outFile):
    logx = useLogXforPt
    ## make the dir
    DIR = MAINDIR+"/%s" % var
    if not os.path.exists(DIR): os.makedirs(DIR)

    ## define the bins 
    ptBins     = bins[0]
    absetaBins = bins[1]

    ## get list of keys
    keysMC = list(daDir.GetListOfKeys())
    keysDA = list(mcDir.GetListOfKeys())

    ## the lists will contain the graphs 
    ptGraphList = [
    ]

    ## fill the graphs
    for daK, mcK in zip(keysMC, keysDA):
        keyNameDA = daK.GetName()
        keyNameMC = mcK.GetName()

        ## get the graphs ad hoc
        if keyNameDA.split("_")[0] == "pt" and keyNameDA.split("_")[1] == "PLOT":
            ptGraphList.append( (daDir.Get(keyNameDA).GetPrimitive("hxy_fit_eff"),
                                 mcDir.Get(keyNameMC).GetPrimitive("hxy_fit_eff"))
                        )

    ## define the matrix (TH2F) that will contain the SFs and efficiencies
    SFsHisto = ROOT.TH2F("SFpt(eta)", "SFs for pt(eta)  -  %s muonID"    % str(sys.argv[1]), len(ptBins)-1, 0, len(ptBins)-1, len(absetaBins)-1, 0, len(absetaBins-1))
    daEHisto = ROOT.TH2F("DApt(eta)", "Data efficiencies   -  %s muonID" % str(sys.argv[1]), len(ptBins)-1, 0, len(ptBins)-1, len(absetaBins)-1, 0, len(absetaBins-1))
    mcEHisto = ROOT.TH2F("MCpt(eta)", "MC efficiencies  -  %s muonID"    % str(sys.argv[1]), len(ptBins)-1, 0, len(ptBins)-1, len(absetaBins)-1, 0, len(absetaBins-1))

    SFsHisto.GetXaxis().SetTitle("pt [GeV]")
    SFsHisto.GetYaxis().SetTitle("abseta")
    daEHisto.GetXaxis().SetTitle("pt [GeV]")
    daEHisto.GetYaxis().SetTitle("abseta")
    mcEHisto.GetXaxis().SetTitle("pt [GeV]")
    mcEHisto.GetYaxis().SetTitle("abseta")

    SFsHisto.GetXaxis().SetTitleOffset( 1.3*SFsHisto.GetTitleOffset())
    daEHisto.GetXaxis().SetTitleOffset( 1.3*daEHisto.GetTitleOffset())
    mcEHisto.GetXaxis().SetTitleOffset( 1.3*mcEHisto.GetTitleOffset())


    ## set the labels 
    for i in range( (len(absetaBins)-1)):
        SFsHisto.GetYaxis().SetBinLabel(i+1, getBinLabel(i, absetaBins))
        daEHisto.GetYaxis().SetBinLabel(i+1, getBinLabel(i, absetaBins))
        mcEHisto.GetYaxis().SetBinLabel(i+1, getBinLabel(i, absetaBins))
    for i in range( (len(ptBins)-1)):
        SFsHisto.GetXaxis().SetBinLabel(i+1, getBinLabel(i, ptBins))
        daEHisto.GetXaxis().SetBinLabel(i+1, getBinLabel(i, ptBins))
        mcEHisto.GetXaxis().SetBinLabel(i+1, getBinLabel(i, ptBins))

    for i, couple in enumerate(ptGraphList):
        ## define some auxiliary TH1 INSIDE to force a bin reset
        ## otherwise ROOT gets crazy
        daEffH = ROOT.TH1F("effDA", "", len(ptBins)-1, ptBins)
        mcEffH = ROOT.TH1F("effMC", "", len(ptBins)-1, ptBins)    
        EdaEffH = ROOT.TH1F("ErreffDA", "", len(ptBins)-1, ptBins)
        EmcEffH = ROOT.TH1F("ErreffMC", "", len(ptBins)-1, ptBins)
        ## convert the graphs
        GraphToHisto(couple[0], daEffH, EdaEffH)
        GraphToHisto(couple[1], mcEffH, EmcEffH)
        ## get the SFs
        SFs = [
        ]
        for j in range( len(ptBins)-1):
            num = unc.ufloat(daEffH.GetBinContent(j+1), EdaEffH.GetBinContent(j+1))
            den = unc.ufloat(mcEffH.GetBinContent(j+1), EmcEffH.GetBinContent(j+1))
            sf  = num/den if den.nominal_value != 0 else unc.ufloat(0, 0)
            SFs.append((sf, daEffH.GetXaxis().GetBinCenter(j+1)))

            SFsHisto.SetBinContent(j+1, i+1, sf.nominal_value)
            SFsHisto.SetBinError(j+1, i+1, sf.std_dev)

            daEHisto.SetBinContent(j+1, i+1, num.nominal_value)
            daEHisto.SetBinError(j+1, i+1, num.std_dev)

            mcEHisto.SetBinContent(j+1, i+1, den.nominal_value)
            mcEHisto.SetBinError(j+1, i+1, den.std_dev)
        ## print the graphs
        label = "|#eta| in (%s)   -   pT [GeV]"  % str(getBinLabel(i, absetaBins))
        printRatioGraphs( daGraph = couple[0], 
                          mcGraph = couple[1], 
                          sfList  = SFs   , 
                          varName = label ,
                          printDir= DIR   ,
                          logx    = logx  ,
        )
        
    ## print the 2D histos
    c1 = ROOT.TCanvas()
    c2 = ROOT.TCanvas()
    c3 = ROOT.TCanvas()

    c1.cd() ; SFsHisto.Draw("colz2 text error")
    c2.cd() ; daEHisto.Draw("colz2 text error")
    c3.cd() ; mcEHisto.Draw("colz2 text error")

    c1.Print("%s/Ratio_%s.pdf"    % (DIR, str(sys.argv[1])), "pdf") ; c1.Write()
    c2.Print("%s/DataEff_%s.pdf"  % (DIR, str(sys.argv[1])), "pdf") ; c2.Write()
    c3.Print("%s/MCEff_%s.pdf"    % (DIR, str(sys.argv[1])), "pdf") ; c3.Write()

    ## create the Json structures
    jsonStrucSF = OrderedDict()
    jsonStrucMC = OrderedDict()
    jsonStrucDA = OrderedDict()

    ## fill the structures
    for i in range( len(absetaBins)-1):
       jsonStrucSF[getBinRange(i, absetaBins)] = OrderedDict()
       jsonStrucMC[getBinRange(i, absetaBins)] = OrderedDict()
       jsonStrucDA[getBinRange(i, absetaBins)] = OrderedDict()
       for j in range( len(ptBins)-1):
           jsonStrucSF[getBinRange(i, absetaBins)][getBinRange(j, ptBins)] = {}
           jsonStrucMC[getBinRange(i, absetaBins)][getBinRange(j, ptBins)] = {}
           jsonStrucDA[getBinRange(i, absetaBins)][getBinRange(j, ptBins)] = {}

           jsonStrucSF[getBinRange(i, absetaBins)][getBinRange(j, ptBins)]['value'] = SFsHisto.GetBinContent(j+1, i+1)  if SFsHisto.GetBinContent(j+1, i+1) != 0 else None
           jsonStrucMC[getBinRange(i, absetaBins)][getBinRange(j, ptBins)]['value'] = mcEHisto.GetBinContent(j+1, i+1)  if mcEHisto.GetBinContent(j+1, i+1) != 0 else None
           jsonStrucDA[getBinRange(i, absetaBins)][getBinRange(j, ptBins)]['value'] = daEHisto.GetBinContent(j+1, i+1)  if daEHisto.GetBinContent(j+1, i+1) != 0 else None

           jsonStrucSF[getBinRange(i, absetaBins)][getBinRange(j, ptBins)]['error'] = SFsHisto.GetBinError(j+1, i+1) if SFsHisto.GetBinError(j+1, i+1) != 0 else None
           jsonStrucMC[getBinRange(i, absetaBins)][getBinRange(j, ptBins)]['error'] = mcEHisto.GetBinError(j+1, i+1) if mcEHisto.GetBinError(j+1, i+1) != 0 else None
           jsonStrucDA[getBinRange(i, absetaBins)][getBinRange(j, ptBins)]['error'] = daEHisto.GetBinError(j+1, i+1) if daEHisto.GetBinError(j+1, i+1) != 0 else None

    return jsonStrucSF, jsonStrucDA, jsonStrucMC