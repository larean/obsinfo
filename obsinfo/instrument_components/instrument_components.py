""" 
nomenclature:
    A "measurement instrument" is a means of recording one physical parameter,
        from sensor through dac
    An "instrument" is composed of one or more measurement instruments
"""
# Standard library modules
import math as m
import os.path
import sys

# Non-standard modules
import yaml
import obspy.core.util.obspy_types as obspy_types
import obspy.core.inventory as inventory
import obspy.core.inventory.util as obspy_util
from obspy.core.utcdatetime import UTCDateTime

# obsinfo modules
from ..misc.info_files import load_information_file
from ..misc.FDSN import equipment_type as FDSN_equipment_type
from .instrument_component import instrument_component as oi_instrument_component

        
################################################################################       
class instrument_components:
    """ Everything in a instrument_components information file"""
    def __init__(self,filename,referring_file=None,debug=False):
        """ Read instrument_components information file"""
        temp,basepath=load_information_file(filename,referring_file)
        if debug:
            print(basepath)
        self.basepath=basepath
        self.filename=filename
        self.revision=temp['revision']
        self.format_version=temp['format_version']
        #self.facility_reference_name=temp['facility_reference_name']
        self.instrument_blocks=temp['instrument_components']['instrument_blocks']
        
    def __repr__(self) :
        return "<instrument_components: {}>".format(self.filename)    
                    
    def __load_specific_component(self,component,serial_number,debug=False):
        if not 'specific' in self.instrument_blocks[component.type]:
            return component
        elif not serial_number in self.instrument_blocks[component.type]['specific']:
            return component
        specific=self.instrument_blocks[component.type]['specific'][serial_number]
        if debug:
            print("[{}][{}]=".format(component.type,serial_number))
            print("specific=",specific)
        if 'response' in specific:
            for key in specific['response']:
                component['response'][key]=specific['response'][key] 
        if 'equipment' in specific:
            component.equipment.merge(FDSN_equipment_type(specific['equipment'])) 
        return component    
                
    def __check_response_files(self,files_dict,component_dict,resp_dir,
                                            print_names,debug=False):
        if debug:
            print(files_dict)
            print(component_dict)
        if 'generic' in component_dict:
            for component in component_dict['generic'].values():
                files_dict=self.__test_response_files(\
                                        files_dict,
                                        component,
                                        resp_dir,
                                        print_names)
        else:
            print('No generic objects for component type "{}"'.format(\
                                block_type))
        if 'specific' in component_dict:
            for model in component_dict['specific'].values():
                for component in model.values():
                    files_dict= \
                        self.__test_response_files( \
                                        files_dict,
                                        component,
                                        resp_dir,
                                        print_names)
        return files_dict  
             
    def __test_response_files(self,files_dict,component,resp_dir,print_names,
                                debug=False):
#         if debug:
#             print('')
#             print(component)
        if 'response_stages' in component:
            for file_ref in component['response_stages']:
                if debug:
                    print(file_ref)
                filename=file_ref['$ref']
                if filename in files_dict:
                    files_dict[filename]['n_cites']=\
                                        files_dict[filename]['n_cites']+1
                else:
                    files_dict[filename]=dict(n_cites=1,exists=None)
                    if not os.path.isfile(os.path.join(resp_dir,filename)):
                        files_dict[filename]['exists']=False
                    else:
                        files_dict[filename]['exists']=True
        return files_dict
    def get_component(self,block_type, reference_code, serial_number=None,
                        get_responses=True):
        """ get one instrument_component
    
            inputs:
                block_type: 'datalogger','preamplifier' or 'sensor'
                reference_code:
                serial_number: optional
                get_responses: return with responses filled in [True]
            output:
                instrument_component: OBS_Instrument_Component object 
                                            OR 
                                      list of possible component names
        """    
        if reference_code not in self.instrument_blocks[block_type]['generic']:
            code_list=[]
            for generic_code in  self.instrument_blocks[block_type]['generic']:
                if (reference_code+'_') in generic_code:
                    code_list.append(generic_code)
            if not code_list:
                code_list=None
            return code_list    
        # LOAD GENERIC COMPONENT    
        component= oi_instrument_component( \
                self.instrument_blocks[block_type]['generic'][reference_code],
                self.basepath)
        component.reference_code=reference_code
        component.type=block_type
        if serial_number:
            component.equipment.serial_number=serial_number
            # LOAD SPECIFIC COMPONENT, IF IT EXISTS
            component=self.__load_specific_component(component,serial_number)
        return component
    def print_elements(self,elem_type):
        """ prints one type of InstrumentComponent (descriptions and  serial numbers)
        type = ('sensor', "preamplifier' or 'datalogger')
        """
        for key,element in sorted(self.instrument_blocks[elem_type]['generic'].items()):
            description=None
            if 'equipment' in element:
                equipment=element['equipment']
                if type(equipment) == dict :
                    equipment=FDSN_equipment_type(equipment)
                description = equipment.description
            if not description:
                if 'description' in element:
                    description = element['description']
                else:
                    description = 'None provided'
            SNs=[]
            if 'specific' in self.instrument_blocks[elem_type]:
                if key in self.instrument_blocks[elem_type]['specific']:
                    SNs= sorted(self.instrument_blocks[elem_type]['specific'][key])        
            #output={'    model':key,'description':description,'specified_serial_numbers':SNs}
            #print(yaml.dump(output,indent=10,width=80))
            print(f'{key}: description="{description}", specified_SNs={SNs}')
            
    def verify_individuals(self):
        """ Verify that all "specific" instruments have a generic counterpart
        
            returns true if so, false + error message if not
        """
        checksOut=True
        for block_type in sorted(self.instrument_blocks.keys()):
            subcomponents=self.instrument_blocks[block_type]
            if 'specific' in subcomponents:
                no_error_for_type = True
                for model in subcomponents['specific'].keys() :
                    if model not in subcomponents['generic'] :
                        if no_error_for_type:
                            print('  {:>15}: '.format(block_type),end='')                        
                            no_error_for_type = False
                        checksOut=False
                        print(15*' ' +'"{}" is in "specific" but not in \
                                    "generic"'.format(model))
        return checksOut
        
    def verify_source_files(self,print_names=False,debug=False):
        """ Verify that all response files exist
        
            returns true if so, false + error message if not
            also returns number of files listed
        """
        print('Searching for response files')
        files_dict=dict()
        for block_type in self.instrument_blocks:
            files_dict = self.__check_response_files(\
                                files_dict,
                                self.instrument_blocks[block_type],
                                self.basepath,
                                print_names)
        if debug:
            print(files_dict)
        total_files=0
        total_found=0
        total_cites=0
        for filename,value in sorted(files_dict.items()):
            total_files=total_files+1
            n_cites=value['n_cites']
            total_cites=total_cites+n_cites
            if value['exists']:
                total_found=total_found+1
                if print_names:
                    if n_cites==1:
                        print( '        FOUND ( 1 cite ): {}'.format(filename))
                    else:
                        print( '        FOUND ({:2d} cites): {}'.format(n_cites,filename))
            else:
                if n_cites==1:
                    print( '    NOT FOUND ( 1 cite ): {}'.format(filename))
                else:
                    print( '    NOT FOUND ({:2d} cites): {}'.format(n_cites,filename))
        return total_files,total_found,total_cites 
