from Variable import Variable, ScalarType, VectorType

s1 = ScalarType('x', 'F')
s2 = Variable.fromString('phi/F')
s3 = Variable.fromString('y/I')

print "Scalars:"
print s1
print s2
print s3

print

v1 = VectorType('Jet', ['pt/F', 'eta/F', s2], nMax = 10)
v2 = Variable.fromString('Lepton[pt/F,eta/F,phi/F]')

print "Vectors:"
print v1
print v2
