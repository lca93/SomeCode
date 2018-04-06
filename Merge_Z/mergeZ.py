import json 
import math
from collections    import OrderedDict

def getWMean(ptList):
    mean = 0
    wght = 0
    for cc in ptList:
        mean += cc[0] / (cc[1]**2)
        wght += 1. / (cc[1]**2)

    mean = mean / wght
    wght = math.sqrt(1. / wght)

    return mean, wght

def getWMeanVal(ptList): return getWMean(ptList)[0]
def getWMeanErr(ptList): return getWMean(ptList)[1]

## int. luminosity [1/fb]
lumiBF = 3.011 + 2.573 + 4.242 + 4.025 + 3.105
lumiGH = 7.576 + 8.651

mainKey = 'tightID_from_Z'

inputFileBF = open('files/EfficienciesAndSF_BCDEF.json' , 'r')
inputFileGH = open('files/EfficienciesAndSF_GH.json'    , 'r')  

jsonDictBF  = json.load(inputFileBF, object_pairs_hook=OrderedDict)
jsonDictGH  = json.load(inputFileGH, object_pairs_hook=OrderedDict)

jsonDictBF = jsonDictBF['MC_NUM_TightID_DEN_genTracks_PAR_pt_eta']['pt_abseta_ratio']
jsonDictGH = jsonDictGH['MC_NUM_TightID_DEN_genTracks_PAR_pt_eta']['pt_abseta_ratio']

jsonOut     = OrderedDict()
jsonOut[mainKey] = OrderedDict()
jsonOut[mainKey]['pt_eta']   = OrderedDict()
jsonOut[mainKey]['pt']       = OrderedDict()
jsonOut[mainKey]['pt']['0.0,2.4']   = OrderedDict()

outputFile = open('SF_from_Z.json', 'w')

## loop over pT keys
for pB, pG in zip(jsonDictBF.keys(), jsonDictGH.keys()):
    if pB != pG: raise ValueError('ERROR BF and GH keys do not coincide')

    ptKey = pB.strip('pt:[').strip(']')
    ## loop over eta keys
    for eB, eG in zip(jsonDictBF[pB].keys(), jsonDictGH[pG].keys()):
        ptList = []
        if eB != eG: raise ValueError('ERROR BF and GH keys do not coincide')

        etaKey = eB.strip('abseta:[').strip(']')
        
        if not etaKey in jsonOut[mainKey]['pt_eta']        : jsonOut[mainKey]['pt_eta'][etaKey]        = OrderedDict()
        if not ptKey  in jsonOut[mainKey]['pt_eta'][etaKey]: jsonOut[mainKey]['pt_eta'][etaKey][ptKey] = OrderedDict()

        sf = (jsonDictBF[pB][eB]['value'] * lumiBF + jsonDictGH[pB][eB]['value'] * lumiGH) / (lumiBF + lumiGH)
        er = math.sqrt( lumiBF**2 * jsonDictBF[pB][eB]['error'] **2 + lumiGH**2 * jsonDictGH[pB][eB]['error'] **2) / (lumiBF + lumiGH)
        
        ptList.append((sf, er))

        jsonOut[mainKey]['pt_eta'][etaKey][ptKey]['value'] = sf
        jsonOut[mainKey]['pt_eta'][etaKey][ptKey]['error'] = er

    ## calculate the pT Sf as weighted mean of pt_eta SFs
    if not ptKey in jsonOut[mainKey]['pt']['0.0,2.4']: jsonOut[mainKey]['pt']['0.0,2.4'][ptKey] = OrderedDict() 
    jsonOut[mainKey]['pt']['0.0,2.4'][ptKey]['value'] = getWMeanVal(ptList)
    jsonOut[mainKey]['pt']['0.0,2.4'][ptKey]['error'] = getWMeanErr(ptList)

outputFile.write( json.dumps(jsonOut, indent=4, sort_keys=False))

## calculate SFs as function of pT only as weighted mean

outputFile.close()
inputFileBF.close()
inputFileGH.close()

