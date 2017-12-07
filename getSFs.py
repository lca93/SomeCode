#######################################################################
## 5 Dec. 2017
## 
## the codes reads the root files created by the CMS TnP code
## and calculates the SFs 1D and 2D from the efficiencies saved 
## in those files
##

import sys, os
import ROOT
import numpy as np
import json


from collections        import OrderedDict
from libs.getSFs_libs   import getSFs_1D, getSFs_2D
from cfg_getSFs         import varList, fileDA, fileMC, MAINDIR
from cfg_getSFs         import printGraphs as pG

sys.path.insert(0, os.environ['HOME'] + '/.local/lib/python2.6/site-packages')
import uncertainties as unc

## bypass pG
if len(sys.argv) > 2:
  if sys.argv[2] == "plot":
    pG = True
  elif sys.argv[2] == "sf":
    pG = False
  else:
    print "ignoring second argument (is not 'plot' nor 'sf')"
    print "using defalut cfg instead (%s)" % str(pG)

## set up root
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gStyle.SetPaintTextFormat(".3f")
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kFatal;")

## some variables
mainKey = str(sys.argv[1])

## create the main directory
if not os.path.exists(MAINDIR): os.makedirs(MAINDIR)

## json files
## bypass cras TOBEFIXED
if not pG:
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
    ## directory containing the efficiency plots
    plotDirDA = fileDA.GetDirectory("tpTree/eff_%s/fit_eff_plots" % var)
    plotDirMC = fileMC.GetDirectory("tpTree/eff_%s/fit_eff_plots" % var)

    ## get the list of keys
    keys = list(plotDirMC.GetListOfKeys())

    if len(keys) == 1:
        print "getting 1D SFs for %s" % var
        return  getSFs_1D( daDir = plotDirDA     ,
                           mcDir = plotDirMC     ,
                           var       = var           ,
                           bins      = bins          ,
                           printGraphs=pG
                )

    else:
        print "getting 2D SFs for %s" % var
        return  getSFs_2D( daDir = plotDirDA     ,
                           mcDir = plotDirMC     , 
                           var   = var           ,
                           bins  = bins          ,
                           printGraphs=pG
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
## avoid crash TOBEFIXED
if not pG:
  jsonFileSF.write(jsonObjSF)
  jsonFileDA.write(jsonObjDA)
  jsonFileMC.write(jsonObjMC)