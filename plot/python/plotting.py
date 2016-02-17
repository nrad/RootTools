''' Create and fill histograms
'''

# Logging
import logging
logger = logging.getLogger(__name__)

# Standard imports
import ROOT
import os
import copy
from math import log

# RootTools
import RootTools.core.Variable as Variable
import RootTools.core.helpers as helpers


def getLegendMaskedArea(legend_coordinates, pad):

    def constrain(x, interval=[0,1]):
        if x<interval[0]: return interval[0]
        elif x>=interval[0] and x<interval[1]: return x
        else: return interval[1]

    return {
        'yLowerEdge': constrain( 1.-(1.-legend_coordinates[1] - pad.GetTopMargin())/(1.-pad.GetTopMargin()-pad.GetBottomMargin()), interval=[0.3, 1] ),
        'xLowerEdge': constrain( (legend_coordinates[0] - pad.GetLeftMargin())/(1.-pad.GetLeftMargin()-pad.GetRightMargin()), interval = [0, 1] ),
        'xUpperEdge':constrain( (legend_coordinates[2] - pad.GetLeftMargin())/(1.-pad.GetLeftMargin()-pad.GetRightMargin()), interval = [0, 1] )
        }

def fill(plots, read_variables = [], reduce_stat = 1):
    '''Create and fill all plots
    '''

    # Unique list of selection strings
    selectionStrings    = list(set(p.selectionString for p in plots))
    # Convert extra arguments from text to Variable instance
    read_variables      = list(helpers.fromString(read_variables))

    for selectionString in selectionStrings:
        logger.info( "Now working on selection string %s"% selectionString )

        # find all plots with current selection
        plots_for_selection = [p for p in plots if p.selectionString == selectionString]

        # Find all samples we have to loop over
        samples = list(set(sum([p.stack.samples() for p in plots_for_selection], [])))
        logger.info( "Found %i different samples for this selectionString."%len(samples) )

        # Give histos to plot
        for p in plots_for_selection:
            p.histos = p.stack.make_histos(p)

        for sample in samples:
            logger.info( "Now working on sample %s" % sample.name )
            # find all plots whose stack contains the current sample
            plots_for_sample = [p for p in plots_for_selection if sample in p.stack.samples()]

            # find the positions (indices)  of the stack in each plot
            for plot in plots_for_sample:
                plot.sample_indices = plot.stack.getSampleIndicesInStack(sample)

            # Make reader
            chain_variables  = list(set([p.variable for p in plots_for_sample if p.variable.filler is None]))
            filled_variables = list(set([p.variable for p in plots_for_sample if p.variable.filler is not None]))

            # Create reader and run it over sample, fill the plots
            r = sample.treeReader( variables = read_variables + chain_variables, filled_variables = filled_variables, selectionString = selectionString)

            # reducing event range
            evt_range = r.reduceEventRange(reduce_stat)

            sample_scale = sample.scale(sample) if  hasattr(sample, "scale") else 1

            r.start()
            while r.run():
                for plot in plots_for_sample:
                    for index in plot.sample_indices:

                        weight = 1 if plot.weight is None else plot.weight(r.data)
                        val = plot.variable.filler(r.data) if plot.variable.filler else getattr(r.data, plot.variable.name)
                        plot.histos[index[0]][index[1]].Fill(val, weight*sample_scale)

            # Clean up
            for plot in plots_for_sample:
                del plot.sample_indices
            r.cleanUpTempFiles()

def draw(plot, yRange = "auto", extensions = ["pdf", "png", "root"], plot_directory = ".", logX = False, logY = True, ratio = None, sorting = False, legend = "auto"):

    # FIXME -> Introduces CMSSW dependence
    ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/RootTools/plot/scripts/tdrstyle.C")
    ROOT.setTDRStyle()
    defaultRatioStyle = {'num':1, 'den':0, 'logY':False, 'style':None, 'texY': 'Data / MC', 'yRange': (0.5, 1.5)}
    if ratio is not None and not type(ratio)==type({}):
        raise ValueError( "'ratio' must be dict (default: {}). General form is {'num':1, 'den':0, 'logY':bool, 'style':style funcion, 'texY': 'Data / MC', 'yRange': (0.5, 1.5)}." )
    if ratio is not None and len(plot.stack)<2:
        raise ValueError( "Need at least 2 components in stack to make ratio. Got %i."%len(plot.stack) )

    # Make sure ratio dict has all the keys by updating the default
    if ratio is not None:
        defaultRatioStyle.update(ratio)
        ratio = defaultRatioStyle

    # Make canvas and if there is a ratio plot adjust the size of the pads
    y_width = 500
    y_ratio = 200
    if ratio is not None:
        y_width += y_ratio
        scaleFacRatioPad = y_width/float(y_ratio)
        y_border = y_ratio/float(y_width)

    c1 = ROOT.TCanvas("ROOT.c1","drawHistos",200,10,500, y_width)

    if ratio is not None:
        c1.Divide(1,2,0,0)
        topPad = c1.cd(1)
        topPad.SetBottomMargin(0)
        topPad.SetLeftMargin(0.15)
        topPad.SetTopMargin(0.07)
        topPad.SetRightMargin(0.05)
        topPad.SetPad(topPad.GetX1(), y_border, topPad.GetX2(), topPad.GetY2())
        bottomPad = c1.cd(2)
        bottomPad.SetTopMargin(0)
        bottomPad.SetRightMargin(0.05)
        bottomPad.SetLeftMargin(0.15)
        bottomPad.SetBottomMargin(scaleFacRatioPad*0.13)
        bottomPad.SetPad(bottomPad.GetX1(), bottomPad.GetY1(), bottomPad.GetX2(), y_border)
    else:
        topPad = c1
        topPad.SetBottomMargin(0.13)
        topPad.SetLeftMargin(0.15)
        topPad.SetTopMargin(0.07)
        topPad.SetRightMargin(0.05)

    topPad.cd()

    # Clone (including any attributes) and add up histos in stack
    histos = map(lambda l:map(lambda h:helpers.clone(h), l), plot.histos)
    for i, l in enumerate(histos):

        # recall the sample for use in the legend
        for j, h in enumerate(l):
            h.sample = plot.stack[i][j]

        # sort 
        if sorting:
            l.sort(key=lambda h: -h.Integral())

        # Add up stacks
        for j, h in enumerate(l):
            for k in range(j+1, len(l) ):
                l[j].Add(l[k])

    # Range on y axis: Start with default
    if not yRange=="auto" and not (type(yRange)==type(()) and len(yRange)==2):
        raise ValueError( "'yRange' must bei either 'auto' or (yMin, yMax) where yMin/Max can be 'auto'. Got: %r"%yRange )

    max_ = max( l[0].GetMaximum() for l in histos )
    min_ = min( l[0].GetMinimum() for l in histos )

    #Calculate legend coordinates in gPad coordinates
    if legend is not None:
        if legend=="auto":
            legendCoordinates = (0.50,0.93-0.05*sum(map(len, plot.stack)),0.95,0.93)
        else:
            legendCoordinates = legend 

    if logY:
        yMax_ = 10**0.5*max_
        yMin_ = 0.7
    else:
        yMax_ = 1.2*max_
        yMin_ = 0 if min_>0 else 1.2*min_
    if type(yRange)==type(()) and len(yRange)==2:
        yMin_ = yRange[0] if not yRange[0]=="auto" else yMin_
        yMax_ = yRange[1] if not yRange[1]=="auto" else yMax_

    #Avoid overlap with the legend
    if yRange=="auto" or yRange[1]=="auto":
        scaleFactor = 1
        # Get x-range and y
        legendMaskedArea = getLegendMaskedArea(legendCoordinates, topPad)
        for i, l in enumerate(histos):
            histo = histos[i][0]
            for i_bin in range(1, 1 + histo.GetNbinsX()):
                # low/high bin edge in the units of the x axis
                xLowerEdge_axis, xUpperEdge_axis = histo.GetBinLowEdge(i_bin), histo.GetBinLowEdge(i_bin)+histo.GetBinWidth(i_bin) 
                # linear transformation to gPad system
                xLowerEdge  = (xLowerEdge_axis  -  histo.GetXaxis().GetXmin())/(histo.GetXaxis().GetXmax() - histo.GetXaxis().GetXmin())
                xUpperEdge  = (xUpperEdge_axis -  histo.GetXaxis().GetXmin())/(histo.GetXaxis().GetXmax() - histo.GetXaxis().GetXmin())
                # maximum allowed fraction in given bin wrt to the legendMaskedArea: Either all (1) or legendMaskedArea['yLowerEdge']
                maxFraction = legendMaskedArea['yLowerEdge'] if xUpperEdge>legendMaskedArea['xLowerEdge'] and xLowerEdge<legendMaskedArea['xUpperEdge'] else 1
                # Save 20%
                maxFraction*=0.8
                # Use: (y - yMin_) / (sf*yMax_ - yMin_) = maxFraction (and y->log(y) in log case). 
                # Compute the maximum required scale factor s. 
                y = histo.GetBinContent(i_bin)
                if logY:
                    new_sf = yMin_/yMax_*(y/yMin_)**(1./maxFraction) if y>0 else 1 
                else:
                    new_sf = 1./yMax_*(yMin_ + (y-yMin_)/maxFraction ) 

                scaleFactor = new_sf if new_sf>scaleFactor else scaleFactor
                # print i_bin, xLowerEdge, xUpperEdge, 'yMin', yMin_, 'yMax', yMax_, 'y', y, 'maxFraction', maxFraction, scaleFactor, new_sf

        # Apply scale factor to avoid legend
        yMax_ = scaleFactor*yMax_

    # Draw the histos
    same = ""
    for i, l in enumerate(histos):
        for j, h in enumerate(l):
            # Get draw option. Neither Clone nor copy preserves attributes of histo
            drawOption = histos[i][j].drawOption if hasattr(histos[i][j], "drawOption") else "hist"
            topPad.SetLogy(logY)
            topPad.SetLogx(logX)
            h.GetYaxis().SetRangeUser(yMin_, yMax_)
            h.GetXaxis().SetTitle(plot.texX)
            h.GetYaxis().SetTitle(plot.texY)
            if ratio is None:
                h.GetXaxis().SetTitleSize(0.045)
                h.GetYaxis().SetTitleSize(0.045)
                h.GetYaxis().SetLabelSize(0.045)
                h.GetXaxis().SetLabelSize(0.045)
                h.GetYaxis().SetTitleOffset(1.2)
                h.GetXaxis().SetTitleOffset(1.1)
            else:
                h.GetYaxis().SetTitleSize(0.045)
                h.GetYaxis().SetLabelSize(0.045)
                h.GetYaxis().SetTitleOffset(1.2)

            h.Draw(drawOption+same)
            same = "same"

    topPad.RedrawAxis()
    # Make the legend
    if legend is not None:
        legend_ = ROOT.TLegend(*legendCoordinates)
        legend_.SetFillColor(0)
        legend_.SetShadowColor(ROOT.kWhite)
        legend_.SetBorderSize(0)
        legend_.SetBorderSize(1)
        for l in histos:
            for h in l:
                legend_text = h.sample.texName if hasattr(h.sample, "texName") else h.sample.name
                legend_.AddEntry(h, legend_text)
        legend_.Draw()

    # Make a ratio plot
    if ratio is not None:
        bottomPad.cd()
        num = histos[ratio['num']][0]
        h_ratio = helpers.clone(num)
        h_ratio.Divide(histos[ratio['den']][0])

        if ratio['style'] is not None: ratio['style'](h_ratio) 

        h_ratio.GetXaxis().SetTitle(plot.texX)
        h_ratio.GetYaxis().SetTitle(ratio['texY'])

        h_ratio.GetXaxis().SetTitleSize( 0.12 )
        h_ratio.GetYaxis().SetTitleSize( 0.12 )

        h_ratio.GetXaxis().SetLabelSize( 0.11 )
        h_ratio.GetYaxis().SetLabelSize( 0.11 )


        h_ratio.GetXaxis().SetTickLength( 0.03*3 )
        h_ratio.GetYaxis().SetTickLength( 0.03*2 )

        h_ratio.GetXaxis().SetTitleOffset( 1.1 )
        h_ratio.GetYaxis().SetTitleOffset( 1.6/scaleFacRatioPad )

        h_ratio.GetYaxis().SetRangeUser( *ratio['yRange'] )
        h_ratio.GetYaxis().SetNdivisions(505)

        drawOption = h_ratio.drawOption if hasattr(h_ratio, "drawOption") else "hist"
        h_ratio.Draw(drawOption)

        line = ROOT.TPolyLine(2)
        line.SetPoint(0, h_ratio.GetXaxis().GetXmin(), 1.)
        line.SetPoint(1, h_ratio.GetXaxis().GetXmax(), 1.)
        line.SetLineWidth(1)
        line.Draw()

    for extension in extensions:
        c1.Print( os.path.join( plot_directory, "%s.%s"%(plot.variable.name, extension) ) )

    del c1
