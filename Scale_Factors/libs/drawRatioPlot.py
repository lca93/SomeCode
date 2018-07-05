import ROOT
import sys, os

sys.path.insert(0, os.environ['HOME'] + '/.local/lib/python2.6/site-packages')
import uncertainties as unc

def printRatioGraphs (daGraph, mcGraph, sfList, varName, printDir, logx = False):
    ## define some ranges
    yRatioHigh = 1.1*max(sfList)[0].nominal_value if max(sfList)[0].nominal_value < 20.5 else 20.5
    yRatioLow  = 0.9*min(sfList)[0].nominal_value if min(sfList)[0].nominal_value > 0.0 else 0.0
    yEffHigh = 1.3*max ( ROOT.TMath.MaxElement(daGraph.GetN(), daGraph.GetY()),
                         ROOT.TMath.MaxElement(mcGraph.GetN(), mcGraph.GetY()))
    yEffLow  = 0
    xLow  = sfList[0][1] - 0.05*(sfList[-1][1]-sfList[0][1])
    xHigh = sfList[-1][1]*1.1

    ## create support histos
    supportEff = ROOT.TH1F("suppE", "", len(sfList), sfList[0][1], sfList[-1][1]*1.1)
    supportRat = ROOT.TH1F("suppR", "", len(sfList), sfList[0][1], sfList[-1][1]*1.1)

    ## define the axis range (multigraph bypass this, so only for ratio)
    supportRat.GetYaxis().SetRangeUser(yRatioLow, yRatioHigh)
    supportRat.GetXaxis().SetLimits(xLow, xHigh)

    ## create the legend
    legPad = ROOT.TLegend(0.7, 0.55, 0.85, 0.45)
    legPad.AddEntry(daGraph, "Data", "lp")
    legPad.AddEntry(mcGraph, "MC"  , "lp")

    ## set up the gaphs
    multiG = ROOT.TMultiGraph()
    multiG.SetTitle("SFs - %s muon ID; %s; efficiency" % (str(sys.argv[1]), varName))
    multiG.Add(daGraph)
    multiG.Add(mcGraph)
    multiG.SetMinimum(yEffLow)
    multiG.SetMaximum(yEffHigh)
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

    ## fill the SFs graph
    for i in range(len(sfList)):
        sfGraph.SetPoint( i, 
                          sfList[i][1],
                          sfList[i][0].nominal_value
        )
        sfGraph.SetPointError( i, 
                               0,
                               sfList[i][0].std_dev
        )

    outCan = ROOT.TCanvas("outCan%s" % varName, "", 700, 1000)
    outCan.SetTitle("SFs for %s binning  -  %s muonID" %(varName, str(sys.argv[1])))
    outCan.Divide(1, 2)
    ## set the pads
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
    
    ## draw the results
    outCan.cd(1)
    supportEff.Draw()
    multiG.Draw("same p")
    multiG.GetXaxis().SetLimits(xLow, xHigh)
    multiG.GetXaxis().SetTitleOffset( 1.3*multiG.GetXaxis().GetTitleOffset())
    legPad.Draw("same")

    
    ## draw on the ratio pad
    outCan.cd(2)
    supportRat.Draw()
    sfGraph.Draw("PLE3")
    ##print 
    outCan.Print("%s/SFs_%s_%s.pdf" % (printDir, varName, str(sys.argv[1])), "pdf")
    ## wirte on file
    outCan.Write()

    return 