#######################################################################
## 
## The code reads the TnP output root files and extract the SFs and
## their error (as propagation of the bigget uncertanty between upper
## and lower error).
## Plots are saved for efficiencies and their ratio.
##
## The code work with 1D and 2D SFs. Configurations are set in 
## 'cfg/cfg_getSFs.py'.
##
## SFs are obtained from the TGraphs of the TnP files and not from 
## fitresults; this way it is easies to extract the pltos
##
## The SFs, and data and MC efficiencies are saved in a json file
## The plots are saved in a root file
## NOTE: for 0 SFs/efficiencies or 0 errors a value 'null' 
## is filled instead
##
## NOTE: ROOT may crash sometimes, try to run again or see the results:
## it may have succeded anyway
##
## JSON STRUCTURE:
## <ID tested>
## |
## ---> <variable1>
## |    |
## |    ---> <bin1>
## |    |    |
## |    |    ---> <value>
## |    |    ---> <error>
## |    ---> <bin2>
## |         |
## |         ---> <value>
## |         ---> <error>
## |
## ---> <variable2>
##      |
##      ---> <bin1>
## [etc]

import sys, os
import ROOT
import numpy as np
import json


from collections        import OrderedDict
from libs.getSFs_libs   import getSFs_1D, getSFs_2D
from cfg.cfg_getSFs     import varList, fileDA, fileMC, MAINDIR, printConfig, ID_type

sys.path.insert(0, os.environ['HOME'] + '/.local/lib/python2.6/site-packages')
import uncertainties as unc

global outFile

## set up root
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gStyle.SetPaintTextFormat(".3f")
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kFatal;")

## some variables
mainKey = ID_type

## root output file
outFile = ROOT.TFile("%s/%s.root" % (MAINDIR, ID_type), "RECREATE")

## create the main directory
if not os.path.exists(MAINDIR): os.makedirs(MAINDIR)

## json files
jsonFileSF  = open("%s/ScaleFactors_%s.json"      % (MAINDIR, mainKey), "w")
jsonFileDA  = open("%s/Efficiencies_%s_DATA.json" % (MAINDIR, mainKey), "w")
jsonFileMC  = open("%s/Efficiencies_%s_MC.json"   % (MAINDIR, mainKey), "w")

## create json structures
jsonStrucSF = OrderedDict()
jsonStrucDA = OrderedDict()
jsonStrucMC = OrderedDict()
jsonStrucSF[mainKey] = OrderedDict()
jsonStrucDA[mainKey] = OrderedDict()
jsonStrucMC[mainKey] = OrderedDict()

def getSFs (var, bins):
    outFile.cd()
    outFile.mkdir(var)
    outFile.cd(var)
    ## directory containing the efficiency plots
    plotDirDA = fileDA.GetDirectory("tpTree/eff_%s/fit_eff_plots" % var)
    plotDirMC = fileMC.GetDirectory("tpTree/eff_%s/fit_eff_plots" % var)

    ## get the list of keys
    ## check if directory exists, otherwise exit
    try:
      keysMC = list(plotDirMC.GetListOfKeys())
      keysDA = list(plotDirDA.GetListOfKeys())
    except:
      print ">>skipping %s: directory not found" % var
      return -1

    if len(keysMC) == 1:
        print "getting 1D SFs for %s" % var
        return  getSFs_1D( daDir = plotDirDA     ,
                           mcDir = plotDirMC     ,
                           var       = var       ,
                           bins      = bins      ,
                )

    else:
        print "getting 2D SFs for %s" % var
        return  getSFs_2D( daDir = plotDirDA     ,
                           mcDir = plotDirMC     , 
                           var   = var           ,
                           bins  = bins          ,
                )        

## <MAIN LOOP>
printConfig()

for vv in varList:
    struc = getSFs(vv[0], vv[1])
    if struc != -1:
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

jsonFileSF.close()
jsonFileDA.close()
jsonFileMC.close()

outFile.Close()
