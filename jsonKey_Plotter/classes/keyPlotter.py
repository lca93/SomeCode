import ROOT
import json

from collections import OrderedDict

class keyPlotter ():
    def __init__(self, iFile, oName = 'outFile'):
        self.oName = oName  
        self.json  = json.load(iFile, object_pairs_hook=OrderedDict)
        self.rFile = ROOT.TFile('%s' % oName, 'RECREATE')

        self.keyList1D = []         ## 1D key lsit
        self.keyList2D = []         ## 2D key list

        self.currentKey = ''        ## key being parsed at a certain step of the code
        self.xArray = OrderedDict() ## array of the x positions of a certain key (info stored as dict for every key)

        self.SetAttributes()        ## init the class attributes
        self.SetOptions()           ## init the class options

    ## set the class attributes used to plot the result
    ##
    def SetAttributes(self, yName = 'efficiency', mStyle = 20, mColor = ROOT.kBlack, lColor = ROOT.kBlack, dOptions1D = 'AP', dOptions2D = 'colz2 text error', separator2D = '__VS__'):
        
        self.yName          = yName         ## name of the Y variable
        self.markerStyle    = mStyle        ## marker style
        self.markerColor    = mColor        ## marker color
        self.lineColor      = lColor        ## line color
        self.separator2D    = separator2D   ## character used to split 2D variables
        self.drawOptions1D  = dOptions1D    ## draw options for 1D variables
        self.drawOptions2D  = dOptions2D    ## draw options for 2D variables

    ## add a json key to be plotted
    ##
    def AddKey(self, keyName, xArray = None, is2D = False):
        if self.is2D: 
            self.keyList2D.append(keyName)
            self.xArray[keyName] = xArray
        else:    
            self.keyList1D.append(keyName)
            self.xArray[keyName] = xArray

    ## set the class options for plotting
    ##
    def SetOptions(self, useXerror = True, useXposArray = False, keySeparator = ','):
        self.useXerror    = useXerror       ## plot x errors as bin width
        self.useXposArray = useXposArray    ## use the xArray definition for the bin center
        self.keySeparator = keySeparator    ## set the json key separator for bin range (e.g. 2.0,2.5)

    ## returns the x position of the selected bin
    ##
    def getXposition(self, key, idx):
        if not self.xArray[self.currentKey] is None: 
            return self.xArray[ self.currentKey][idx]
        return 0.5*(float( key.split( self.keySeparator)[0]) + float( key.split( self.keySeparator)[1]))

    ## returns the x error as bin width
    ## TODO: find a way to plot asymmetric x errors
    ##
    def getXerror(self, key, idx):
        if not self.useXerror: return 0
        return 0.5*(float( key.split( ',')[1]) - float( key.split(',')[0]))        

    ## plot the selected object on a canvas and write it to the output file
    ##
    def plotOnCanvas(self, obj, opt = ''):
        cVas = ROOT.TCanvas() ; cVas.cd()
        cVas.SetName('%s_cvas' % obj.GetName())
        obj.Draw(opt)
        cVas.Write()
 
    ## the main function to be called from outside
    ##
    def Plot(self):
        for kk in self.keyList1D: 
            self.currentKey = kk
            self.rFile.cd() ; self.rFile.mkdir(kk) ; self.rFile.cd(kk)
            self.parse1Dkey(dicn = self.json[kk], key = str(kk))
        for kk in self.keyList2D:
            self.currentKey = kk
            self.rFile.cd() ; self.rFile.mkdir(kk) ; self.rFile.cd(kk)
            self.parse2Dkey(dicn = self.json[kk], key = str(kk))

        self.iFile.close()
        self.rFile.Close()

    ## parse a one-dimensional key and plot it on a TGraph
    ##
    def parse1Dkey(self, dicn, key):
        graph = ROOT.TGraphErrors()     ## output graph on which th ekey is plotted
        
        graph.SetName(key)  
        graph.SetTitle('efficiency plot [%s]' % key)
        graph.GetXaxis().SetTitle(key)
        graph.GetYaxis().SetTitle( self.yName)

        graph.SetMarkerStyle( self.markerStyle)
        graph.SetMarkerColor( self.markerColor)
        graph.SetLineColor  ( self.lineColor)

        for ii, kk in enumerate( dicn.keys()):  ##
            graph.SetPoint( ii, 
                            self.getXposition(kk, ii), 
                            dicn[kk]['value']
            )
            graph.SetPointError(    ii, 
                                    self.getXerror(kk, ii), 
                                    dicn[kk]['error']
            )

        graph.Write()                                   ## write the graph to the output file
        self.plotOnCanvas(graph, self.drawOptions1D)    ## write the graph to the output file as a canvas

        return graph

    ## parse a two-dimensional key and plot it on a 2D histogram
    ##
    def parse2Dkey(self, dicn, key):
        th2 = ROOT.TH2F(    '%s efficiency' % key, '',
                            len( dicn[dicn.keys()[0]].keys()), 0, len( dicn[dicn.keys()[0]].keys()), 
                            len( dicn.keys()), 0, len( dicn.keys())
        ) 
        th2.GetXaxis().SetTitle( key.split( self.separator2D)[0])
        th2.GetYaxis().SetTitle( key.split( self.separator2D)[1])

        for ii, kk in enumerate(dicn.keys()):
            ## set the bin labels
            th2.GetYaxis().SetBinLabel(ii+1, kk)
            for jj, sk in enumerate(dicn[dicn.keys()[0]].keys()): th2.GetXaxis().SetBinLabel(jj+1, sk)
            ## create the root directory
            self.rFile.GetDirectory(key).mkdir(kk) ; self.rFile.GetDirectory(key).cd(kk)
            ## parse the subkey as a 1D key and obtain the corresponding graph
            graph = self.parse1Dkey(dicn[kk], kk)
            ## write the graph content on the TH2 correspondin bin
            for jj, yy in enumerate(graph.GetY()): 
                th2.SetBinContent(jj+1, ii+1, yy)
                th2.SetBinError(jj+1, ii+1, graph.GetErrorY(jj))

        ## write the TH2 on the root file as TH2 and as canvas
        self.rFile.GetDirectory(key).cd()
        th2.Write() 
        self.plotOnCanvas(th2, self.drawOptions2D)


