''' Collection of helpers for usage with cmg
'''
def read_cmg_normalization( file ):
    sumW = None
    allEvents = None
    for line in file:
      if "Sum Weights" in line: sumW = float(line.split()[2])
      if 'All Events'  in line: allEvents = float(line.split()[2])
    if sumW is not None: return sumW
    else:                return allEvents

