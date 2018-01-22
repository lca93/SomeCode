import ROOT
import json

from collections import OrderedDict

class keyPlotter ():
    def __init__(self, iFile, oName = 'outFile'):
        self.oName = oName  ## string
        self.iFile = iFile
        self.json  = json.load(self.iFile, object_pairs_hook=OrderedDict)
        self.rFile = ROOT.TFile('%s.root' % oName, 'RECREATE')

        self.keyList1D = []
        self.keyList2D = []

        self.currentKey = ''
        self.xArray = OrderedDict()

        self.SetAttributes()
        self.SetOptions()

    def SetAttributes(self, yName = 'efficiency', mStyle = 20, mColor = ROOT.kBlack, lColor = ROOT.kBlack, dOptions1D = 'AP', dOptions2D = 'colz2 text error', separator2D = '__VS__'):
        self.yName   = yName
        self.markerStyle= mStyle
        self.markerColor= mColor
        self.lineColor  = lColor
        self.drawOptions1D = dOptions1D
        self.drawOptions2D = dOptions2D
        self.separator2D = separator2D

    def AddKey(self, keyName, xArray = None, is2D = False):
        if is2D: 
            self.keyList2D.append(keyName)
            self.xArray[keyName] = xArray
        else:    
            self.keyList1D.append(keyName)
            self.xArray[keyName] = xArray

    def SetOptions(self, useXerror = True, useXposArray = False, keySeparator = ','):
        self.useXerror    = useXerror
        self.useXposArray = useXposArray
        self.keySeparator = keySeparator

    def getXposition(self, key, idx):
        if not self.xArray[ self.currentKey] is None: return self.xArray[ self.currentKey][idx]
        return 0.5*(float( key.split( self.keySeparator)[0]) + float( key.split( self.keySeparator)[1]))

    def getXerror(self, key, idx):
        if not self.useXerror: return 0
        return 0.5*(float( key.split( ',')[1]) - float( key.split(',')[0]))        

    def plotOnCanvas(self, obj, opt = ''):
        cVas = ROOT.TCanvas() ; cVas.cd()
        cVas.SetName('%s_cvas' % obj.GetName())
        obj.Draw(opt)
        cVas.Write()
 
    def Plot(self):
        for kk in self.keyList1D: 
            self.currentKey = kk
            self.rFile.cd() ; self.rFile.mkdir(kk) ; self.rFile.cd(kk)
            self.parse1Dkey(dicn = self.json[kk], key = str(kk))
        for kk in self.keyList2D:
            self.currentKey = kk
            self.rFile.cd() ; self.rFile.mkdir(kk) ; self.rFile.cd(kk)
            self.parse2Dkey(dicn = self.json[kk], key = str(kk))
        self.end()

    def parse1Dkey(self, dicn, key):
        graph = ROOT.TGraphErrors()
        
        graph.SetName(key)
        graph.SetTitle('efficiency plot [%s]' % key)
        graph.GetXaxis().SetTitle(key)
        graph.GetYaxis().SetTitle( self.yName)

        graph.SetMarkerStyle( self.markerStyle)
        graph.SetMarkerColor( self.markerColor)
        graph.SetLineColor  ( self.lineColor)

        for ii, kk in enumerate( dicn.keys()):
            graph.SetPoint( ii, 
                            self.getXposition(kk, ii), 
                            dicn[kk]['value']
            )
            graph.SetPointError(    ii, 
                                    self.getXerror(kk, ii), 
                                    dicn[kk]['error']
            )

        graph.Write() ; self.plotOnCanvas(graph, self.drawOptions1D)
        return graph

    def parse2Dkey(self, dicn, key):
        th2 = ROOT.TH2F(    '%s efficiency' % key, '',
                            len( dicn[dicn.keys()[0]].keys()), 0, len( dicn[dicn.keys()[0]].keys()), 
                            len( dicn.keys()), 0, len( dicn.keys())
        )
        th2.GetXaxis().SetTitle( key.split( self.separator2D)[0])
        th2.GetYaxis().SetTitle( key.split( self.separator2D)[1])

        for ii, kk in enumerate(dicn.keys()):
            th2.GetYaxis().SetBinLabel(ii+1, kk)
            for jj, sk in enumerate(dicn[dicn.keys()[0]].keys()): th2.GetXaxis().SetBinLabel(jj+1, sk)

        for ii, kk in enumerate(dicn.keys()):
            self.rFile.GetDirectory(key).mkdir(kk) ; self.rFile.GetDirectory(key).cd(kk)
            graph = self.parse1Dkey(dicn[kk], kk)
            for jj, yy in enumerate(graph.GetY()): 
                th2.SetBinContent(jj+1, ii+1, yy)
                th2.SetBinError(jj+1, ii+1, graph.GetErrorY(jj))

        self.rFile.GetDirectory(key).cd() ; th2.Write() ; self.plotOnCanvas(th2, self.drawOptions2D)


    def end(self):
        self.iFile.close()
        self.rFile.Close()


