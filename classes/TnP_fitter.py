import ROOT
import json
from collections import OrderedDict

class tnpFitter ():
    def __init__(self, den, num, oth = "1", pdfNum, pdfDen, fileName="outFile", tree, mainVar, mainCanvas = ROOT.TCanvas()):
        self.den = den
        self.num = num
        self.oth = oth
        
        self.pdfNum = pdfNum
        self.pdfDen = pdfDen

        self.fileName = fileName

        self.tree = tree
        self.cvas = mainCanvas

        self.rFile = ROOT.TFile('%s.root' % self.fileName)
        self.oFile = open('%s.json' % self.fileName)

        self.mainVar = mainVar
        self.varList = []

        self.jsonStruc = OrderedDict()

        self.integFuncIsSet = False

        setOptions()

    def setOptions(self, fitOpt = "RIMQ", fitAttNo = 1, pdbFit = True):
        self.fitOpt = fitOpt
        self.fitAttemptNo = fitAttNo
        self.pdbFit = pdbFit

    def setIntegratingFunction(self, func, *args):
        self.integFuncIsSet = True
        self.integFunc = func
        self.integArgs = args

    def getIntegral(self, func):
        return self.integFunc(func, self.integArgs)

    def addBinnedVar(self, var, bins):
        self.varList.append((var, bins))

    def getHistogram(self, name, cut):
        cAux = ROOT.TCanvas() ; cAux.cd()
        self.tree.Draw("%s>>%s()" % (self.mainVar, name), cut)
        cAux.Close() ; self.mainCanvas.cd()
        return ROOT.gDirectory.Get(name)

    def fitHisto(self, histo, func):
        for i in range (self.fitAttemptNo): histo.Fit(func, self.fitOpt)
        if self.pdbFit: import pdb ; pdb.set_trace()
        ## update to lates fit panel fit
        func = histo.GetFunction(func.GetName())

    def writeObj(self, obj):
        obj.Write()

    def checkBeforeStart(self):
        if self.den        is None : print "Denominator not set"        ; return False
        if self.num        is None : print "Numerator not set"          ; return False
        if self.pdfNum     is None : print "Nuimberator pdf not set"    ; return False
        if self.pdfDen     is None : print "Denominator pdf not set"    ; return False
        if self.tree       is None : print "tree not set"               ; return False
        if self.mainVar    is None : print "Main variable not set"      ; return False
        if len(self.varList) == 0  : print "No binned variable set"     ; return False    

        return True

    def CalculateEfficiency(self):
        if not self.checkBeforStart(): return

        for vv in self.varList:
            self.jsonStruc[vv[0]] = OrderedDict()
            self.oFile.cd() ; self.oFile.mkdir(vv[0]) ; self.oFile.cd(vv[0])

            if not isinstance(vv[1], tuple):     ## 1D efficiencies 
                self.jsonStruc[vv[0]] = self.getEff(varName = vv[0], bins = vv[1])
            else:                                ## 2D efficiencies
                for j in range( len(vv[1][1])-1):
                    self.oFile.GetDirectory(vv[0]).mkdir(getBinRange(j, vv[1][1])) ; self.oFile.GetDirectory(vv[0]).cd(getBinRange(j, vv[1][1]))
                    
                    self.jsonStruc[vv[0]][getBinRange(j, vv[1][1])] = OrderedDict()
                    self.jsonStruc[vv[0]][getBinRange(j, vv[1][1])] = self.getEff(varName = vv[0], bins = vv[1], is2D = True, indx = j)

    def getEff( varName, bins, is2D = False, indx = -1):
        jsonOut = OrderedDict()

        if is2D: bins1 = bins[0] ; bins2 = bins[1]
        else: bins1 = bins

        for i in range( len(bins1)-1):
            ##get the bin range
            if is2D:
                var1 = varName.split('::VS::')[0]
                var2 = varName.split('::VS::')[1]
                binR = '%s & %s' % (BinRange(i, bins1, var1), BinRange(indx, bins2, var2))
            else: binR = BinRange(i, bins1, varName)
            
            ## get the histos
            histoD = self.getHistogram('histoN', '%s & %s & %s' % (self.den, binR, self.oth))
            histoN = self.getHistogram('histoD', '%s & %s & %s' % (self.num, binR, self.oth))

            ## fit the histos
            self.fitHisto( histoN, self.pdfNum)
            self.fitHisto( histoD, self.pdfDen)

            ## write in file
            self.writeObj(histoN)
            self.writeObj(histoD)

            ## get the integral
            intN = getIntegral(self.pdfNum)
            intD = getIntegral(self.pdfDen)
            
            ## get the efficiency
            eff = intN[0]/intD[0]
            err = math.sqrt( ((1./intD[0])**2) * intN[1] + ((intN[0]/intD[0]**2)**2) * intD[1])

            ## results
            jsonOut[getBinRange(i, bins1)] = OrderedDict()
            jsonOut[getBinRange(i, bins1)]['value'] = eff
            jsonOut[getBinRange(i, bins1)]['error'] = err

        return jsonOut

    ## get bin interval condition
    def BinRange(ind, bins, var, absVal=True):
        return ? absVal 'abs(%s) >= %s && abs(%s) <= %s' % (var, bins[ind], var, bins[ind+1]) : \
                        'abs(%s) >= %s && abs(%s) <= %s' % (var, bins[ind], var, bins[ind+1]) 

    def writeFiles(self):
        self.oFile.write(json.dumps(self.jsonStruc, indent=4, sort_keys=False))
        self.oFile.close()
        self.rFile.Close()
