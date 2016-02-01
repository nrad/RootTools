cStringTypeDict = {
    'b': 'UChar_t',
    'S': 'Short_t',
    's': 'UShort_t',
    'I': 'Int_t',
    'i': 'UInt_t',
    'F': 'Float_t',
    'D': 'Double_t',
    'L': 'Long64_t',
    'l': 'ULong64_t',
    'O': 'Bool_t',
}

defaultTypeDict = {
    'b': '0',
    'S': '-1',
    's': '0',
    'I' or s=='int': '-1',
    'i': '0',
    'F' or s=='float': 'TMath::QuietNaN()',
    'D': 'TMath::QuietNaN()',
    'L': '-1',
    'l': '-1',
    'O': '0',
}

def getCTypeString(typeString):
    '''Translate ROOT shortcuts for branch description to proper C types
    '''
    if typeString in cStringTypeDict.keys():
        return cStringTypeDict[typeString]
    else:
        raise Exception( "Cannot determine C type for '%s'"%typeString )

def getCDefaultString(typeString):
    '''Get default string from ROOT branch description shortcut
    '''
    if typeString in defaultTypeDict.keys():
        return defaultTypeDict[typeString]
    else:
        raise Exception( "Cannot determine C type for '%s'"%typeString )

def createClassString(scalars, vectors):

    scalarDeclaration = "".join(["  %15s %s;\n"% ( getCTypeString(scalar['type']), scalar['name'] ) for scalar in scalars])
    scalarInitString  = "".join(["  %15s = %s;\n"%( scalar['name'], getCDefaultString(scalar['type']) ) for scalar in scalars]) 
    vectorDeclaration = ""
    for vector in vectors:
        vectorDeclaration += "".join([ "  %15s %s_%s[%3i];\n"%( getCTypeString(c['type']), vector['name'], c['name'], vector['nMax']) for c in vector['variables']])
    vectorInitString=""
    for vector in vectors:
        vectorInitString  += """  for(UInt_t i=0;i<{nMax};i++){{\n{vecCompString}     }}; //End for loop""".format(nMax = vector['nMax'], vecCompString =\
             "".join([ "  %15s_%s[i] = %15s;\n"%(vector['name'], c['name'], getCDefaultString(c['type'])) for c in vector['variables'] ] ) 
        )

    return \
"""#ifndef __className__\n#define __className__\n\n#include<vector>\n#include<TMath.h>\n\n
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