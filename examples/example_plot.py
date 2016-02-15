''' Little demonstration how to define stacks.
Note: A stack is made from Samples (not from histos)
'''

#Standard imports
import ROOT
from math import sqrt, cos

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel', 
      action='store',
      nargs='?',
      choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],
      default='INFO',
      help="Log level for logging"
)

# RootTools
from RootTools.plot.Stack import Stack 
from RootTools.plot.Plot import Plot 
from RootTools.core.Sample import Sample 
from RootTools.core.Variable import Variable
from RootTools.core.logger import get_logger
import RootTools.core.helpers as helpers
import RootTools.plot.styles as styles
import RootTools.plot.plotting as plotting

args = argParser.parse_args()
logger = get_logger(args.logLevel, logFile = None)

#make samples
s0 = Sample.fromFiles("", "example_data/file_0.root" )
s1 = Sample.fromFiles("", "example_data/file_1.root" , selectionString = 'met_pt>100')
s2 = Sample.fromFiles("", "example_data/file_2.root" , selectionString = 'met_pt>100')

# styles are functions to be executed on the histogram
s0.style = styles.lineStyle( color = ROOT.kBlue )
s1.style = styles.lineStyle( color = ROOT.kRed )
s1.style = styles.fillStyle( color = ROOT.kGreen )

# scaling a sample
sample_weight = lambda sample:2
s2.scale = sample_weight

# Define the stack 
stack = Stack( [ s0, s1], [ s2 ] )

# A variable in the chain
variable  = Variable.fromString( "met_pt/F" )
# A variable with a filler
variable2 = Variable.fromString( "sqrt_met_pt2/F", filler = lambda data:sqrt(data.met_pt**2) )

plot_weight   = lambda data:1

selectionString = "nJet>0"
selectionString_2 = "nJet>1"

read_variables =  ["Jet[pt/F]", "met_pt/F"]

plot1 = Plot(\
    stack = stack,
    variable = Variable.fromString( "met_pt/F" ), 
    binning = [10,0,100], 
    selectionString = selectionString,
    weight = plot_weight 
)

plot2 = Plot(\
    stack = stack, 
    variable = Variable.fromString( "met_plus_jet0Pt/F").addFiller( lambda data:sqrt(data.met_pt + data.Jet_pt[0]) ), 
    binning = [10,0,100], 
    selectionString = selectionString,
    weight = plot_weight
)

cosMetPhi = Variable.fromString('cosMetPhi/F') 
cosMetPhi.filler = helpers.uses(lambda data: cos( data.met_phi ) , "met_phi/F")
plot3 = Plot(\
    stack = stack, 
    variable = cosMetPhi, 
    binning = [10,-1,1], 
    selectionString = selectionString,
    weight = plot_weight,
    texX = "cos(#phi(#slash{E}_{T}))",
    texY = "Number of Events "
)

plotting.fill([plot1, plot2, plot3], read_variables = read_variables)
plotting.draw(plot3)
