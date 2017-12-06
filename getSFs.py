#######################################################################
## 5 Dec. 2017
## 
## the codes reads the root files created by the CMS TnP code
## and calculates the SFs 1D and 2D from the efficiencies saved 
## in those files
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

from collections    import OrderedDict
from getSFs_libs    import getSFs_1D, getSFs_2D

sys.path.insert(0, os.environ['HOME'] + '/.local/lib/python2.6/site-packages')
import uncertainties as unc

## set up root
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gStyle.SetPaintTextFormat(".3f")
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kFatal;")
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
absetaBins = np.array([0, 0.9, 1.2, 2.1, 2.4])

varList =[  ("pt"   , ptBins  ),
            ("eta"  , etaBins ),
            ("nVtx" , nVtxBins),
            #("pt_abseta", (ptBins, absetaBins)),
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

    ## get the list of keys
    keysMC = list(plotDirDA.GetListOfKeys())
    keysDA = list(plotDirMC.GetListOfKeys())
    if not len(keysDA) == len(keysMC): 
        print "MC keys are different in number from Data keys for %s" % var
        return

    if len(keysDA) == 1:
        print "getting 1D SFs for %s" % var
        return  getSFs_1D( plotDirDA = plotDirDA     ,
                           plotDirMC = plotDirMC     ,
                           var       = var           ,
                           bins      = bins          ,
                           printGraphs = printGraphs ,
                )

    else:
        print "getting 2D SFs for %s" % var
        return  getSFs_2D( daDir = plotDirDA     ,
                           mcDir = plotDirMC     , 
                           bins  = bins          ,
                )        

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