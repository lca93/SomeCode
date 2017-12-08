###############################################
##
## compare SFs obtained by getSFs.py
##

TITLE = 

def compare1D (key1, key2):
    ## get the graphs
    DAgraph1 = kk1.ReadObj().GetListOfPrimitives()[0]
    MCgraph1 = 
    SFgraph1 =

    DAgraph2 = 
    MCgraph2 = 
    SFgraph2 =

    ## multigraphs
    multiG1 = ROOT.TMultiGraph()
    multiG2 = ROOT.TMultiGraph()

    multiG1.Add(DAgraph1)
    multiG1.Add(MCgraph1)
    multiG1.Add(SFgraph1)

    multiG2.Add(DAgraph2)
    multiG2.Add(MCgraph2)
    multiG2.Add(SFgraph2)

    ## set the graphs
    DAgraph2.SetMarkerStyle(26)
    MCgraph2.SetMarkerStyle(24)
    SFgraph2.SetMarkerStyle(24)

    DAgraph2.SetMarkerColor(ROOT.kGreen)
    MCgraph2.SetMarkerColor(ROOT.kYellow)
    SFgraph2.SetMarkerColor(ROOT.kCyan)

    DAgraph2.SetLineColor(ROOT.kGreen)
    MCgraph2.SetLineColor(ROOT.kYellow)
    SFgraph2.SetLineColor(ROOT.kCyan)

    ##set the canvas
    outCan = ROOT.TCanvas("outCan", TITLE)
    outCan.Divide(1, 2)
    outCan.GetListOfPrimitives()[0].SetPad('effPad%s'   % varName, 'effPad'  , 0., 0.30, 1., 1., 0, 0)
    outCan.GetListOfPrimitives()[1].SetPad('ratioPad%s' % varName, 'ratioPad', 0., 0.32, 1., .0, 0, 0)
    outCan.GetListOfPrimitives()[0].SetLogx(logx)
    outCan.GetListOfPrimitives()[1].SetLogx(logx)

    outCan.GetListOfPrimitives()[0].SetGridy(True)
    outCan.GetListOfPrimitives()[1].SetGridy(True)
    outCan.GetListOfPrimitives()[0].SetGridx(True)
    outCan.GetListOfPrimitives()[1].SetGridx(True)

    outCan.GetListOfPrimitives()[0].SetBottomMargin(0.2)
    outCan.GetListOfPrimitives()[1].SetBottomMargin(0.2)
    
    ## print on same canvas
    outCan.cd(1)


## open files
file1 = ROOT.TFile.Open()
file2 = ROOT.TFile.Open()

## get the keys
keys1 = 
keys2 = 

## loop inside the directories
for k1, k2 in zip(keys1, keys2):
    ## get the keys of the directory
    kk1 = k1.ReadObj().GetListOfKeys()
    kk2 = k2.ReadObj().GetListOfKeys()
    ## 1D
    if len(kk1)==1:
        compare1D(kk1, kk2)
    ## 2D
    else:





    fitresDA = ROOT.RooRealVar( kk[0].ReadObj().Get("fitresults").floatParsFinal().at(1) ).getValV()
