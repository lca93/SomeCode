import ROOT
import json

from collections import OrderedDict

class FittR():
    def __init__(self, iFile, mainVar, RooVar, binning, den, num, run, varList = []):
        self.iFile = iFile
        self.tree  = iFile.Get('tree')

        self.mainVar = mainVar
        self.binning = binning

        self.den = den
        self.num = num
        self.run = run

        self.RooVar = RooVar

        self.oFile = ROOT.TFile.Open('eff_from_ds.rot', 'RECREATE')
        self.oJson = open('eff_from_ds.json', 'w')
        self.dJson = OrderedDict()

        self.varList = varList
        self.fitVars = []

        self.fitF_pN = None
        self.fitF_fN = None
        self.fitF_DD = None

    def AddVariable(self, var_cpl):
        ## add couple (variable, binning)
        self.varList.append(var_cpl)

    def SetFitF(self, passN, failN, total):
        ## set fit funxtion for pass, fail, total
        self.fitF_pN = passN
        self.fitF_fN = failN
        self.fitF_DD = total

    def load_histo(self, name, cut):
        ## load hist with cut
        self.tree.Draw('%s>>histo%s' % (self.mainVar, self.binning), cut)
        return ROOT.RooDataHist(name, name, ROOT.RooArgList(self.RooVar), ROOT.gDirectory.Get('histo'))

    def BuildGaussian(self, name, mean, sigma):
        ## build a gaussian function from input
        mn = str(mean. split('[')[0])
        sn = str(sigma.split('[')[0])

        mm = [ float(mean .replace('%s[' %mn, '').split(', ')[i].replace(']', '')) for i in range(3)] 
        ss = [ float(sigma.replace('%s[' %sn, '').split(', ')[i].replace(']', '')) for i in range(3)] 

        if self.checkPreDefinition(mn): 
            for vv in self.fitVars: 
                if vv[0].GetName() == mn: mean = vv[0]
        else: mean  = ROOT.RooRealVar(mn, mn, mm[0], mm[1], mm[2]) ; self.SaveVar(mean, mean.getValV())

        if self.checkPreDefinition(sn): 
            for vv in self.fitVars: 
                if vv[0].GetName() == sn: sigma = vv[0]
        else: sigma  = ROOT.RooRealVar(sn, sn, ss[0], ss[1], ss[2]) ; self.SaveVar(sigma, sigma.getValV())

        return ROOT.RooGaussian(name, name, self.RooVar, mean, sigma)

    def BuildPolynomial1(self, name, pars):
        ## build a polynomial of degree 1 from input
        argList = []
        for pp in pars:
            np = pp.split('[')[0]
            rp = [ float(pp.split('[')[1].split(',')[i].replace(']', '')) for i in range(3)]

            if self.checkPreDefinition(np):
                for vv in self.fitVars: 
                    if vv[0].GetName() == np: par = vv[0]
            else: par = ROOT.RooRealVar( np, np, rp[0], rp[1], rp[2]) ;  self.SaveVar(par, par.getValV())

            argList.append(par)

        return ROOT.RooPolynomial(name, name, self.RooVar, ROOT.RooArgList(argList[0], argList[1]))

    def Sum2PDFs(self, name, pdf1, pdf2, yild = 0):
        ## sum two pdfs, can use fied yield
        if not yild: Y = ROOT.RooRealVar ('%s_yield' % name, '%s_yield' % name, 0, 1) ; self.SaveVar(Y, Y.getValV())
        else:        Y = ROOT.RooConstVar('%s_yield' % name, '%s_yield' % name, yild) ; self.SaveVar(Y, Y.getValV())
        return ROOT.RooAddPdf(name, name, pdf1, pdf2, Y)

    def SaveVar(self, var, value):
        ## save var for code stability: RooFit needs this
        self.fitVars.append((var, value))

    def FindVar(self, name):
        ## find RooFit var by name
        for vv in self.fitVars:
            if vv[0].GetName() == name: return vv[0]
        return False

    def ResetVars(self):
        ## reset all variables to teir initial values
        for vv in self.fitVars: 
            vv[0].setVal( vv[1])

    def checkPreDefinition(self, varName):
        ## check whether the variable has already been defined.
        ## avoids redefinition and allows to use the same variable for multiple functions
        for vv in self.fitVars:
            if vv[0].GetName() == varName: return True
        return False

