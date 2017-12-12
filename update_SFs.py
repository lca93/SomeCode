####################################################
## the code updates the SF jsons in order to
## make 1D plots 2D readable
## 
## that is, each pt 1D bin gets an additional key
## of abseta
##
## jsons inputs are muonPOG format-like
##

import json
import sys
from collections    import OrderedDict

## some variables
global ID

ID = str(sys.argv[1])

if   ID.find("BCDEF_") != -1: fID = "BCDEF/%s" % ID
elif ID.find("GH_")    != -1: fID = "GH/%s"    % ID
else: fID = ID

##input files
jsonFileI = open('%s/ScaleFactors_%s_muonID.json' % (fID, ID), 'r')
jsonStruc = json.load(jsonFileI)

## output file
jsonFileO = open('%s/ScaleFactors_%s_muonID_updt.json' % (fID, ID), 'w')

def update_pt(jsonStruc):
    mID = "%s_muonID" % ID
    ## create the output json
    jsonOut      = OrderedDict()
    jsonOut[mID] = OrderedDict()
    jsonOut[mID]['pt']        = OrderedDict()
    jsonOut[mID]['eta']       = jsonStruc[mID]['eta']
    try   : jsonOut[mID]['nVtx'] = jsonStruc[mID]['nVtx']
    except: pass
    jsonOut[mID]['pt_abseta'] = jsonStruc[mID]['pt_abseta']

    ## import pt key
    jsonPt  = jsonStruc[mID]['pt']

    ## create the additional eta key
    jsonOut[mID]['pt']['0.0,2.4'] = OrderedDict()

    ## fill the pt bins keys
    for i, kk in jsonPt.iteritems():
        jsonOut[mID]['pt']['0.0,2.4'][str(i)] = kk

    return jsonOut

## <<MAIN LOOP>>
jsonOut = update_pt(jsonStruc)
jsonObj = json.dumps(jsonOut, indent=4, sort_keys=False) 

jsonFileO.write(jsonObj)

jsonFileO.close()
jsonFileI.close()
