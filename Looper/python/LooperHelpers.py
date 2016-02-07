# RootTools imports

from RootTools.Variable.Variable import cStringTypeDict, defaultCTypeDict, Variable, VectorType, ScalarType

def getCTypeString(typeString):
    '''Translate ROOT shortcuts for branch description to proper C types
    '''
    if typeString in cStringTypeDict.keys():
        return cStringTypeDict[typeString]
    else:
        raise Exception( "Cann ot determine C type for type '%s'"%typeString )

def getCDefaultString(typeString):
    '''Get default string from ROOT branch description shortcut
    '''
    if typeString in defaultCTypeDict.keys():
        return defaultCTypeDict[typeString]
    else:
        raise Exception( "Can not determine C type for type '%s'"%typeString )

def createClassString(variables, useSTDVectors = False, addVectorCounters = False):
    '''Create class string from scalar and vector variables
    '''

    vectors = [v for v in variables if isinstance(v, VectorType) ]
    scalars = [s for s in variables if isinstance(s, ScalarType) ]

    # Adding default counterVariable 'nVectorname/I' if specified
    if addVectorCounters: scalars += [v.counterVariable() for v in vectors]

    # Create the class string
    scalarDeclaration = "".join(["  %s %s;\n"% ( getCTypeString(scalar.type), scalar.name ) for scalar in scalars])
    scalarInitString  = "".join(["  %s = %s;\n"%( scalar.name, getCDefaultString(scalar.type) ) for scalar in scalars]) 
    vectorDeclaration = ""
    vectorInitString  = ""
    if useSTDVectors:
        for vector in vectors:
            vectorDeclaration += "".join([ "  std::vector< %s > %s_%s;\n" % \
                ( getCTypeString(c.type), vector.name, c.name) for c in vector.components])
            vectorInitString  += "".join([ "  %s_%s.clear();\n" % (vector.name, c.name) for c in vector.components])
    else:
        for vector in vectors:
            if not hasattr( vector, 'nMax' ):
                raise ValueError ("Vector definition needs nMax if using C arrays: %r"%vector)
            vectorDeclaration += "".join([ "  %s %s_%s[%3i];\n" % \
                ( getCTypeString(c.type), vector.name, c.name, vector.nMax) for c in vector.components])
            vectorInitString  += """  for(UInt_t i=0;i<{nMax};i++){{\n{vecCompString}     }}; //End for loop"""\
                .format(nMax = vector.nMax, vecCompString =\
                 "".join([ "  %s_%s[i] = %15s;\n"%(vector.name, c.name, getCDefaultString(c.type)) for c in vector.components]) 
            )

    return \
"""#ifndef __className__
#define __className__

#include<vector>
#include<TMath.h>


class className{{
  public:
{scalarDeclaration}
{vectorDeclaration}
  void init(){{

{scalarInitString}
{vectorInitString}
  }}; // End init
}}; // End class declaration
#endif""".format(scalarDeclaration = scalarDeclaration,\
                 scalarInitString = scalarInitString, vectorDeclaration=vectorDeclaration, 
                 vectorInitString=vectorInitString)
