import json
import os
from tabulate       import tabulate
from collections    import OrderedDict

def condition (dictionary):
    safeCheck = not (dictionary['value'] is None or dictionary['error']  is None)

    return ( (dictionary['value']) > 2 and safeCheck )

varList = [
    'pt'                    ,
    'pt_eta'                ,
    'pt_abseta'             ,
    'ds_pt'                 ,
    'ds_pt__VS__ds_eta'     ,
]

fileList = [
    'HLT_track_SFs'                                 ,
    'ScaleFactors_looseNOTmedium_muonID_updt'       ,
    'ScaleFactors_mediumNOTtight2016_muonID_updt'   ,
    'ScaleFactors_RunBH_muonHLT'                    ,
    'ScaleFactors_soft2016NOTloose_muonID_updt'     ,
    'ScaleFactors_tight2016_muonID_updt'            ,
    'ScaleFactors_tight2016_muonID_updt_withZ'      ,
    'SF_from_Z_ordered'                             ,
]

path = '%s/public/jsonFiles_SF' % os.path.expanduser('~')
fileList = ['%s/%s.json' % (path, ff) for ff in fileList]

outFile = open('fishyBins.txt', 'w')
table = []

for ff in fileList:
    rFile = open(ff, 'r')
    jsonDict = json.load(rFile, object_pairs_hook=OrderedDict)
    fileName = str( jsonDict.keys()[0])
    jsonDict = jsonDict[fileName]

    for vl in varList:
        varKeys = []
        varKeys = [str(vk) for vk in jsonDict.keys()]
        if not vl in varKeys: continue
        jsonDictEta = jsonDict[vl]

        etaKeys = jsonDictEta.keys()
        etaKeys = [ str( ek) for ek in etaKeys]

        for ek in etaKeys:
            jsonDictPt = jsonDictEta[ek]

            ptKeys = jsonDictEta[ek].keys()
            ptKeys = [str(pk) for pk in ptKeys]
            
            for pk in ptKeys:
                if condition(jsonDictPt[pk]):
                    table += [[fileName, vl, ek, pk, '%s +- %s' %(jsonDictPt[pk]['value'], jsonDictPt[pk]['error'])]]

    rFile.close()

outFile.write( tabulate(table, headers = ['ID', 'BIN. VAR', 'ETA', 'PT', 'SF +- ERR']))
outFile.close()
