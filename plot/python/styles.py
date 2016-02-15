import ROOT

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

def fillStyle( color ):
    def func( histo ):
        histo.SetLineColor( ROOT.kBlack )
        histo.SetMarkerSize( 0 )
        histo.SetMarkerStyle( 0 )
        histo.SetMarkerColor( ROOT.kBlack )
        histo.SetFillColor( color )
        histo.drawOption = "hist"
        return 
    return func
