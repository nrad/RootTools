import os, shutil
def copyIndexPHP( directory ):
    ''' Copy index.php to directory
    '''
    index_php = os.path.join( directory, 'index.php' )
    if not os.path.exists( directory ): os.makedirs( directory )
    shutil.copyfile( os.path.expandvars( '$CMSSW_BASE/src/RootTools/plot/php/index.php' ), index_php )
    #if not directory[-1] == '/': directory = directory+'/'
    #subdirs = directory.split('/')
    #for i in range(1,len(subdirs)):
    #  p = '/'.join(subdirs[:-i])
    #  index_php = os.path.join( p, 'index.php' )
    #  if os.path.exists( index_php ): break
    #  else:
    #    shutil.copyfile( os.path.expandvars( '$CMSSW_BASE/src/RootTools/plot/php/index.php' ), index_php )
