''' Little demonstration how to define stacks.
Note: A stack is made from Samples (not from histos)
'''

#Standard imports
import ROOT

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
from RootTools.tools.Stack import Stack 
from RootTools.tools.Plot import Plot 
from RootTools.tools.Sample import Sample 
from RootTools.tools.Variable import Variable
from RootTools.tools.logger import get_logger
import RootTools.tools.helpers as helpers
import RootTools.tools.plotting as plotting

args = argParser.parse_args()
logger = get_logger(args.logLevel, logFile = None)

#make samples
s0 = Sample.fromFiles("", "example_data/file_0.root" )
s1 = Sample.fromFiles("", "example_data/file_1.root" , selectionString = 'met_pt>100')

# styles are functions to be executed on the histogram
s0.style = helpers.lineStyle( color = ROOT.kBlue )
s1.style = helpers.lineStyle( color = ROOT.kRed )

# Define the stack 
stack = Stack( [ s0, s1 ], [ s0 ] )

# A variable in the chain
variable  = Variable.fromString( "met_pt/F" )
# A variable with a filler
variable2 = Variable.fromString( "sqrt_met_pt2/F", filler = lambda data:sqrt(data.met_pt**2) )

weight_func = lambda data:data.weight

selectionString = "nJet>0"
selectionString_2 = "nJet>1"


plot1 = Plot(\
    stack = stack,
    variable = Variable.fromString( "met_pt/F" ), 
    binning = [10,0,100], 
    selectionString = selectionString,
    weight = weight_func 
)

plot2 = Plot(\
    stack = stack, 
    variable = Variable.fromString( "met_plus_jet0Pt/F").addFiller( helpers.uses( lambda data:sqrt(data.met_pt + data.Jet_pt[0]), "Jet_pt" ) ), 
# equivalent:
#    variable = Variable.fromString( "met_plus_jet0Pt/F", filler = helpers.uses( lambda data:sqrt(data.met_pt + data.Jet_pt[0]), "Jet_pt" ) ), 
    binning = [10,0,100], 
    selectionString = selectionString,
    weight = weight_func
)

plot3 = Plot(\
    stack = stack, 
    variable = Variable.fromString( "met_plus_jet0Pt/F").addFiller( helpers.uses( lambda data:sqrt(data.met_pt + data.Jet_pt[0]), "Jet_pt" ) ), 
# equivalent:
#    variable = Variable.fromString( "met_plus_jet0Pt/F", filler = helpers.uses( lambda data:sqrt(data.met_pt + data.Jet_pt[0]), "Jet_pt" ) ), 
    binning = [10,0,100], 
    selectionString = selectionString_2,
    weight = weight_func
)

plotting.fill(plot1, plot2, plot3)
