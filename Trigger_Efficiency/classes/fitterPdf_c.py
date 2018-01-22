import ROOT

class fitterPDF():
    def __init__(self, sigPDF, bacPDF, fitRange):
        self.fitRange = fitRange

        self.sigPDF = self.setSignal( sigPDF)       ;   self.sigPDF.SetName('sigPDF')
        self.bacPDF = self.setBackground( bacPDF)   ;   self.bacPDF.SetName('bacPDF')

    def SetPdfPars(self, sigPars, bacPars):
        for j in range( len(sigPars)):
            if not sigPars[j][0] is None: self.sigPDF.SetParName(j, sigPars[j][0])
            if not sigPars[j][1] is None: self.sigPDF.SetParameter(j, sigPars[j][1])
            if not sigPars[j][2] is None: self.sigPDF.SetParLimits(j, sigPars[j][2][0], sigPars[j][2][1])
        for j in range( len(bacPars)):
            if not bacPars[j][0] is None: self.bacPDF.SetParName(j, bacPars[j][0])
            if not bacPars[j][1] is None: self.bacPDF.SetParameter(j, bacPars[j][1])
            if not bacPars[j][2] is None: self.bacPDF.SetParLimits(j, bacPars[j][2][0], bacPars[j][2][1])

        self.totPDF = self.getTotlPdf()
        self.generateTotlParList()

    def setSignal(self, func):
        if   isinstance(func, ROOT.TF1) : return func
        elif isinstance(func, str)      : return ROOT.TF1('tempSig', func, self.fitRange[0], self.fitRange[1])
        else: raise ValueError('INPUT ERROR SETsignal function')

    def setBackground(self, func):
       if   isinstance(func, ROOT.TF1) : return func
       elif isinstance(func, str)      : return ROOT.TF1('tempBac', func, self.fitRange[0], self.fitRange[1])
       else: raise ValueError('INPUT ERROR SETbackground function')

    def getTotlPdf(self):
        return ROOT.TF1('totlPDF', '+'.join( [self.sigPDF.GetName(), self.bacPDF.GetName()]), self.fitRange[0], self.fitRange[1])   

    def UpdatePDFParameters(self, pars, epars):
        for ii, pp in enumerate(pars): self.totPDF.SetParameter(ii, pp)
        for ii, pp in enumerate(epars): self.totPDF.SetParError(ii, pp)

        self.updateSignal()
        self.updateBackground()

    def GetBacPDF(self): return self.bacPDF
    def GetSigPDF(self): return self.sigPDF
    def GetTotPDF(self): return self.totPDF

    def updateSignal(self):
        for ii, jj in product( range(self.sigPDF.GetNpar()), range(self.totPDF.GetNpar())):
            if self.sigPDF.GetParName() == self.totPDF.GetParName(): 
                self.sigPDF.SetParameter(ii, self.totPDF.GetParameter(ii))
                self.sigPDF.SetParError(ii, self.totPDF.GetParError(ii))

    def updateBackground(self):
        for ii, jj in product( range( self.bacPDF.GetNpar()), range(self.totPDF.GetNpar())):
            if self.bacPDF.GetParName() == self.totPDF.GetParName(): 
                self.bacPDF.SetParameter(ii, self.totPDF.GetParameter(ii))
                self.bacPDF.SetParError(ii, self.totPDF.GetParError(ii))

    def generateTotlParList(self):
        self.iTotlPars = []
        for ii in range( self.totPDF.GetNpar()):
            limUp = ROOT.Double(0)
            limDw = ROOT.Double(0)

            self.totPDF.GetParLimits(ii, limDw, limUp)

            self.iTotlPars.append(  (self.totPDF.GetParName(ii)  ,
                                    self.totPDF.GetParameter(ii) ,
                                    (limDw, limUp)               )              
            )






