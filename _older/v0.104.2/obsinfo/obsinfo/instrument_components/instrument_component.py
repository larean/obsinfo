""" 
Print complete stations from information in network.yaml file

nomenclature:
    A "measurement instrument" is a means of recording one physical parameter,
        from sensor through dac
    An "instrument" is composed of one or more measurement instruments
    
    version 0.99
    
I need to modify the code so that it treats a $ref as a placeholder for the associated object
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

from ..misc.info_files import load_information_file, root_symbol
from ..misc.FDSN import equipment_type as FDSN_equipment_type

################################################################################       
class instrument_component:
    """ One obsinfo instrument component 
    
        Inputs:
            component_dict: generic component dictionary from 
                            instrument_components information file
            
    """
    def __init__(self,component_dict,basepath,
                component_type=None,reference_code=None,
                debug=False):
        """ Inputs:
                component_dict: generic component dictionary from 
                                instrument_components information file
                basepath: full path of directory containing Instrument_Components file
                component_type = component type ('datalogger','preamplifier' or 'sensor')
                reference_code = component reference code
            
        """
        if debug:
            print(basepath)
        self.basepath=basepath
        self.equipment = FDSN_equipment_type(component_dict['equipment'])
        if 'seed_codes' in component_dict:
            self.seed_codes = component_dict['seed_codes']
        self.response_superstages = component_dict['response_stages']
        self.type=component_type
        self.reference_code=reference_code
        self.response=None
        
    def __repr__(self) :
        return "<OBS_Instrument_Component: {}>".format(self.reference_code)
        
    def fill_responses(self,debug=False) :
        """ Fill in instrument responses from references"""
        if debug:
            print("self.response_superstages=",end='')
            print(yaml.dump(self.response_superstages))
        self.__read_response_yamls()
        if debug:
            print("self.response=",end='')
            print(yaml.dump(self.response))
                
    def __read_response_yamls(self,debug=False) : 
        """ READ INSTRUMENT RESPONSES FROM RESPONSE_YAML FILES
    
        Input:
            directory: base directory of response_yaml files
        """
        self.response=list()
        if debug:
            print('{:d} superstage files for the component'.format(len(self.response_superstages)))
        for superstage in self.response_superstages:    
            superstage_file=superstage['$ref']
            if debug:
                print("Reading superstage file {}".format(superstage_file))
            stages,temp=load_information_file(superstage_file+root_symbol+'response/stages',self.basepath)
            for stage in stages:
                # IF STAGE FILTER IS A "$ref", READ AND INJECT THE REFERRED FILE
                if '$ref' in stage['filter']:
                    # READ REFERRED FILE
                    filter_ref = os.path.join(\
                            os.path.split(superstage_file)[0],stage['filter']['$ref'])
                    if debug:
                        print('filter file ref:',filter_ref)
                    filter,temp=load_information_file(filter_ref,self.basepath)
                    # MAKE SURE IT'S THE SAME TYPE, IF SO INJECT
                    stage['filter']=filter
                self.response.append(stage)        
            if debug:
                print("{:d} stages read".format(len(stages)))                
        if debug:
            print("{:d} total stages in component".format(len(self.response)))
            print(yaml.dump(self.response))
