'''
Created on Jun 17, 2021

@author: JGD
'''
import re
import cast_upgrade_1_6_13 # @UnusedImport
import logging
from cast.application import ApplicationLevelExtension, create_link
from cast.application import CustomObject

class LinkObject:
    def __init__(self, linkType, callerObject, calledObject):
        self.linkType = linkType
        self.callerObject = callerObject
        self.calledObject = calledObject

class ReqCodeApplication(ApplicationLevelExtension):
    def __init__(self):      
        self.nbNewClasses = 0
        self.nbNewLinks = 0
        #loading the Msg and Procs objects
        self.dotNetFiles = {}
        self.clsOrInt = {}
        self.linkObjects = []
        self.project = None
        
    '''
    def end_application(self, application):
        logging.info('Missing DotNet Imports - End Application')
        for linkObject in self.linkObjects:
            create_link(linkObject.linkType, linkObject.callerObject, linkObject.calledObject)
            self.nbNewLinks += 1
        
        logging.info('New Links: %d' % self.nbNewLinks)    
    '''
    
    def end_application_create_objects(self, application):
        logging.info('Missing DotNet Imports - End Application Create Objects')
        
        self.load_dotnet_files(application)
        self.load_classes_and_interfaces(application)
        
        for pro in application.get_projects():
            if pro.get_type() == 'CAST_DotNet_Project':
                logging.info("found DotNet Project")
                self.project = pro
                break
        
        try:
            self.parent_to_set_to_unknown_db_name = self.parent_to_set_to_unknown_dbobj.get_name()
        except:
            pass
        
        with self.get_intermediate_file("missingDotNetImports.txt") as f:
            for line in f:
                callerFilename, calledFullname = line.strip().split(";")
                #logging.info("(%s) %s -> %s " % (callerType, callerFullname, calledFullname))
                if calledFullname not in self.clsOrInt:
                    #logging.info('%s does not exists -> create missing object' % calledFullname)
                    missingClass = self.create_missing_class(calledFullname)
                    self.clsOrInt[calledFullname] = missingClass
                else:
                    missingClass = self.clsOrInt[calledFullname]

                if callerFilename not in self.dotNetFiles:
                    logging.warning('%s does not exists - WTF?' % callerFilename)
                else:
                    callerFileObj = self.dotNetFiles[callerFilename]
                    for subObj in callerFileObj.load_objects():
                        if subObj.is_class():
                            self.linkObjects.append(LinkObject('relyonLink', subObj, missingClass))
                            break
                        
        logging.info('New Missing Classes: %d' % self.nbNewClasses)
        
        for linkObject in self.linkObjects:
            create_link(linkObject.linkType, linkObject.callerObject, linkObject.calledObject)
            self.nbNewLinks += 1
        
        logging.info('New Links: %d' % self.nbNewLinks) 
    
    def create_missing_class(self, fullname):              
        newClass = CustomObject()
        #newClass.set_guid(fullname)
        newClass.set_name(self.get_name_from_fullname(fullname))
        newClass.set_fullname(fullname)
        newClass.set_type('UnknownDotNetClass')
        newClass.set_parent(self.project)
        logging.info('New Class: %s - %s' % (self.get_name_from_fullname(fullname), fullname))
        #newClass.set_external()
        newClass.save()
        self.nbNewClasses += 1
        return newClass
    
    def get_name_from_fullname(self, fullname):
        matchObj = re.search("[\.]*([^\.]+)$", fullname)
        if matchObj:
            return matchObj.group(1)
        else:
            logging.warning('Could not extract name from |%s|' % fullname)
            return fullname
    
    def load_dotnet_files(self, application):
        for target in application.get_files(languages=['CAST_DotNet_SourceFile', 'CAST_DotNet_CSharpFile', 'CAST_DotNet_VBNetFile'], external=True):
            self.dotNetFiles[target.get_path().lower()] = target   
        
        #logging.info('Files: %d' % len(self.dotNetFiles))         
         
    def load_classes_and_interfaces(self, application):   

        for target in application.objects().has_type(['CAST_DotNet_VB', 'CAST_DotNet_DotNet', 'CAST_DotNet_CSharp']).is_class():
            self.clsOrInt[target.get_fullname()] = target
        
        #logging.info('Classes and Interfaces: %d' % len(self.clsOrInt))

            