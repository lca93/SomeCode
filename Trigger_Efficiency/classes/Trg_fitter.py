import ROOT
import json
import math
from collections import OrderedDict
from fitterPdf_c import fitterPDF

class TrgFitter ():
    def __init__(self, tree, mainVar, den, num, fitRange, nBins, oth = '1', fileName = 'outFile'):
        self.den = den
        self.num = ' & '.join([num, den])
        self.oth = oth

        self.fileName = fileName

        self.tree = tree
        self.cvas = ROOT.TCanvas()

        self.rFile = ROOT.TFile('%s.root' % self.fileName, 'RECREATE')
        self.oFile = open('%s.json' % self.fileName, 'w')

        self.mainVar = mainVar
        self.varList = {}

        self.jsonStruc = OrderedDict()

        self.fitRange = fitRange
        self.nBins= nBins

        self.SetOptions()
##
## public members

    def SetPDFs(self, numPDFs, numPDFb, denPDFs, denPDFb, numParS, numParB, denParS, denParB):
        self.pdfNum = fitterPDF(sigPDF = numPDFs, bacPDF=numPDFb, fitRange=self.fitRange)
        self.pdfDen = fitterPDF(sigPDF = denPDFs, bacPDF=denPDFb, fitRange=self.fitRange)

        self.pdfNum.SetPdfPars(sigPars=numParS, bacPars=numParB)
        self.pdfDen.SetPdfPars(sigPars=denParS, bacPars=denParB)

    def SetOptions(self, fitOpt = "RIMQ", fitAttNo = 1, pdbFit = True):
        self.fitOpt         = fitOpt
        self.fitAttemptNo   = fitAttNo
        self.pdbFit         = pdbFit

    def AddBinnedVar(self, var, bins):
        self.varList[var] = bins

    def CalculateEfficiency(self):
        if not self.checkBeforeStart(): return

        for vv in self.varList.keys():
            self.jsonStruc[vv] = OrderedDict()
            self.rFile.cd() ; self.rFile.mkdir(vv) ; self.rFile.cd(vv)

            if not isinstance(self.varList[vv], tuple):     ## 1D efficiencies
                self.jsonStruc[vv] = self.getEff(varName = vv, bins = self.varList[vv])
            else:                                           ## 2D efficiencies
                for j in range( len(self.varList[vv][1])-1):
                    self.rFile.GetDirectory(vv).mkdir(self.getBinRange(j, self.varList[vv][1])) ; self.rFile.GetDirectory(vv).cd(self.getBinRange(j, self.varList[vv][1]))

                    self.jsonStruc[vv][self.getBinRange(j, self.varList[vv][1])] = OrderedDict()
                    self.jsonStruc[vv][self.getBinRange(j, self.varList[vv][1])] = self.getEff(varName = vv, bins = self.varList[vv], is2D = True, indx = j)

        self.writeFiles()
##
## private members

    def getHistogram(self, name, cut):
        self.tree.Draw("%s>>%s(%s, %s, %s)" % (self.mainVar, name, self.nBins, self.fitRange[0], self.fitRange[1]), cut)
        return ROOT.gDirectory.Get(name)

    def fitHisto(self, histo, func, bpdf = None):
        for i in range (self.fitAttemptNo):
            histo.Fit(func, self.fitOpt)
        self.cvas.Update()
        if self.pdbFit: import pdb ; pdb.set_trace()
        ## update to lates fit panel fit
        func = histo.GetFunction(func.GetName())

        parv = [func.GetParameter(ii) for ii in range( func.GetNpar())]
        pare = [func.GetParError(ii)  for ii in range( func.GetNpar())]

        return (parv, pare)

    def checkBeforeStart(self):
        if self.den        is None : print "Denominator not set"        ; return False
        if self.num        is None : print "Numerator not set"          ; return False
        if self.pdfNum     is None : print "Nuimberator pdf not set"    ; return False
        if self.pdfDen     is None : print "Denominator pdf not set"    ; return False
        if self.tree       is None : print "tree not set"               ; return False
        if self.fitRange   is None : print "Fit limits not set"         ; return False
        if self.nBins      is None : print "Number of bins not set"     ; return False
        if self.mainVar    is None : print "Main variable not set"      ; return False
        if len(self.varList) == 0  : print "No binned variable set"     ; return False

        return True

    def getEff(self, varName, bins, is2D = False, indx = -1):
        jsonOut = OrderedDict()

        if is2D: bins1 = bins[0] ; bins2 = bins[1]
        else: bins1 = bins

        for i in range( len(bins1)-1):
            ##get the bin range
            if is2D:
                var1 = varName.split('__VS__')[0]
                var2 = varName.split('__VS__')[1]
                binR = '%s & %s' % (self.binRange(i, bins1, var1), self.binRange(indx, bins2, var2))
            else: binR = self.binRange(i, bins1, varName)

            ## get the histos
            histoN = self.getHistogram('bin%s NUM' % i, '%s & %s & %s' % (self.num, binR, self.oth))
            histoD = self.getHistogram('bin%s DEN' % i, '%s & %s & %s' % (self.den, binR, self.oth))
            
            ## fit the histos
            resNum = self.fitHisto( histoN, self.pdfNum.GetTotPDF()) ; self.pdfNum.UpdatePDFParameters(resNum[0], resNum[1])
            resDen = self.fitHisto( histoD, self.pdfDen.GetTotPDF()) ; self.pdfDen.UpdatePDFParameters(resDen[0], resDen[1])

            ## draw on a canvas
            self.drawResults(histoN, histoD).Write()

            ## write in file
            histoN.Write()
            histoD.Write()

            ## get the integral
            intN = (    self.pdfNum.GetSigPDF().Integral( self.fitRange[0], self.fitRange[1]),
                        self.pdfNum.GetSigPDF().IntegralError( self.fitRange[0], self.fitRange[1])**2
            )
            intD = (    self.pdfDen.GetSigPDF().Integral( self.fitRange[0], self.fitRange[1]),
                        self.pdfDen.GetSigPDF().IntegralError( self.fitRange[0], self.fitRange[1])**2
            )
            import pdb ; pdb.set_trace()

            ## get the efficiency
            eff = intN[0]/intD[0]
            err = math.sqrt( ((1./intD[0])**2) * intN[1] + ((intN[0]/intD[0]**2)**2) * intD[1])

            ## results
            jsonOut[self.getBinRange(i, bins1)] = OrderedDict()
            jsonOut[self.getBinRange(i, bins1)]['value'] = eff
            jsonOut[self.getBinRange(i, bins1)]['error'] = err

        return jsonOut

    def drawResults(self, histoN, histoD):
        outCvas = ROOT.TCanvas()
        outCvas.Divide(2, 1)

        outCvas.cd(1) ; histoN.Draw() ; self.pdfNum.GetTotPDF().Draw('same') ; self.pdfDen.GetBacPDF().Draw('same')
        outCvas.cd(2) ; histoD.Draw() ; self.pdfDen.GetTotPDF().Draw('same') ; self.pdfDen.GetBacPDF().Draw('same')

        return outCvas

    def binRange(self, ind, bins, var, absVal=True):
        return  'abs(%s) >= %s && abs(%s) <= %s' % (var, bins[ind], var, bins[ind+1]) if absVal else \
                '%s >= %s && %s <= %s'           % (var, bins[ind], var, bins[ind+1])

    def getBinRange(self, i, bins, sep = ','):
        down =  str(bins[i])
        up   =  str(bins[i+1])
        return down+sep+up

    def writeFiles(self):
        self.oFile.write(json.dumps(self.jsonStruc, indent=4, sort_keys=False))
        self.oFile.close()
        self.rFile.Close()
