import cast_upgrade_1_6_13 # @UnusedImport
import cast.analysers.dotnet
from cast.analysers import log
import re

class MissingImportsAnalysis(cast.analysers.dotnet.Extension): 
    def __init__(self):        
        self.intermediateFile = None
        self.NbImports = 0
    
    def start_analysis(self, options):
        log.info('Starting Missing DotNet Import Analysis...')
        self.intermediateFile = self.get_intermediate_file("missingDotNetImports.txt")
    
    def end_analysis(self):
        log.info('Imports identified: %d' % self.NbImports)
    
    def start_file(self, _file):
        if _file.get_path() != '':
            log.info('Processing %s ...' % _file.get_path().lower())
            lineNb = 0
            with open(_file.get_path(), 'r') as f:
                for line in f:
                    lineNb +=1
                    #using System.Collections.Generic;
                    matchObj = re.search('^[\s]*using[\s]+([\w\.]+)', line)
                    if matchObj: #import
                        log.info('Import: %s' % matchObj.group(1))
                        self.intermediateFile.write('%s;%s\n' % (_file.get_path().lower(), matchObj.group(1)))
                        self.NbImports += 1
     
            