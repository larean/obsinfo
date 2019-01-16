""" 
Print complete stations from information in network.yaml file

nomenclature:
    A "measurement instrument" is a means of recording one physical parameter,
        from sensor through dac
    An "instrument" is composed of one or more measurement instruments
        
I need to modify the code so that it treats a $ref as a placeholder for the associated object
"""
# Standard library modules
import math as m
import json
import pprint
import os.path
import sys

# Non-standard modules
import yaml
import obspy.core.util.obspy_types as obspy_types
import obspy.core.inventory as inventory
import obspy.core.inventory.util as obspy_util
from obspy.core.utcdatetime import UTCDateTime

# obsinfo modules
from ..misc.info_files import load_information_file,root_symbol
from ..misc import FDSN
from ..instrument_components import instrument_components as oi_instrument_components

################################################################################       
class instrumentation:
    """ Everything in an instrumentation.yaml file
    
    Functions are very similar to those in instrument_components: should there 
    be a shared class?
    """
    def __init__(self,filename,referring_file=None):
        temp,basepath=load_information_file(filename,referring_file)
        
        self.basepath =        basepath
        self.format_version =  temp['format_version']
        self.revision =        temp['revision']
        self.facility =        temp['instrumentation']['facility']
        self.components_file = temp['instrumentation']['instrument_components']['$ref']
        self.instruments =     temp['instrumentation']['instruments']
        
    def __repr__(self) :
        return "<OBS_Instrumentation: facility={}>".format(\
                    self.facility['reference_name'])  
                      
    def __components_exist(self,components_dict,instrument,components,
                                print_names,debug=False):
        for das_component in instrument['das_components'].values():
            if debug:
                print(yaml.dump(das_component))
            for key,values in das_component.items():
                if "reference_code" in values:
                    ref_code=values["reference_code"]
                    if ref_code in components_dict:
                        components_dict[ref_code]['n_cites']=\
                                            components_dict[ref_code]['n_cites']+1
                    else:
                        components_dict[ref_code]=dict(n_cites=1,
                                                        exists=None,
                                                        component_type=key,
                                                        config_list=False)
                        if debug:
                            print("components=",components)
                        component=components.get_component(key,ref_code)
                        if component:
                            components_dict[ref_code]['exists']=True
                            if type(component)==list:
                                components_dict[ref_code]['config_list']=\
                                        [x[len(ref_code)+1:] for x in component]
                        else:
                            components_dict[ref_code]['exists']=False
        return components_dict
    def print_elements(self,debug=False):
        """ prints all instruments (descriptions and  serial numbers)
        """
        for key,element in sorted(self.instruments['generic'].items()):
            description=None
            if debug:
                print(element)
            if 'equipment' in element:
                equipment=element['equipment']
                if type(equipment) == dict :
                    equipment=FDSN.equipment_type(equipment)
                description = equipment.description
            if not description :
                if 'description' in element:
                    description = element['description']
                else:
                    description = 'None provided'
            SNs=[]
            if 'specific' in self.instruments:
                if key in self.instruments['specific']:
                    SNs= sorted(self.instruments['specific'][key])        
            #output={' model':key,'description':description,'specified_serial_numbers':SNs}
            #print(yaml.dump(output,width=76))
            print(f'{key}: description="{description}", specified_SNs={SNs}')
            
    def verify_individuals(self):
        """ Verify that all "specific" instruments have a generic counterpart
        
            returns true if so, false + error message if not
        """
        checksOut=True
        no_error_for_type=True
        if 'specific' in self.instruments:
            for model in self.instruments['specific'].keys() :
                if model not in self.instruments['generic'] :
                    if no_error_for_type:
                        print('  {:>15}: '.format(block_type),end='')
                        no_error_for_type=False                        
                    checksOut=False
                    print(15*' ' +'"{}" is in "specific" but not in "generic"'.format(model))
        return checksOut
        
    def check_dependencies(self,print_names=False,debug=False):
        """ Verify that the components file exists and contains requested components
        
            Prints out error message if anything fails
            returns:
                file_exists: true if file exists, false otherwise
                components_exist: true if all components exist, false otherwise
                n_components: number of components checked (including repeats)
        """
        comp_file=os.path.join(self.basepath,self.components_file)
        if not os.path.isfile(comp_file) :
            print('Intrument_components file not found: "{}"'.format(comp_file))
            return False,False,None
        components=oi_instrument_components(comp_file)
        if debug:
            print("check_dependencies:components=",components)
        components_dict=dict()
        for instrument in self.instruments['generic'].values():
            if debug:
                print(yaml.dump(instrument))
            components_dict=self.__components_exist(components_dict,
                                                    instrument,
                                                    components,
                                                    print_names)
        total_components=0
        total_found=0
        total_cites=0
        for ref_code,value in sorted(components_dict.items()):
            total_components=total_components+1
            n_cites=value['n_cites']
            total_cites=total_cites+n_cites
            if value['exists']:
                comments=''
                total_found=total_found+1
                if print_names:
                    if n_cites==1:
                        print( '        FOUND ( 1 cite ): {}'.format(ref_code))
                    else:
                        print( '        FOUND ({:2d} cites): {}'.format(n_cites,ref_code))
            else:
                if n_cites==1:
                    print( '    NOT FOUND ( 1 cite ): {}'.format(ref_code))
                else:
                    print( '    NOT FOUND ({:2d} cites): {}'.format(n_cites,ref_code))
        config_header_written=False
        for ref_code,value in sorted(components_dict.items()):
            if value['config_list']:
                if not config_header_written:
                    print(' **Some component citations must be completed in '\
                            'the network.yaml file.')
                    config_header_written = True
                print(' **   - Stations using instruments containing: the {} {}'.format(\
                                                ref_code,
                                                value['component_type']))
                print(' **                              must specify: {}_config'.format(\
                                                value['component_type']))
                print(' **                   using one of the values: {}'.format(\
                                                value['config_list']))
        return True,total_components, total_found, total_cites     
