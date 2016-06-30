import ROOT

def errorStyle( color, markerStyle = 20):
    def func( histo ):
        histo.SetLineColor( color )
        histo.SetMarkerSize( 1 )
        histo.SetMarkerStyle( 20 )
        histo.SetMarkerColor( color )
#        histo.SetFillColor( color )
        histo.SetLineWidth( 1 )
        histo.drawOption = "e1"
        return 
    return func

def lineStyle( color, width = None):
    def func( histo ):
        histo.SetLineColor( color )
        histo.SetMarkerSize( 0 )
        histo.SetMarkerStyle( 0 )
        histo.SetMarkerColor( color )
        histo.SetFillColor( 0 )
        if width: histo.SetLineWidth( width )
        histo.drawOption = "hist"
        return 
    return func

def fillStyle( color, lineColor = ROOT.kBlack ):
    def func( histo ):
        lc = lineColor if lineColor is not None else color
        histo.SetLineColor( lc )
        histo.SetMarkerSize( 0 )
        histo.SetMarkerStyle( 0 )
        histo.SetMarkerColor( lc )
        histo.SetFillColor( color )
        histo.drawOption = "hist"
        return 
    return func
