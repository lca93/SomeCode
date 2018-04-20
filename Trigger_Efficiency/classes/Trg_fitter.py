import ROOT
import json
import math
import numpy

from collections import OrderedDict
from fitterPdf_c import fitterPDF

class TrgFitter ():
    def __init__(self, tree, mainVar, den, num, fitRangeDen, fitRangeNum, nBins, fitRange = None,  oth = '1', fileName = 'outFile'):
        self.den = den
        self.num = ' & '.join([num, den])
        self.oth = oth

        self.bpdfNum = None
        self.bpdfDen = None

        self.fileName = fileName

        self.tree = tree
        self.cvas = ROOT.TCanvas()

        self.rFile = ROOT.TFile('%s.root' % self.fileName, 'RECREATE')
        self.oFile = open('%s.json' % self.fileName, 'w')

        self.mainVar = mainVar
        self.varList = {}

        self.jsonStruc = OrderedDict()

        self.fitRangeNum = fitRangeNum
        self.fitRangeDen = fitRangeDen
        
        self.checkFitRange(fitRange)

        self.nBins= nBins
        self.pVal = False

        self.SetOptions()

    def checkFitRange(self, fitRange):
        if fitRange is not None: 
            self.fitRange = fitRange
            return
        else:
            self.fitRange = (   min( self.fitRangeNum[0], self.fitRangeDen[0]),
                                max( self.fitRangeNum[1], self.fitRangeDen[1])
            )

    def SetPDFs(self, numPDFs, numPDFb, denPDFs, denPDFb, numParS, numParB, denParS, denParB):
        self.pdfNum = fitterPDF(sigPDF = numPDFs, bacPDF=numPDFb, fitRange=self.fitRangeNum, name = 'NUM')
        self.pdfDen = fitterPDF(sigPDF = denPDFs, bacPDF=denPDFb, fitRange=self.fitRangeDen, name = 'DEN')

        self.pdfNum.SetPdfPars(sigPars=numParS, bacPars=numParB)
        self.pdfDen.SetPdfPars(sigPars=denParS, bacPars=denParB)

    def SetOptions(self, useGausSignal = False, useAsymErrors = True, fitOpt = "RIMQ", fitAttNo = 2, pdbFit = True, DrawResidual = False):
        self.fitOpt         = fitOpt
        self.fitAttemptNo   = fitAttNo
        self.pdbFit         = pdbFit
        self.useGausSignal = useGausSignal
        self.useAsymErrors = useAsymErrors
        self.DrawResidual  = DrawResidual

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

    def getHistogram(self, name, cut):
        self.tree.Draw("%s>>%s(%s, %s, %s)" % (self.mainVar, name, self.nBins, self.fitRange[0], self.fitRange[1]), cut)
        return ROOT.gDirectory.Get(name)

    def fitHisto(self, histo, func):
        for xx in range (self.fitAttemptNo):
            histo.Fit(func, self.fitOpt)

        self.cvas.Update()

        if self.pdbFit: import pdb ; pdb.set_trace()
        ## update to lates fit panel fit
        func = histo.GetFunction(func.GetName())
        if func.GetProb() < 0.001: self.pVal = True

        ## get the paramters
        parV = [func.GetParameter(ii) for ii in range( func.GetNpar())]
        parE = [func.GetParError(ii)  for ii in range( func.GetNpar())]

        ##get the covariance matrix
        cMat =  ROOT.TMatrixDSym( func.GetNpar())
        ROOT.gMinuit.mnemat( cMat.GetMatrixArray(), func.GetNpar())
        covM = [cMat.GetMatrixArray()[zz] for zz in range( func.GetNpar()**2)]

        ## diagonalize check
        #covM = numpy.asarray( [covM[mm] if mm in [xx*6 for xx in range( func.GetNpar())] else 0 for mm in range( func.GetNpar()**2)] )
        #import pdb ; pdb.set_trace()


        return (parV, parE, covM)
        #return (parV, parE)

    def checkBeforeStart(self):
        if self.den        is None : print "Denominator not set"        ; return False
        if self.num        is None : print "Numerator not set"          ; return False
        if self.pdfNum     is None : print "Nuimberator pdf not set"    ; return False
        if self.pdfDen     is None : print "Denominator pdf not set"    ; return False
        if self.tree       is None : print "tree not set"               ; return False
        if self.fitRangeDen is None: print "Fit limits not set"         ; return False
        if self.fitRangeNum is None: print "Fit limits not set"         ; return False
        if self.nBins      is None : print "Number of bins not set"     ; return False
        if self.mainVar    is None : print "Main variable not set"      ; return False
        if len(self.varList) == 0  : print "No binned variable set"     ; return False

        if self.useGausSignal: print '!! Using gaussian parametrization for integral calculation !!'

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

            ## set the covariance matrix
            self.pdfNum.SetCovMatrix( resNum[2])
            self.pdfDen.SetCovMatrix( resDen[2])

            ## draw on a canvas
            self.drawResults(histoN, histoD).Write()

            ## set usefull params
            parNum = numpy.asarray([self.pdfNum.GetSigPDF().GetParameter(pp) for pp in range( self.pdfNum.GetSigPDF().GetNpar())])
            parDen = numpy.asarray([self.pdfDen.GetSigPDF().GetParameter(pp) for pp in range( self.pdfDen.GetSigPDF().GetNpar())])

            ## write in file
            histoN.Write()
            histoD.Write()

            binSize = (self.fitRange[1]-self.fitRange[0])/self.nBins

            ## get the integral
            if self.useGausSignal:    
                intN = self.__getEvt(self.pdfNum.GetSigPDF())
                intD = self.__getEvt(self.pdfDen.GetSigPDF())
            else:
                intN = (    self.pdfNum.GetSigPDF().Integral( self.fitRange[0], self.fitRange[1]) / binSize,
                            (self.pdfNum.GetSigPDF().IntegralError(  self.fitRange[0], self.fitRange[1], 
                                                                     self.pdfNum.GetSigParList(), self.pdfNum.GetSigCovMatrix()
                            )**2)/(binSize**2)
                )
                intD = (    self.pdfDen.GetSigPDF().Integral( self.fitRange[0], self.fitRange[1]) / binSize,
                            (self.pdfDen.GetSigPDF().IntegralError(  self.fitRange[0], self.fitRange[1],
                                                                     self.pdfDen.GetSigParList(), self.pdfDen.GetSigCovMatrix()
                            )**2)/(binSize**2)
                )

            ## get the efficiency
            if self.useAsymErrors:
                asy = self.getAsymEff(intN[0], intD[0])
                eff = asy[0]
                err = asy[1]
            else:
                eff = intN[0]/intD[0]
                err = math.sqrt( ((1./intD[0])**2) * intN[1] + ((intN[0]/intD[0]**2)**2) * intD[1] )

            ## results
            jsonOut[self.getBinRange(i, bins1)] = OrderedDict()
            jsonOut[self.getBinRange(i, bins1)]['value'] = eff
            if self.useAsymErrors:
                jsonOut[self.getBinRange(i, bins1)]['errorUP']  = err[0]
                jsonOut[self.getBinRange(i, bins1)]['errorDW']  = err[1]
                jsonOut[self.getBinRange(i, bins1)]['error'] = max(err[0], err[1])
            else:
                jsonOut[self.getBinRange(i, bins1)]['error'] = err

        if self.pVal == True: print 'You may want to check some of the fits'
        return jsonOut

    def getAsymEff (self, vNum, vDen):
        hPass = ROOT.TH1F('hP', 'passing events', 1, 0, 1)
        hTotl = ROOT.TH1F('hT', 'total events'  , 1, 0, 1)

        hPass.SetBinContent(1, vNum)
        hPass.SetBinError(1, math.sqrt(vNum))
        hTotl.SetBinContent(1, vDen)
        hTotl.SetBinError(1, math.sqrt(vDen))

        tEff = ROOT.TEfficiency(hPass, hTotl)

        return tEff.GetEfficiency(1), (tEff.GetEfficiencyErrorUp(1), tEff.GetEfficiencyErrorLow(1))

    def __getEvt(self, pdf):
        vNorm = pdf.GetParameter(0) ; eNorm = pdf.GetParError(0)
        vSigm = pdf.GetParameter(2) ; eSigm = pdf.GetParError(2)
        binSize = (self.fitRange[1] - self.fitRange[0]) / self.nBins

        evt = abs(vNorm * vSigm * math.sqrt(2. * math.pi) / binSize)
        er2 = (2.*math.pi) * ( (vNorm*eSigm)**2 + (vSigm*eNorm)**2) / (binSize**2)

        return (evt, er2)

    def drawResults(self, histoN, histoD):
        outCvas = ROOT.TCanvas()
        outCvas.Divide(2, 1+int(self.DrawResidual))

        self.pdfNum.GetBacPDF().SetLineStyle(ROOT.kDashed)
        self.pdfDen.GetBacPDF().SetLineStyle(ROOT.kDashed)

        self.pdfNum.GetSigPDF().SetLineColor(ROOT.kBlue) ; self.pdfNum.GetSigPDF().SetLineWidth(1) ; self.pdfNum.GetSigPDF().SetLineStyle(2)
        self.pdfDen.GetSigPDF().SetLineColor(ROOT.kBlue) ; self.pdfDen.GetSigPDF().SetLineWidth(1) ; self.pdfDen.GetSigPDF().SetLineStyle(2)

        histoN.SetMinimum(0)
        histoD.SetMinimum(0)

        outCvas.cd(1) ; histoN.Draw() ; self.pdfNum.GetTotPDF().Draw('same') ; self.pdfNum.GetBacPDF().Draw('same') ; self.pdfNum.GetSigPDF().Draw("same")
        outCvas.cd(2) ; histoD.Draw() ; self.pdfDen.GetTotPDF().Draw('same') ; self.pdfDen.GetBacPDF().Draw('same') ; self.pdfDen.GetSigPDF().Draw("same")

        self.resNum = ROOT.TH1F('resN', 'Fit residual', self.nBins, self.fitRange[0], self.fitRange[1])
        self.resDen = ROOT.TH1F('resD', 'Fit residual', self.nBins, self.fitRange[0], self.fitRange[1])

        if self.DrawResidual:
            for bb in range( histoN.GetSize() - 1):
                if histoN.GetBinError(bb + 1) != 0: 
                    self.resNum.SetBinContent( bb + 1, 
                            (histoN.GetBinContent(bb + 1) - self.pdfNum.GetTotPDF().Eval( histoN.GetBinCenter( bb + 1))) / histoN.GetBinError(bb + 1)
                    )
                else: self.resNum.SetBinContent( bb + 1, 0)
                if histoD.GetBinError(bb + 1) != 0: 
                    self.resDen.SetBinContent( bb + 1, 
                            (histoD.GetBinContent(bb + 1) - self.pdfDen.GetTotPDF().Eval( histoN.GetBinCenter( bb + 1))) / histoD.GetBinError(bb + 1)
                    )
                else: self.resDen.SetBinContent( bb + 1, 0)
                
                self.resNum.SetBinError(bb + 1, 1)
                self.resDen.SetBinError(bb + 1, 1)

            outCvas.cd(3) ; self.resNum.SetMarkerStyle(10); self.resNum.Draw('E1')
            outCvas.cd(4) ; self.resDen.SetMarkerStyle(10); self.resDen.Draw('E1')

            outCvas.GetListOfPrimitives()[2].SetGridy()
            outCvas.GetListOfPrimitives()[3].SetGridy()

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
