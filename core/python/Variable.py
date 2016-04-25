''' Implementation of scalar and vector types.
Used in the Loopers and for plotting.
'''

# Standard imports
import abc
import uuid

from RootTools.core.helpers import cStringTypeDict, shortTypeDict, defaultCTypeDict

allTypes  = set(cStringTypeDict.keys())
allCTypes = set(cStringTypeDict.values())

class Variable( object ):
    __metaclass__ = abc.ABCMeta
   
    @abc.abstractmethod
    def __init__(self):
        return 

    @classmethod
    def fromString(cls, string, filler = None):
        try:
            return VectorType.fromString(string, filler = filler)
        except ( ValueError, AssertionError ):
            return ScalarType.fromString(string, filler = filler)
    
    def addFiller(self, filler):
        self.filler = filler
        return self

class ScalarType( Variable ):

    def __init__( self, name, tp, filler = None, defaultCString = None):
        ''' Initialize variable. 
            tp: shortcut for ROOT type (b/s/S/I/i/F/D/L/l/O) or the corresponding C ROOT types, 
            'filler': function that fills the variable,
            'defaultCString': value the variable will be initialized with in a string representing  C code (!), 
                i.e. '-1' or 'TMath::QuietNaN()'
        '''
        self.name = name

        if not  tp in allTypes.union( allCTypes ):
            raise ValueError( "Type %r not known"%tp )
        # translate type to short form
        self.tp = tp if tp in allTypes else shortTypeDict[tp]

        self.filler = filler

        # store default
        self.defaultCString = defaultCString if defaultCString is not None else defaultCTypeDict[self.tp]

    @property
    def type(self):
        return self.tp

    @classmethod
    def fromString(cls, string, filler = None):
        '''Create scalar variable from syntax 'name/type'
        '''
        if not type(string)==type(""): raise ValueError( "Expected string got %r"%string )
        string = string.replace(' ', '')
        if not string.count('/')==1:
            raise ValueError( "Could not parse string '%s', format is 'name/type'."%string )

            
        name, tp = string.split('/')
        return cls( name = name, tp = tp, filler = filler)

    @classmethod
    def uniqueFloat(cls):
        return cls(name = "float_"+str(uuid.uuid4()), tp='F', filler = None )

    @classmethod
    def uniqueInt(cls):
        return cls(name = "int_"+str(uuid.uuid4()), tp='I', filler = None )

    def __str__(self):
        if self.filler:
            return "%s(scalar, type: %s, filler)" %(self. name, self.tp)
        else:
            return "%s(scalar, type: %s)" %(self. name, self.tp)

class VectorType( Variable ):

    def __init__( self, name, components, filler = None, nMax = None):
        ''' Initialize variable.
            'components': list of ScalarType 
            'filler': function that fills the vector,
            default is the value the variable will be initialized with,
            nMax is the maximal length of the vector in memory (if not specified: 100)
        '''
        self.name = name
        # Scalar components
        self._components = [ ScalarType.fromString("%s_%s"%(self.name, x) ) if type(x)==type("") else x for x in components ]

        self.filler = filler
        
        self.nMax = int(nMax) if nMax is not None else 100

    @classmethod
    def fromString(cls, string, filler = None, nMax = None):
        '''Create vector variable from syntax 'name[c1/type1,c2/type2,...]'
        '''
        if not type(string)==type(""): raise ValueError( "Expected string got %r"%string )
        string = string.replace(' ', '')

        name_ = string[:string.find("[")]

        ts_ = string[string.find("[")+1:string.find("]")]
        componentStrings_ = ts_.split(',')

        return cls( name = name_, components = componentStrings_, nMax = nMax, filler = filler)

    @property 
    def components(self):
        return self._components

    def counterVariable(self):
        ''' Return a scalar counter variable 'nVectorname/I'
        '''
        return ScalarType('n'+self.name, 'I')

    def __str__(self):
        return "%s(vector[%s], filler: %r, components: %s )" %(self. name, self.nMax, bool(self.filler), ",".join(str(c) for c in self.components) )
