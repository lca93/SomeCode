## the code computes SFs for the pT VS eta binning specified
## results are obtained with a weighted mean above the eta bins
## the pT key is the one used in the anlysis, and requires a eta subkey (whole range 0-2.4)

import json
import sys, os
from collections import OrderedDict
import ROOT
import math

sys.path.insert(0, os.environ['HOME'] + '/.local/lib/python2.6/site-packages')
import uncertainties as unc

fileDA = open('Ds_eta_pt_data_allstat.json', 'r')
fileMC = open('Ds_eta_pt_mc.json', 'r')

jsonDA = json.load(fileDA, object_pairs_hook=OrderedDict)
jsonMC = json.load(fileMC, object_pairs_hook=OrderedDict)

jsonOut  = open('HLT_track_SFs.json', 'w')

mainKey = 'HLT_track'
jsonDict = OrderedDict()
jsonDict[mainKey] = OrderedDict()
jsonDict[mainKey]['pt_eta'] = OrderedDict()

jsonDict[mainKey]['pt'] = OrderedDict()
jsonDict[mainKey]['pt']['0.0,2.4'] = OrderedDict()

keyListEta = jsonDA['pt_eta'].keys()
keyListEta = [str(kk) for kk in keyListEta]
keyListPt  = jsonDA['pt_eta'][keyListEta[0]].keys()
keyListPt = [str(kk) for kk in keyListPt]

sfHisto = ROOT.TH2F('HLT_track_sf', 'HLT track SFs', len(keyListPt), 0, len(keyListPt),len(keyListEta), 0, len(keyListEta))

## pt_eta
for i, ke in enumerate(keyListEta):
    jsonDict[mainKey]['pt_eta'][ke] = OrderedDict()
    for j, kp in enumerate(keyListPt):
        jsonDict[mainKey]['pt_eta'][ke][kp] = OrderedDict()
        dVal = unc.ufloat(
            jsonDA['pt_eta'][ke][kp]['value'],
            jsonDA['pt_eta'][ke][kp]['error'],
        )
        mVal = unc.ufloat(
            jsonMC['pt_eta'][ke][kp]['value'],
            jsonMC['pt_eta'][ke][kp]['error'],
        )
        sVal = dVal / mVal if mVal.nominal_value != 0 else unc.ufloat(0, 0)
        
        jsonDict[mainKey]['pt_eta'][ke][kp]['value'] = sVal.nominal_value
        jsonDict[mainKey]['pt_eta'][ke][kp]['error'] = sVal.std_dev

        sfHisto.SetBinContent( j+1, i+1, sVal.nominal_value)
        sfHisto.SetBinError( j+1, i+1, sVal.std_dev)

## pt as weighted mean of pt_eta
for j in range( len(keyListPt)):
    val = 0
    err = 0
    jsonDict[mainKey]['pt']['0.0,2.4'][keyListPt[j]] = OrderedDict()
    for i in range( len(keyListEta)):
        val += sfHisto.GetBinContent(j+1, i+1) / (sfHisto.GetBinError(j+1, i+1) **2)
        err += 1. / sfHisto.GetBinError(j+1, i+1) **2 ## normalization

    val = val / err ## normalise    
    err = math.sqrt( 1./err) ## define the error

    jsonDict[mainKey]['pt']['0.0,2.4'][keyListPt[j]]['value'] = val
    jsonDict[mainKey]['pt']['0.0,2.4'][keyListPt[j]]['error'] = err

jsonOut.write( json.dumps(jsonDict, indent=4, sort_keys=False))
jsonOut.close()
fileDA.close()
fileMC.close()

