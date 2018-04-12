## get SFs from data and MC jsons
import json
import sys, os
from collections import OrderedDict
import ROOT
import math

sys.path.insert(0, os.environ['HOME'] + '/.local/lib/python2.6/site-packages')
import uncertainties as unc

fileDA = open('results_asym/allStat_data.json', 'r')
fileMC = open('results_asym/allStat_mc.json', 'r')

jsonDA = json.load(fileDA, object_pairs_hook=OrderedDict)
jsonMC = json.load(fileMC, object_pairs_hook=OrderedDict)

jsonOut  = open('HLT_track_SFs.json', 'w')

mainKey     = 'HLT_track_SFs'
ptKey       = 'ds_pt'
ptetaKey    = 'ds_pt__VS__ds_eta'

jsonDict = OrderedDict()
jsonDict[mainKey] = OrderedDict()
jsonDict[mainKey][ptKey] = OrderedDict()
jsonDict[mainKey][ptKey]['0.0,2.4'] = OrderedDict()
jsonDict[mainKey][ptetaKey] = OrderedDict()



## get pT SFs
for kk in jsonDA[ptKey].keys():
    kk = str(kk)
    jsonDict[mainKey][ptKey]['0.0,2.4'][kk] = OrderedDict()

    num = unc.ufloat( jsonDA[ptKey][kk]['value'], jsonDA[ptKey][kk]['error'])
    den = unc.ufloat( jsonMC[ptKey][kk]['value'], jsonMC[ptKey][kk]['error'])

    rat = num / den if den.nominal_value != 0 else unc.ufloat(1, 1)

    jsonDict[mainKey][ptKey]['0.0,2.4'][kk]['value'] = rat.nominal_value
    jsonDict[mainKey][ptKey]['0.0,2.4'][kk]['error'] = rat.std_dev

for cc in jsonDA[ptetaKey].keys():
    cc = str(cc)
    jsonDict[mainKey][ptetaKey][cc] = OrderedDict()
    for kk in jsonDA[ptetaKey][cc].keys():
        kk = str(kk)
        jsonDict[mainKey][ptetaKey][cc][kk] = OrderedDict()

        num = unc.ufloat( jsonDA[ptetaKey][cc][kk]['value'], jsonDA[ptetaKey][cc][kk]['error'])
        den = unc.ufloat( jsonMC[ptetaKey][cc][kk]['value'], jsonMC[ptetaKey][cc][kk]['error'])

        rat = num / den if den.nominal_value != 0 else unc.ufloat(1, 1)      

        jsonDict[mainKey][ptetaKey][cc][kk]['value'] = rat.nominal_value
        jsonDict[mainKey][ptetaKey][cc][kk]['error'] = rat.std_dev  


jsonOut.write(  json.dumps(jsonDict, indent=4, sort_keys=False))
jsonOut.close()
fileMC.close()
fileDA.close()