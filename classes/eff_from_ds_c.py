import ROOT
import json
import numpy as np

from collections import OrderedDict

class FittR():
    def __init__(self, iFile, varName, nBins, den, num, run, workspace, varList = []):
        self.iFile = iFile
        self.tree  = iFile.Get('tree')

        self.nBins = nBins

        self.workspace = workspace

        self.den   = '%s & %s'           %(den, run)
        self.failN = '%s & %s == 0 & %s' %(den, num, run)
        self.passN = '%s & %s & %s'      %(den, num, run)

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
            cc = ROOT.TCanvas() ; cc.Divide(2,2) ; cc.SetName('%s_bin%s' %(varName, i))

            binRange = self.getBinRange(varName, bins, i)

            framP = self.RooVar.frame()
            framF = self.RooVar.frame()
            framA = self.RooVar.frame()

            passH = self.load_histo('pass_%s_bin%s' %(varName, i), '%s & %s' %(binRange, self.passN)) ; framP.SetTitle('[%s] PASS bin%s'  %(varName, i))
            failH = self.load_histo('fail_%s_bin%s' %(varName, i), '%s & %s' %(binRange, self.failN)) ; framF.SetTitle('[%s] FAIL bin%s'  %(varName, i))
            totlH = self.load_histo('totl_%s_bin%s' %(varName, i), '%s & %s' %(binRange, self.den  )) ; framA.SetTitle('[%s] ALL bin%s'   %(varName, i))

            self.pdfFail.fitTo(failH)
            self.pdfPass.fitTo(passH)  

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
            
            cc.cd(1) ; framP.Draw()
            cc.cd(2) ; framF.Draw()
            cc.cd(3) ; framA.Draw()
            cc.Write()

            jsonOut[self.getBinLabel(i, bins)] = OrderedDict()
            jsonOut[self.getBinLabel(i, bins)]['value'] = 'gino'
            jsonOut[self.getBinLabel(i, bins)]['error'] = 'pino'

            cc.Close()
            self.ReInitVals()

        return jsonOut





