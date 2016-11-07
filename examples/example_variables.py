''' Little demonstration how to define variables
'''

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
from RootTools.core.standard import *

args = argParser.parse_args()
logger = get_logger(args.logLevel, logFile = None)

s1 = ScalarType('x', 'F')
s2 = TreeVariable.fromString('phi/F')
s3 = TreeVariable.fromString('y/I')

print "Scalars:"
print s1
print s2
print s3

print

v1 = VectorType('Jet', ['pt/F', 'eta/F', s2], nMax = 10)
v2 = TreeVariable.fromString('Lepton[pt/F,eta/F,phi/F]')

print "Vectors:"
print v1
print v2
