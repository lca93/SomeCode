###############################################################################################
## 23 november 2017
##
## The code reads TnP results and computes 2D ptxabseta scale factors. Also saves some canvas
##
import ROOT, math
import sys, os, subprocess

## propagate error on ratio
## (data error, mc error, data efficiency, mc efficiency)
def ErrorRatio(eDat, eMC, effData, effMC):
    if effMC == 0: return 0
    part1 = (1./effMC)**2 * eDat**2    
    part2 = (effData/effMC**2)**2 * eMC **2
    return math.sqrt( part1 + part2 )

# return bin range as string
def getBinRange (i, bins):
    return str(bins[i])+"-"+str(bins[i+1])
    
## set up root. NOTE batch for faster code
ROOT.gStyle.SetOptStat(0000)
ROOT.gStyle.SetPaintTextFormat(".3f")
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")

## some defs
ptBin     = np.array([2., 2.5, 2.75, 3., 3.25, 3.5, 3.75, 4., 4.5, 5., 6., 8., 10., 15., 20., 30.])
etaBin    = np.array([0, 0.9, 2.1, 2.4])

## path variables
DIR  = "/afs/cern.ch/work/l/lguzzi/CMSSW_8_0_25/src/MuonAnalysis/all_together/Eff/2DPlots/" + str(sys.argv[1])
MC   = "mc_"+str(sys.argv[1])+".root"
DATA = "data_"+str(sys.argv[1])+".root"
PATH = "/afs/cern.ch/work/l/lguzzi/CMSSW_8_0_25/src/MuonAnalysis/all_together/root_files"
Data_path   = PATH+"/data/"+DATA
MC_path     = PATH+"/mc/"+MC

## make all necessary directories
if not os.path.exists("/afs/cern.ch/work/l/lguzzi/CMSSW_8_0_25/src/MuonAnalysis/all_together/Eff/2DPlots/"): os.makedirs("/afs/cern.ch/work/l/lguzzi/CMSSW_8_0_25/src/MuonAnalysis/all_together/Eff/2DPlots/")
if not os.path.exists(DIR): os.makedirs(DIR)
if not os.path.exists(DIR+"/bin_fits"): os.makedirs(DIR+"/bin_fits")
if not os.path.exists(DIR+"/bin_fits/mc"): os.makedirs(DIR+"/bin_fits/mc")
if not os.path.exists(DIR+"/bin_fits/data"): os.makedirs(DIR+"/bin_fits/data")
if not os.path.exists(DIR+"/efficiencies"): os.makedirs(DIR+"/efficiencies")
if not os.path.exists(DIR+"/efficiencies/pt_bins"): os.makedirs(DIR+"/efficiencies/pt_bins")
if not os.path.exists(DIR+"/efficiencies/eta_bins"): os.makedirs(DIR+"/efficiencies/eta_bins")

## files
outFile     = ROOT.TFile(DIR+"/"+str(sys.argv[1])+".root", "RECREATE")
MC_file     = ROOT.TFile.Open(MC_path)
Data_file   = ROOT.TFile.Open(Data_path)

## auxiliar canvases
c = ROOT.TCanvas()
c2= ROOT.TCanvas()

## some feedback
print
print "Data FILE        " + Data_path
print "MC   FILE        " + MC_path
print

## histos
effHistoData = ROOT.TH2F("effdata", "Data efficiencies"+str(sys.argv[1]), 15, 0, 15, 4, 0, 4)
effHistoMC = ROOT.TH2F("effmc", "MC efficiencies"+str(sys.argv[1]), 15, 0, 15, 4, 0, 4) 

ratHisto    = ROOT.TH2F("rat", "Data/MC ratios  "+str(sys.argv[1]), 15, 0, 15, 4, 0, 4)
ratHistoErr = ROOT.TH2F("ratErr", "Data/MC ratios errors (indicative)  "+str(sys.argv[1]), 15, 0, 15, 4, 0, 4)

effHistoErrMC   = ROOT.TH2F("EffmcErr", "MC eff. errors (indicative)", 15, 0, 15, 4, 0, 4)
effHistoErrData = ROOT.TH2F("EffdataErr", "Data eff. errors (indicative)", 15, 0, 15, 4, 0, 4)

## set mc histo
effHistoMC.GetZaxis().SetRangeUser(-.01, 1)
effHistoMC.GetXaxis().SetTitle("pt [GeV]")
effHistoMC.GetYaxis().SetTitle("abseta")

## set bin labels
for i in range( len(ptBin)):
    effHistoMC.GetXaxis().SetBinLabel(i+1, getBinRange(i, ptBin))
    effHistoData.GetXaxis().SetBinLabel(i+1, getBinRange(i, ptBin))
    ratHisto.GetXaxis().SetBinLabel(i+1, getBinRange(i, ptBin))
    ratHistoErr.GetXaxis().SetBinLabel(i+1, getBinRange(i, ptBin))

for i in range( len(etaBin)):
    effHistoMC.GetYaxis().SetBinLabel(i+1, getBinRange(i, etaBin))
    effHistoData.GetYaxis().SetBinLabel(i+1, getBinRange(i, etaBin))
    ratHisto.GetYaxis().SetBinLabel(i+1, getBinRange(i, etaBin))
    ratHistoErr.GetYaxis().SetBinLabel(i+1, getBinRange(i, etaBin))

## get the efficiency plots
##      Different bins are saved in different plots, so loop over pt bins.
##      Efficiency are organized in pt bins with 4 eta points AND eta bins with 15 pt points
##      To get the correct information: open pt bin
##                                      fill ptVSeta
## 
##          15 pt bins:     (2, 2.5, 2.75, 3, 3.25, 3.5, 3.75, 4, 4.5, 5, 6, 8, 10, 15, 20, 1200)    
##          4 abseta bins:  (0, 0.9, 1.2, 2.1, 2.4)
##

## loop over pt binning
print "     working..."
for i in range(15):
    ## get the graphs
    MC_dir       = MC_file.GetDirectory("tpTree/eff_pt_abseta/fit_eff_plots")
    MC_can       = MC_dir.Get("abseta_PLOT_pt_bin%d_&_Mu7p5_Track2_Jpsi_TK_pass_&_tag_Mu7p5_MU_pass_&_tag_Mu7p5_Track2_Jpsi_MU_pass" %i)
    MC_graph     = MC_can.GetPrimitive("hxy_fit_eff")
    Data_dir     = Data_file.GetDirectory("tpTree/eff_pt_abseta/fit_eff_plots")
    Data_can     = Data_dir.Get("abseta_PLOT_pt_bin%d_&_Mu7p5_Track2_Jpsi_TK_pass_&_tag_Mu7p5_MU_pass_&_tag_Mu7p5_Track2_Jpsi_MU_pass" %i)
    Data_graph   = Data_can.GetPrimitive("hxy_fit_eff")

    ## get MC points
    for jj in range(MC_graph.GetN()):
        ## declare x, y, erry inside jj loop to force new memory allocation at each loop
        x = ROOT.Double(0.)
        y = ROOT.Double(0.)
        erry = ROOT.Double(0.)

        MC_graph.GetPoint(jj, x, y)
        ## will only propagate the biggest error (indicative)
        erry = max(MC_graph.GetErrorYhigh(jj), MC_graph.GetErrorYlow(jj))

        ## what eta bin is this? (Some eta points are missing due to low statistics)
        if   x >=0 and x <0.9:
            effHistoMC.SetBinContent(i+1, 1, y)
            effHistoErrMC.SetBinContent(i+1, 1, erry)

        elif x >=0.9 and x <1.2:
            effHistoMC.SetBinContent(i+1, 2, y)
            effHistoErrMC.SetBinContent(i+1, 2, erry)

        elif x >=1.2 and x <2.1:
            effHistoMC.SetBinContent(i+1, 3, y)
            effHistoErrMC.SetBinContent(i+1, 3, erry) 

        elif x >=2.1 and x <=2.4:
            effHistoMC.SetBinContent(i+1, 4, y)
            effHistoErrMC.SetBinContent(i+1, 4, erry)

        else: 
            print ("ERROR importing MC value for eta = %d, pt_bin = %d" %MC_x %i)

    ## see MC loop
    for jj in range(Data_graph.GetN()):
        x = ROOT.Double(0.)
        y = ROOT.Double(0.)
        erry = ROOT.Double(0.)

        Data_graph.GetPoint(jj, x, y)
        erry = max(Data_graph.GetErrorYhigh(jj), Data_graph.GetErrorYlow(jj))

        if   x >=0 and x <0.9:
            effHistoData.SetBinContent(i+1, 1, y)
            effHistoErrData.SetBinContent(i+1, 1, erry)

        elif x >=0.9 and x <1.2:
            effHistoData.SetBinContent(i+1, 2, y)
            effHistoErrData.SetBinContent(i+1, 2, erry)

        elif x >=1.2 and x <2.1:
            effHistoData.SetBinContent(i+1, 3, y) 
            effHistoErrData.SetBinContent(i+1, 3, erry)

        elif x >=2.1 and x <=2.4:
            effHistoData.SetBinContent(i+1, 4, y)
            effHistoErrData.SetBinContent(i+1, 4, erry)
            
        else: 
            print ("error importing Data value for eta = %d, pt_bin = %d" %MC_x %i)
## get the ratios
for ii in range (1, 16):
    for jj in range(1, 5):
        effData = effHistoData.GetBinContent(ii, jj)
        effMC   = effHistoMC.GetBinContent(ii, jj)

        ratio = effData/effMC if effMC != 0 else 0.
        ratHisto.SetBinContent(ii, jj, ratio)

        ## error propagation
        error = math.sqrt( (1./effMC)**2 * effHistoErrData.GetBinContent(ii, jj)**2 + (effData/effMC**2)**2 * effHistoErrMC.GetBinContent(ii, jj) **2) if effMC != 0 else 0
        ratHisto.SetBinError(ii, jj, error)
        ratHistoErr.SetBinContent(ii, jj, error)

## save results in root file

## make dirs all here
outFile.cd()
outFile.mkdir("results")                ## efficiencies and ratios
outFile.mkdir("bin_fits")            
outFile.mkdir("bin_fits/mc")            ## mc fits imported from input
outFile.mkdir("bin_fits/data")          ## data fits imported from input
outFile.mkdir("efficiencies")       
outFile.mkdir("efficiencies/pt_bins")   ## efficiencies binned for pt
outFile.mkdir("efficiencies/eta_bins")  ## efficiencies binned for eta

## write the results and print some canvas
outFile.cd("results")

effHistoMC.Write()
effHistoData.Write()
effHistoErrMC.Write()
effHistoErrData.Write()
ratHisto.Write()
ratHistoErr.Write()

c.cd()
effHistoMC.Draw("colz2 text")   ; c.Print(DIR+"/MC_efficiency.pdf", "pdf")
effHistoData.Draw("colz2 text") ; c.Print(DIR+"/Data_efficiency.pdf", "pdf")
ratHisto.Draw("colz2 text error")     ; c.Print(DIR+"/Ratio.pdf", "pdf")
c.SetLogz() ## set logarithmic scal for errors
ratHistoErr.Draw("colz2 text")  ; c.Print(DIR+"/Ratio_errors.pdf", ".pdf")

## write and print fit results
outFile.cd("bin_fits/mc")
## import MC bin fits (loop over eta and pt)
for ii in range (4):
    for jj in range(15):
        MC_dir   = MC_file  .GetDirectory("tpTree/eff_pt_abseta/abseta_bin%d__pair_drM1_bin0__pair_probeMultiplicity_bin0__pt_bin%d__tag_abseta_bin0__tag_pt_bin0__Mu7p5_Track2_Jpsi_TK_pass__tag_Mu7p5_MU_pass__tag_Mu7p5_Track2_Jpsi_MU_pass__vpvPlusExpo" % (ii, jj))
        ## some fits fails and canvases are empty. Write a dummy
        try:
            MC_can      = MC_dir  .Get("fit_canvas")
            MC_can  .SetName("MC__pt_bin"+str(jj)+"__eta_bin"+str(ii))
        except:
            MC_can = ROOT.TCanvas("MC__pt_bin"+str(jj)+"__eta_bin"+str(ii), "dummyMCcanvas pt_bin"+str(jj)+"__eta_bin"+str(ii))
        MC_can.Write()
        MC_can.Print(DIR+"/bin_fits/mc/"+MC_can.GetName()+".pdf", "pdf")
## import data bin fits (see MC above)
outFile.cd("bin_fits/data")
for ii in range (4):
    for jj in range(15):
        Data_dir = Data_file.GetDirectory("tpTree/eff_pt_abseta/abseta_bin%d__pair_drM1_bin0__pair_probeMultiplicity_bin0__pt_bin%d__tag_abseta_bin0__tag_pt_bin0__Mu7p5_Track2_Jpsi_TK_pass__tag_Mu7p5_MU_pass__tag_Mu7p5_Track2_Jpsi_MU_pass__vpvPlusExpo" % (ii, jj))
        
        try:   
            Data_can    = Data_dir.Get("fit_canvas")
            Data_can.SetName("Data__pt_bin"+str(jj)+"__eta_bin"+str(ii))
        except:
            Data_can = ROOT.TCanvas("Data__pt_bin"+str(jj)+"__eta_bin"+str(ii), "dummyMCcanvas pt_bin"+str(jj)+"__eta_bin"+str(ii))
        Data_can.Write()
        Data_can.Print(DIR+"/bin_fits/data/"+Data_can.GetName()+".pdf", "pdf")

## import pt binned efficiency plots
## save MC and data on same canvas
outFile.cd("efficiencies/pt_bins")
for ii in range(15):
    ## get the graphs
    Data_dir = Data_file.GetDirectory("tpTree/eff_pt_abseta/fit_eff_plots")
    Data_can = Data_dir.Get("abseta_PLOT_pt_bin%d_&_Mu7p5_Track2_Jpsi_TK_pass_&_tag_Mu7p5_MU_pass_&_tag_Mu7p5_Track2_Jpsi_MU_pass" %ii)
    MC_dir = MC_file.GetDirectory("tpTree/eff_pt_abseta/fit_eff_plots")
    MC_can = MC_dir.Get("abseta_PLOT_pt_bin%d_&_Mu7p5_Track2_Jpsi_TK_pass_&_tag_Mu7p5_MU_pass_&_tag_Mu7p5_Track2_Jpsi_MU_pass" %ii)

    MC_graph = MC_can.GetPrimitive("hxy_fit_eff")
    Data_graph = Data_can.GetPrimitive("hxy_fit_eff")
    ##set the graph
    MC_graph.SetMarkerStyle(20)
    MC_graph.SetMarkerColor(ROOT.kRed)
    MC_graph.SetLineColor(ROOT.kRed)
    Data_graph.SetMarkerStyle(22)
    Data_graph.SetMarkerColor(ROOT.kBlue)
    Data_graph.SetLineColor(ROOT.kBlue)
    ## print the multigraph
    multiG = ROOT.TMultiGraph()
    multiG.Add(Data_graph)
    multiG.Add(MC_graph)
    multiG.SetTitle(str(sys.argv[1])+"ID   pt in "+getBinRange(ii, ptBin)+" GeV; abseta; efficiency")
    multiG.SetName("pt_bin"+str(ii))
    multiG.SetMinimum(0)
    multiG.SetMaximum(1.1)

    leg = ROOT.TLegend(0.7, 0.25, 0.85, 0.15)
    leg.AddEntry(Data_graph, "Data", "lp")
    leg.AddEntry(MC_graph, "MC", "lp")

    c2.cd(); 
    multiG.Draw("AP"); leg.Draw("same")
    c2.Print(DIR+"/efficiencies/pt_bins/pt_bin"+str(ii)+".pdf", "pdf")
    c2.SetName(multiG.GetName())
    c2.Write()


outFile.cd("efficiencies/eta_bins")
for ii in range(4):
    ## get the graphs
    Data_dir = Data_file.GetDirectory("tpTree/eff_pt_abseta/fit_eff_plots")
    Data_can = Data_dir.Get("pt_PLOT_abseta_bin%d_&_Mu7p5_Track2_Jpsi_TK_pass_&_tag_Mu7p5_MU_pass_&_tag_Mu7p5_Track2_Jpsi_MU_pass" %ii)
    MC_dir = MC_file.GetDirectory("tpTree/eff_pt_abseta/fit_eff_plots")
    MC_can = MC_dir.Get("pt_PLOT_abseta_bin%d_&_Mu7p5_Track2_Jpsi_TK_pass_&_tag_Mu7p5_MU_pass_&_tag_Mu7p5_Track2_Jpsi_MU_pass" %ii)

    MC_graph = MC_can.GetPrimitive("hxy_fit_eff")
    Data_graph = Data_can.GetPrimitive("hxy_fit_eff")

    ## set the graph
    MC_graph.SetMarkerStyle(20)
    MC_graph.SetMarkerColor(ROOT.kRed)
    MC_graph.SetLineColor(ROOT.kRed)
    Data_graph.SetMarkerStyle(22)
    Data_graph.SetMarkerColor(ROOT.kBlue)
    Data_graph.SetLineColor(ROOT.kBlue)
    ## print the multigraph
    multiG = ROOT.TMultiGraph()
    multiG.Add(Data_graph)
    multiG.Add(MC_graph)
    multiG.SetTitle(str(sys.argv[1])+"ID   |#eta| in "+getBinRange(ii, etaBin)+"; pt [Gev]; efficiency")
    multiG.SetName("eta_bin"+str(ii))
    multiG.SetMinimum(0)
    multiG.SetMaximum(1.1)

    leg = ROOT.TLegend(0.7, 0.25, 0.85, 0.15)
    leg.AddEntry(Data_graph, "Data", "lp")
    leg.AddEntry(MC_graph, "MC", "lp")

    c2.cd()
    c2.SetLogx()
    multiG.Draw("AP"); leg.Draw("same")
    c2.Print(DIR+"/efficiencies/eta_bins/eta_bin"+str(ii)+".pdf", "pdf")
    c2.SetName(multiG.GetName())
    c2.Write()

## la fin
print "All done. Results saved in "+DIR
outFile.Close()