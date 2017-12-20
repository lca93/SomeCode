import ROOT
import json
import math
import numpy as np

from collections import OrderedDict

class FittR():
    def __init__(self, iFile, varName, nBins, den, num, run, workspace, varList = []):
        self.iFile = iFile
        self.tree  = iFile.Get('tree')

        self.nBins = nBins

        self.workspace = workspace

        self.den   = '%s & %s'      %(den, run)
        self.failN = '%s & %s == 0' %(self.den, num)
        self.passN = '%s & %s'      %(self.den, num)

        self.RooVar    = self.workspace.var(varName)
        self.mainVar   = varName
        self.mainRange = '(%s, %s, %s)' %(nBins, self.RooVar.getMin(), self.RooVar.getMax())

        self.signalPass = self.workspace.pdf('signalPass')
        self.signalFail = self.workspace.pdf('signalFail')
        self.backgroundPass = self.workspace.pdf('backgroundPass')
        self.backgroundFail = self.workspace.pdf('backgroundFail')

        self.pdfPass = None
        self.pdfFail = None
        self.pdfTotl = None

        self.ParseWorkspace()

        self.outFile   = ROOT.TFile.Open('eff_from_ds.root', 'RECREATE')
        self.jsonStruc = OrderedDict()

        self.InitVals = np.array([0]*ROOT.RooArgList(self.workspace.allVars()).getSize(), 'float64')
        self.SaveInitValues()

        self.varList = varList

    def AddVariable(self, var_cpl):
        ## add couple (variable, binning)
        self.varList.append(var_cpl)

    def ParseWorkspace(self):
        ## set fit funxtion for pass, fail, total
        self.workspace.factory('SUM::pdfPass(yieldSignalPass[0,1]*signalPass,backgroundPass)')
        self.workspace.factory('SUM::pdfFail(yieldSignalFail[0,1]*signalFail,backgroundFail)')
        self.workspace.factory('SUM::pdfTotl(yieldPass[0.5]*pdfPass,pdfFail)')
        
        self.pdfPass = self.workspace.pdf('pdfPass')
        self.pdfFail = self.workspace.pdf('pdfFail')
        self.pdfTotl = self.workspace.pdf('pdfTotl')

        self.allRooVars = ROOT.RooArgList(self.workspace.allVars())

    def SaveInitValues(self):
        for i in range( len(self.InitVals)): 
            self.InitVals[i] =  ROOT.RooArgList(self.workspace.allVars())[i].getValV()

    def ReInitVals(self):
        for i in range( len(self.InitVals)):
            ROOT.RooArgList(self.workspace.allVars())[i].setVal( self.InitVals[i])

    def load_histo(self, name, cut):
        ## load hist with cut
        aux = ROOT.TCanvas() ; aux.cd()
        self.tree.Draw('%s>>histo%s' % (self.mainVar, self.mainRange), cut)
        aux.Close()
        return ROOT.RooDataHist(name, name, ROOT.RooArgList(self.RooVar), ROOT.gDirectory.Get('histo'))

    def getBinRange(self, varName, bins, index):
        return '%s >= %s & %s <= %s' %(varName, bins[index], varName, bins[index+1])

    def getBins1D(self, varName):
        for vv, bb in varList: 
            if vv == varName: return bb
        print 'ERROR::variable %s not found' %varName

    def getBinLabel (self, i, bins, sep = ','):
        dwn =  str(bins[i])
        upp =  str(bins[i+1])
        return dwn+sep+upp

    def generateJson(self):
        for vv, bb in self.varList:
            self.outFile.cd() ; self.outFile.mkdir(vv) ; self.outFile.cd(vv)
            self.jsonStruc[vv] = OrderedDict()
            if not isinstance(bb, tuple): self.jsonStruc[vv] = self.getEff(vv, bb)
            else: continue

    def saveResults(self, title):
        jsonFile = open(title, 'w')
        jsonFile.write( json.dumps(self.jsonStruc, indent=4, sort_keys=False))
        
        jsonFile.close()
        self.outFile.Close()

    def getEff(self, varName, bins):
        jsonOut = OrderedDict()

        for i in range( len(bins)-1):
            binRange = self.getBinRange(varName, bins, i)            

            passH = self.load_histo('pass_%s_bin%s' %(varName, i), '%s & %s' %(binRange, self.passN))
            failH = self.load_histo('fail_%s_bin%s' %(varName, i), '%s & %s' %(binRange, self.failN))
            totlH = self.load_histo('totl_%s_bin%s' %(varName, i), '%s & %s' %(binRange, self.den  ))

            if failH.sum(0) > passH.sum(0):
                fitresPass = self.pdfPass.fitTo(passH, ROOT.RooFit.Save())  
                fitresFail = self.pdfFail.fitTo(failH, ROOT.RooFit.Save())
            else:
                fitresFail = self.pdfFail.fitTo(failH, ROOT.RooFit.Save())
                fitresPass = self.pdfPass.fitTo(passH, ROOT.RooFit.Save()) 
        
            ef_er = self.calculateEfficiency(fitresPass, fitresFail, passH, failH)

            jsonOut[self.getBinLabel(i, bins)] = OrderedDict()
            jsonOut[self.getBinLabel(i, bins)]['value'] = ef_er[0]
            jsonOut[self.getBinLabel(i, bins)]['error'] = ef_er[1]
            
            cc = self.plotResults(passH, failH, totlH, varName, i)
            cc.Write()
            cc.Close()

            fitresPass.SetName('FITRES__%s' % cc.GetName()) ; fitresPass.Write()
            fitresFail.SetName('FITRES__%s' % cc.GetName()) ; fitresFail.Write()

            self.ReInitVals()

        return jsonOut

    def plotResults(self, passH, failH, totlH, varName, index):
        can = ROOT.TCanvas() ; can.Divide(2,2) ; can.SetName('%s_bin%s' %(varName, index))

        framP = self.RooVar.frame() ; framP.SetTitle('[%s] PASS bin%s'  %(varName, index))
        framF = self.RooVar.frame() ; framF.SetTitle('[%s] FAIL bin%s'  %(varName, index))
        framA = self.RooVar.frame() ; framA.SetTitle('[%s] ALL bin%s'   %(varName, index))

        passH.plotOn(framP)
        failH.plotOn(framF)
        totlH.plotOn(framA)

        self.pdfPass.plotOn(framP, 
                            ROOT.RooFit.LineColor(ROOT.kGreen)) 
        self.pdfPass.plotOn(framP,
                            ROOT.RooFit.Components('backgroundPass'), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kGreen))
        self.pdfFail.plotOn(framF, 
                            ROOT.RooFit.LineColor(ROOT.kRed)) 
        self.pdfFail.plotOn(framF,
                            ROOT.RooFit.Components('backgroundFail'), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kRed))
        self.pdfTotl.plotOn(framA, ROOT.RooFit.LineColor(ROOT.kBlue))

        can.cd(1) ; framP.Draw()
        can.cd(2) ; framF.Draw()
        can.cd(3) ; framA.Draw()

        return can

    def calculateEfficiency(self, fitresP, fitresF, passH, failH):
        intP = self.pdfPass.createIntegral(ROOT.RooArgSet(self.RooVar)).getValV() * passH.sum(0) 
        intF = self.pdfFail.createIntegral(ROOT.RooArgSet(self.RooVar)).getValV() * failH.sum(0)
        intDen = intP + intF

        errP = self.pdfPass.createIntegral(ROOT.RooArgSet(self.RooVar)).getPropagatedError(fitresP) * passH.sum(0) 
        errF = self.pdfFail.createIntegral(ROOT.RooArgSet(self.RooVar)).getPropagatedError(fitresF) * failH.sum(0) 
        errDen = math.sqrt( errP**2 + errF**2)

        eff = intP/intDen
        err = math.sqrt( (errP/intDen)**2 + (intP*errDen/(intDen**2))**2)

        return eff, err








