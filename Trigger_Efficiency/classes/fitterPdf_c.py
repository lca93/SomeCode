import ROOT
from itertools import product

class fitterPDF():
    def __init__(self, sigPDF, bacPDF, fitRange):
        self.fitRange = fitRange

        self.sigPDF = self.generatePDF( sigPDF) ; self.sigPDF.SetName('sigPDF') 
        self.bacPDF = self.generatePDF( bacPDF) ; self.bacPDF.SetName('bacPDF')
##
## public members
    def SetPdfPars(self, sigPars, bacPars):
        for j in range( len(sigPars)):
            if not sigPars[j][0] is None: self.sigPDF.SetParName(j, sigPars[j][0])
            if not sigPars[j][1] is None: self.sigPDF.SetParameter(j, sigPars[j][1])
            if not sigPars[j][2] is None: self.sigPDF.SetParLimits(j, sigPars[j][2][0], sigPars[j][2][1])
        for j in range( len(bacPars)):
            if not bacPars[j][0] is None: self.bacPDF.SetParName(j, bacPars[j][0])
            if not bacPars[j][1] is None: self.bacPDF.SetParameter(j, bacPars[j][1])
            if not bacPars[j][2] is None: self.bacPDF.SetParLimits(j, bacPars[j][2][0], bacPars[j][2][1])

        self.totPDF = self.generatePDF( '%s+%s' % (self.sigPDF.GetName(), self.bacPDF.GetName())) ; self.totPDF.SetName('totPDF')

    def UpdatePDFParameters(self, pars, epars):
        for ii, pp in enumerate(pars) : self.totPDF.SetParameter(ii, pp)
        for ii, pp in enumerate(epars): self.totPDF.SetParError(ii, pp)
        
        self.updateComponent(self.sigPDF)
        self.updateComponent(self.bacPDF)

    def GetBacPDF(self): return self.bacPDF
    def GetSigPDF(self): return self.sigPDF
    def GetTotPDF(self): return self.totPDF
##
## private members
    def generatePDF(self, func):
        if   isinstance(func, ROOT.TF1) : return func
        elif isinstance(func, str)      : return ROOT.TF1('tempPDF', func, self.fitRange[0], self.fitRange[1])
        else: raise ValueError('INPUT ERROR SETsignal function')

    def updateComponent(self, pdf):
        for ii, jj in product( range(pdf.GetNpar()), range(self.totPDF.GetNpar())):
            if pdf.GetParName(ii) == self.totPDF.GetParName(jj): 
                pdf.SetParameter(ii, self.totPDF.GetParameter(jj))
                pdf.SetParError(ii, self.totPDF.GetParError(jj))
