""" 
Print complete stations from information in network.yaml file

nomenclature:
    A "measurement instrument" is a means of recording one physical parameter,
        from sensor through dac
    An "instrument" is composed of one or more instruments
"""
# Standard library modules
import math as m
import json
import pprint
import os.path

# Non-standard modules
import yaml
import obspy.core.util.obspy_types as obspy_types
import obspy.core.inventory as inventory
import obspy.core.inventory.util as obspy_util
from obspy.core.utcdatetime import UTCDateTime

root_symbol='$'

################################################################################       
    
class OBS_Network:
    """ Everything contained in a network.yaml file
    
        Contains two subclasses:
            stations (type OBS_Station)
            network_info (type FDSN_Network_Info)
    """
    def __init__(self,filename,referring_file=None,debug=False):
        """ Reads from a network.yaml file 
        
        should also be able to specify whether or not it has read its sub_file
        """
        temp,path=load_yaml(filename+root_symbol+'network',referring_file) 
        self.basepath=path
        self.revision=temp['revision'].copy()
        self.facility=temp['facility']
        self.network_info=FDSN_NetworkInfo(temp['network_info'])
        self.instrumentation_file=temp['instrumentation_file'] 
        self.stations=dict()
        for key,station in temp['stations'].items():
            self.stations[key]=OBS_Station(station, key, self.network_info.code)
            if debug:
                print(self.stations[key])
                
    def __repr__(self) :
        return "<OBS_Network: code={}, facility={}, {:d} stations>".format(
                self.network_info.code,self.facility,len(self.stations))
                
    def make_obspy_inventory(self,stations=None,source=None,debug=False):
        """
        Make an obspy inventory object with a subset of stations
        
        stations = list of obs-info.OBS-Station objects
        source  =  value to put in inventory.source
        """
        my_net=self.make_obspy_network(stations)
        if not source:
            source = self.revision['author']['first_name'] + ' ' + self.revision['author']['last_name']
        my_inv = inventory.inventory.Inventory([my_net],source)
        return my_inv
        
    def make_obspy_network(self,stations,debug=False):
        """Make an obspy network object with a subset of stations"""
        obspy_stations=[]    
        for station in stations:
            obspy_stations.append(station.make_obspy_station())
    
        temp=self.network_info.comments
        if temp:
            comments=[]
            for comment in temp:
                comments.append(obspy_util.Comment(comment))
        my_net = inventory.network.Network(
                            self.network_info.code,
                            obspy_stations,
                            description = self.network_info.description,
                            comments =    comments,
                            start_date =  self.network_info.start_date,
                            end_date   =  self.network_info.end_date
                        )
        return my_net
        
    def make_oca_dict(self,referring_file=None,debug=False):
        """Make an oca JSON string """
        if debug:
            print(self)
        for station_code,station in self.stations.items():
            if debug:
                print(station_code)
                print("A:",station.comments)
            station.partial_fill_instrument(self.instrumentation_file,
                                    referring_file=referring_file)
            if debug:
                print("B:", station.comments)
            #self.stations[station_code]=station
        if debug:
            for key,station in self.stations.items():
                print(station.comments)
        oca_net=OCA_Network(self)
        #pprint.pprint(oca_net.dict)
        if debug:
            print(yaml.dump(oca_net.dict))
        return oca_net.dict

################################################################################       
class OBS_Instrumentation:
    """ Everything in an instrumentation.yaml file
    
    Functions are very similar to those in instrument_components: should there 
    be a shared class?
    """
    def __init__(self,filename,referring_file=None):
        temp,basepath=load_yaml(filename+root_symbol+'instrumentation',
                        referring_file)
        self.basepath=basepath
        self.revision=temp['revision']
        self.facility=temp['facility']
        self.components_file=temp['components_file']
        self.instruments=temp['instruments']
        
    def __repr__(self) :
        return "<OBS_Instrumentation: facility={}>".format(\
                    self.facility['reference_name'])  
                      
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
                    equipment=FDSN_EquipmentType(equipment)
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
            output={' model':key,'description':description,'specified_serial_numbers':SNs}
            print(yaml.dump(output,width=76))
            
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
                        print('  {:>15}: '.format(component_type),end='')
                        no_error_for_type=False                        
                    checksOut=False
                    print(15*' ' +'"{}" is in "specific" but not in "generic"'.format(model))
        return checksOut
        
    def check_dependencies(self,print_names=False,debug=False):
        """ Verify that the response file exists and contains requested components
        
            Prints out error message if anything fails
            returns:
                file_exists: true if file exists, false otherwise
                components_exist: true if all componenst exist, false otherwise
                n_components: number of components checked (including repeats)
        """
        comp_file=os.path.join(self.basepath,self.components_file)
        if not os.path.isfile(comp_file) :
            print('Intrument_components file not found: "{}"'.format(resp_dir))
            return False,False,None
        components=OBS_InstrumentComponents(comp_file)
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
                        component=components.get_component(key,ref_code)
                        if component:
                            components_dict[ref_code]['exists']=True
                            if type(component)==list:
                                components_dict[ref_code]['config_list']=\
                                        [x[len(ref_code)+1:] for x in component]
                        else:
                            components_dict[ref_code]['exists']=False
        return components_dict
        
################################################################################       
class OBS_InstrumentComponents:
    """ Everything in a instrument_components file"""
    def __init__(self,filename,referring_file=None,debug=False):
        """ Read instrument-components.yaml file"""
        temp,basepath=load_yaml(filename+root_symbol+'instrument_components',
                        referring_file)
        if debug:
            print(basepath)
        self.basepath=basepath
        self.revision=temp['revision']
        self.facility=temp['facility']
        self.response_files=temp['response_files']
        self.functional_components=temp['functional_components']
        
    def __repr__(self) :
        return "<OBS_InstrumentComponents: facility={}>".format(\
                    self.facility['reference_name'])    
                    
    def print_elements(self,elem_type):
        """ prints one type of InstrumentComponent (descriptions and  serial numbers)
        type = ('sensor', "preamplifier' or 'datalogger')
        """
        for key,element in sorted(self.functional_components[elem_type]['generic'].items()):
            description=None
            if 'equipment' in element:
                equipment=element['equipment']
                if type(equipment) == dict :
                    equipment=FDSN_EquipmentType(equipment)
                description = equipment.description
            if not description:
                if 'description' in element:
                    description = element['description']
                else:
                    description = 'None provided'
            SNs=[]
            if 'specific' in self.functional_components[elem_type]:
                if key in self.functional_components[elem_type]['specific']:
                    SNs= sorted(self.functional_components[elem_type]['specific'][key])        
            output={'    model':key,'description':description,'specified_serial_numbers':SNs}
            print(yaml.dump(output,indent=10,width=80))
            
    def get_component(self,component_type, reference_code, serial_number=None,
                        get_responses=True):
        """ get one instrument_component
    
            inputs:
                component_type: 'datalogger','preamplifier' or 'sensor'
                reference_code:
                serial_number: optional
                get_responses: return with responses filled in [True]
            output:
                instrument_component: OBS_Instrument_Component object 
                                            OR 
                                      list of possible component names
        """    
        if reference_code not in self.functional_components[component_type]['generic']:
            code_list=[]
            for generic_code in  self.functional_components[component_type]['generic']:
                if (reference_code+'_') in generic_code:
                    code_list.append(generic_code)
            if not code_list:
                code_list=None
            return code_list    
        # LOAD GENERIC COMPONENT    
        component= OBS_InstrumentComponent( \
                self.functional_components[component_type]['generic'][reference_code],
                os.path.join(self.basepath,self.response_files['directory']))
        component.reference_code=reference_code
        component.type=component_type
        if serial_number:
            component.equipment.serial_number=serial_number
            # LOAD SPECIFIC COMPONENT, IF IT EXISTS
            component=self.__load_specific_component(component,serial_number)
        return component

    def __load_specific_component(self,component,serial_number,debug=False):
        if not 'specific' in self.functional_components[component.type]:
            return component
        elif not serial_number in self.functional_components[component.type]['specific']:
            return component
        specific=self.functional_components[component.type]['specific'][serial_number]
        if debug:
            print("[{}][{}]=".format(component.type,serial_number))
            print("specific=",specific)
        if 'response' in specific:
            for key in specific['response']:
                component['response'][key]=specific['response'][key] 
        if 'equipment' in specific:
            component.equipment.merge(FDSN_EquipmentType(specific['equipment'])) 
        return component    
                
    def verify_individuals(self):
        """ Verify that all "specific" instruments have a generic counterpart
        
            returns true if so, false + error message if not
        """
        checksOut=True
        for component_type in sorted(self.functional_components.keys()):
            subcomponents=self.functional_components[component_type]
            if 'specific' in subcomponents:
                no_error_for_type = True
                for model in subcomponents['specific'].keys() :
                    if model not in subcomponents['generic'] :
                        if no_error_for_type:
                            print('  {:>15}: '.format(component_type),end='')                        
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
        resp_dir=os.path.join(self.basepath,self.response_files['directory'])
        if not os.path.exists(resp_dir) :
            print('Response file directory not found: "{}"'.format(resp_dir))
            return False
        print('Searching for response files within directory "{}"'.format(resp_dir))
        files_dict=dict()
        for component_type in self.functional_components:
            files_dict = self.__check_response_files(\
                                files_dict,
                                self.functional_components[component_type],
                                resp_dir,
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
                                component_type))
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
        if debug:
            print('')
            print(component)
        if 'response_files' in component:
            for filename in component['response_files'].values():
                if debug:
                    print(filename)
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

################################################################################       
class OBS_InstrumentComponent:
    """ One OBS instrument_component 
    
        Inputs:
            component_dict: generic component dictionary from 
                            instrument_components.yaml file
            
    """
    def __init__(self,component_dict,basepath,
                component_type=None,reference_code=None,
                debug=False):
        """ Inputs:
                component_dict: generic component dictionary from 
                                instrument_components.yaml file
                basepath: full path of directory containing Instrument_Components file
                component_type = component type ('datalogger','preamplifier' or 'sensor')
                reference_code = component reference code
            
        """
        if debug:
            print(basepath)
        self.basepath=basepath
        self.equipment = FDSN_EquipmentType(component_dict['equipment'])
        if 'seed_codes' in component_dict:
            self.seed_codes = component_dict['seed_codes']
        self.response_files = component_dict['response_files']
        self.type=component_type
        self.reference_code=reference_code
        self.response=None
        
    def __repr__(self) :
        return "<OBS_Instrument_Component: {}>".format(self.reference_code)
        
    def fill_responses(self,debug=False) :
        """ Fill in instrument responses from references"""
        if self.type=='sensor':
            response_order=['sensor','analog_filter']
        elif self.type=='preamplifier':
            response_order=['analog_filter']
        elif self.type=='datalogger':
            response_order=['analog_filter','digitizer','digital_filter']
        else:
            raise NameError('Unknown component type: {}'.format(self.type))
        if debug:
            print(self.response_files)
        self.__read_response_yamls(response_order)
        if debug:
            print(self.response)
                
    def __read_response_yamls(self,subcomponent_list,debug=False) : 
        """ READ INSTRUMENT RESPONSES FROM RESPONSE_YAML FILES
    
        Input:
            directory: base directory of response_yaml files
        """
        self.response=list()
        for subcomponent in subcomponent_list:    
            if subcomponent in self.response_files:    
                filename=self.response_files[subcomponent]
                #stage_file=os.path.join(self.basepath,filename)
                stage_file=filename
                if debug:
                    print("Reading subcomponent '{}' from {}".format(\
                        subcomponent,stage_file))
                   
                if debug:
                    print('stage file:',stage_file)
                file_stages,temp=load_yaml(stage_file+root_symbol+'stages',self.basepath)
                #if debug:
                    #print(file_stages)
                for stage in file_stages:
                    #if debug:
                    #    print(stage)
                    # IF STAGE HAS AN "INCLUDE" KEY, READ AND INJECT THE REFERRED FILE
                    if 'include' in stage['response']:
                        # READ REFERRED FILE
                        include_file = os.path.join(\
                                os.path.split(stage_file)[0],stage['response']['include'])
                        #include_file = stage['response']['include']
                        if debug:
                            print('include file:',include_file)
                        response,temp=load_yaml(include_file+root_symbol+'response',self.basepath)
                        # MAKE SURE IT'S THE SAME TYPE, IF SO INJECT
                        if stage['response']['type'] == response['type'] :
                            stage['response']=response
                        else:
                            text="Response and its included file don't have the same type\n"
                            text=text+'   "{}" : "{}" versus "{}"'.format(filename,
                                                            stage['response']['type'],
                                                            response['type'])
                            raise RuntimeError(text) 
                if debug:
                    #print(file_stages)
                    print("{:d} stages read".format(len(file_stages)))
                
                self.response.extend(file_stages)        
        if debug:
            print("{:d} total stages in component".format(len(self.response)))
            print(yaml.dump(self.response))
################################################################################       
class OBS_Instrument:
    """ One instrument from instrumentation.yaml file"""
    def __init__(self,filename,station_instrument,referring_file=None,
                    debug=False):
        """ Load an instrument 
    
        Inputs:
            station_instrument: is an OBS_Station.instrument dictionary
                    station_instrumnet['reference_code'] must correspond to
                        a key in instrumentation['instruments'])        
        """
    
        # READ IN
        instrumentation,path=load_yaml(filename + root_symbol + 'instrumentation',
                                    referring_file)
        generic=self.__get_generic_instrument(instrumentation,
                                    station_instrument['reference_code'])
        
        # SET ATTRIBUTES
        self.basepath=path
        self.facility=instrumentation['facility']
        self.revision=instrumentation['revision']
        self.components_file=instrumentation['components_file']
        self.reference_code=station_instrument['reference_code']
        self.serial_number=station_instrument['serial_number']
        self.equipment=FDSN_EquipmentType(generic['equipment'])
        self.das_components=generic['das_components']

        # SET SPECIFIC ATTRIBUTES (IF ANY)
        specific=self.__get_specific_instrument(instrumentation)
        if specific:
            self.__load_specific_instrument(specific)
        self.equipment.serial_number=self.serial_number
        self.__update_das_components(station_instrument)
                    
    def __repr__(self) :
        return "<  OBS_Instrument: reference_code={}, serial_number={}, {:d} channels >".format(
                                                    self.reference_code, 
                                                    self.serial_number, 
                                                    len(self.das_components))

    def __get_generic_instrument(self,instrumentation,reference_code) :
        generics = instrumentation['instruments']['generic'] 
        if reference_code not in generics:
            raise NameError('"{}" not in generic instrumentation list'.\
                            format(reference_code))
        return generics[reference_code]
        
    def __get_specific_instrument(self,instrumentation) :
        specifics = instrumentation['instruments']['specific'] 
        if self.reference_code not in specifics:
            return None
        if self.serial_number not in specifics[self.reference_code]:
            return None
        return specifics[self.reference_code][self.serial_number]
        
    def __load_specific_instrument(self,specific,debug=False) :
        reference_code=self.reference_code
        serial_number=self.serial_number
        if "orientation_codes" in specific:
            for or_code,inst_spec in specific["orientation_codes"].items():
                das_comp=self.__find_dc_key(or_code)
                if debug:
                    print("or_code=",or_code,"das_comp=",das_comp,"inst_spec=",inst_spec)
                self.__inject_measurement_instrument_parameters(
                                    das_comp,
                                    inst_spec)
        elif "das_components" in specific:
            for das_comp,inst_spec in specific['das_components'].items() :
                if debug:
                    print("das_comp=",das_comp,"inst_spec=",inst_spec)
                self.__inject_measurement_instrument_parameters(
                                    das_comp,
                                    inst_spec)
        else:
            raise NameError('Neither "orientation_codes" nor "das_components" \
                    found for specific instrument {} {}'.format(
                    reference_code,serial_number))
                    
    def __update_das_components(self,station_instrument,debug=False) :
        # FIRST INCORPORATE STANDARD CHANNEL VALUES
        cs=station_instrument['channel_standard']
        if not 'sample_rate' in cs:
            raise NameError('No sample_rate in channel_standard')
        if not 'datalogger_config' in cs:
            raise NameError('No datalogger_config in channel_standard')
        for key in self.das_components:
            if debug:
                print("="*40)
                print(yaml.dump(self.das_components[key]))
            self.__update_das_component(key,cs)
            if debug:
                print(yaml.dump(self.das_components[key]))
        # NEXT INCORPORATE SPECIFIC CHANNEL VALUES
#        if 'channel_locations' in station_instrument:
        for loc_key,value in station_instrument['channel_locations'].items():
            das_component=value.get('das_component',None)
            dc_key = self.__find_dc_key(loc_key[2],das_component)
            self.__insert_codes(dc_key,loc_key)
            self.__update_das_component(dc_key,value)
            
    def __find_dc_key(self,orientation_code,das_component=None,debug=False):
        """ finds the das_component corresponding to the orientation code
        
            Also validates that the orientation code is possible and unique, using
            das_component if necessary
        """
        if das_component:
            return das_component
        dc_key=None
        das_orientation_codes=[]
        for key,value in self.das_components.items():
            das_orientation_codes.append(value['orientation_code'])
            if value['orientation_code'] == orientation_code:
                if dc_key:
                    raise NameError('"{}" is a non-unique orientation code '\
                                    'for this instrument\n'\
                                    'You must specify das_component'\
                                    'in each "channel_locations" declaration'\
                                    ''.format(orientation_code))
                if das_component:
                    if das_component==key:
                        dc_key=key
                else:
                    dc_key=key
        if not dc_key:
            raise NameError('instrument {} : No das_component with orientation code '\
                            '"{}" found, only {} found'.format(
                            self.reference_code,orientation_code,das_orientation_codes))
        return dc_key
                                
    def __insert_codes(self,dc_key,chan_loc, debug=False):
        """ inserts location and seed codes into the das_component
        """
        if debug:
            print(chan_loc)
            print(dc_key)
            print(self.das_components[dc_key])
        self.das_components[dc_key]['band_code']=chan_loc[0]
        self.das_components[dc_key]['inst_code']=chan_loc[1]
        self.das_components[dc_key]['location_code']=chan_loc[4:6]
    def __update_das_component(self,dc_key,chan_values,debug=False):
        """ update a das_component with network:station:channel values """
        dc=self.das_components[dc_key]
        if 'sample_rate' in chan_values:
            dc['sample_rate']=chan_values['sample_rate']
        if 'serial_number' in chan_values:
            dc['equipment'].serial_number=chan_values['serial_number']
        for component_type in ['sensor','datalogger','preamplifier']:
            if component_type in chan_values:
                for key in chan_values[component_type]:
                    dc[component_type][key]=chan_values[component_type][key]
        if 'datalogger_config' in chan_values:
            dl_config=chan_values['datalogger_config']
            if debug:
                print('ADDING datalogger_config ({})'.format(dl_config))
            dc['datalogger']['reference_code']=\
                dc['datalogger']['reference_code']+ '_' + dl_config
            
    def __inject_measurement_instrument_parameters(self,das_component,
                                                instrument_spec,
                                                debug=False):
        """ reads and injects specific values into a measurement instrument """
        if debug:
            print(instrument_spec)              
        for key,values in instrument_spec.items() :
            if 'reference_code' in values:
                self.das_components[das_component][key]['reference_code'] = \
                                    values['reference_code']
            if 'serial_number' in values :
                self.das_components[das_component][key]['serial_number'] = \
                                    values['serial_number']
            if debug:
                print(chan_loc_code, component)
                pprint.pprint(self.channels[chan_loc_code])
                
    def load_components(self,components_file,referring_file=None) :
        """
        Load components into instrument
        
        components_file = name of components file
        referring_file = file that referred to the components file
                         (for resolving paths)
        """
        components=OBS_InstrumentComponents(components_file,referring_file)
    
        for key in self.das_components:
            self.fill_channel(key,components)
        self.response_directory=components.response_files['directory']
        self.resource_id=components.facility['reference_name'] + \
                                    components.revision['date']

    def fill_channel(self, channel_key,components, debug=False):
        """ Replace channel component strings with the actual components 
        
            components is an OBS_Instrument_Components object 
                    (direct from *_instrument_components.yaml)
        """
        channel=self.das_components[channel_key]
        if debug:
            print('Channel=',channel)
        for component_type in ['datalogger','preamplifier','sensor'] :
            if component_type == 'preamplifier' and component_type not in channel:
                print('component type "{}" absent, ignored'.format(component_type))
            if debug:
                print('Component=',component_type, channel[component_type])
            reference_code = channel[component_type]['reference_code']
            serial_number=channel[component_type].get('serial_number',None)

            channel[component_type]= components.get_component(component_type,
                                                            reference_code,
                                                            serial_number)
            if not channel[component_type]:
                raise NameError("Component not found: type:{}, "\
                                "reference_code:{}, serial_number:{}".format(
                                component_type,reference_code,serial_number))

    def modify_sensors(self, sensor_dict, referring_file=None):
        """ Modify sensors within an instrument
        Inputs:
            sensor_dict: dictionary with key = component, val=[reference_code, serial_number]
        """
        
        components,path=load_yaml(self,components_file+root_symbol+'instrument_components/functional_components',
                            referring_file)
        sensors_generic = components['sensor']['generic']
        sensors_specific= components['sensor']['specific']
    
        for channel, values in sensor_dict.items():
            ref_code=values['reference_code']
            SN=values['serial_number']
            self.channels[channel]['sensor']=sensors_generic[ref_code].copy()
            self.channels[channel]['sensor']['serial_number']=SN
            print('Setting {} {} SN to {}'.format(channel,ref_code,SN))
            if ref_code in sensors_specific:
                if SN in sensors_specific[ref_code]:
                    for key,value in sensors_specific[ref_code][SN].items():
                        print('Setting {} to {}'.format(key,value))
                        self.channels[channel]['sensor'][key]=value        

    def fill_responses(self,debug=False) :
        for name,channel in self.das_components.items() :
            if debug:
                print(channel)
            channel['sensor'].fill_responses()
            channel['preamplifier'].fill_responses()
            channel['datalogger'].fill_responses()

            if debug:
                print(channel)
            channel['response']=[]
            channel['response'].extend(channel['sensor'].response) 
            channel['response'].extend(channel['preamplifier'].response) 
            channel['response'].extend(channel['datalogger'].response) 
               
################################################################################       
class OBS_Station:
    """a station from the network.yaml file"""           
    def __init__(self,station_dict,station_code,network_code,debug=False):
        """ station_dict is straight out of the network.yaml file"""
        self.notes=station_dict['notes']
        self.comments=station_dict.get('comments',[])
        self.site=station_dict['site']
        self.start_date=station_dict['start_date']
        self.end_date=station_dict['end_date']
        self.location_code=station_dict['location_code']
        self.instrument=station_dict['instrument']
        self.locations=station_dict['locations']
        self.supplements=station_dict['supplements']
        self.code=station_code
        self.network_code=network_code
        if 'sensors' in station_dict:
            self.sensors=station_dict['sensors']
        else:
            self.sensors=None
    def __repr__(self) :
        if hasattr(self.instrument,'das_components'):
            txt =       "< OBS_Station: code={}, instrument=\n".format(
                                                                self.code)
            txt = txt + "      {} >".format(self.instrument)
            return txt
        else:
            print(self.instrument)
            txt =       "< OBS_Station: code={},".format(self.code)
            txt = txt + " instrument= ['{}','{}']\n".format(
                        self.instrument['reference_code'],
                        self.instrument['serial_number'])
            return txt
    def fill_instrument(self,instrument_file,referring_file=None,debug=False):
        """ Fills in instrument information """
        self.partial_fill_instrument(instrument_file,referring_file)
        if debug:
            print(self.instrument.das_components)
        
        if self.sensors:
            print("Adding custom sensors")
            self.instrument.modify_sensors(self.sensors,referring_file)
            if debug:
                print(self.sensors)
        self.instrument.fill_responses()
        if debug:
            print(self.instrument.das_components)
        
    def partial_fill_instrument(self,instrument_file,referring_file=None,debug=False):
        """ Fills in instrument information, but without specific component information """
        self.instrument=OBS_Instrument(instrument_file,
                            self.instrument,
                            referring_file=referring_file)
        if debug:
            print(self.instrument.das_components)
        self.instrument.load_components(self.instrument.components_file,referring_file)
        if debug:
            print(self.instrument.das_components)
        self.operator=self.instrument.facility
        if debug:
            print(yaml.dump(self))

    def make_obspy_station(self,debug=False):
        """
        Create an obspy station object from a fully informed station
        """
        # CREATE CHANNELS

        #if debug:
        #    print(self)
        channels=[]
        resource_id=self.instrument.resource_id
        for key,chan in self.instrument.das_components.items():
            if debug:
                print(key)
                print(yaml.dump(chan))
            response=make_obspy_response(chan['response'])
            #loc_code=key.split(':')[1]
            loc_code=chan['location_code']
            location = self.locations[loc_code]
            obspy_lon,obspy_lat = calc_obspy_LonLats(location)
            azimuth,dip=get_azimuth_dip(
                                        chan['sensor'].seed_codes,
                                        chan['orientation_code'])
            start_date=None
            end_date=None
            # Give at least 3 seconds margin around start and end dates
            if hasattr(self,'start_date'):
                if self.start_date:
                    start_date=round_down_minute(UTCDateTime(self.start_date),3)
            if hasattr(self,'end_date'):
                if self.end_date:
                    end_date=round_up_minute(UTCDateTime(self.end_date),3)
            if debug:
                print(key)
                print(yaml.dump(chan))
            #print(location)
            if 'localisation_method' in location:
                channel_comment=obspy_util.Comment('Localised using : {}'.format(
                        location['localisation_method']))
            channel_code=make_channel_code(chan['sensor'].seed_codes,
                                            chan['band_code'],
                                            chan['inst_code'],
                                            chan['orientation_code'],
                                            chan['sample_rate'])
            channel = inventory.channel.Channel(
                    code = channel_code,
                    location_code  = loc_code,
                    latitude  = obspy_lat,
                    longitude = obspy_lon,
                    elevation = obspy_types.FloatWithUncertaintiesAndUnit(
                                        location['position'][2],
                                        lower_uncertainty=location['uncertainties_m'][2],
                                        upper_uncertainty=location['uncertainties_m'][2]),
                    depth     = location['depth'],
                    azimuth   = obspy_types.FloatWithUncertainties(
                                        azimuth[0],
                                        lower_uncertainty=azimuth[1],
                                        upper_uncertainty=azimuth[1]),
                    dip       = dip[0],
                    types      =['CONTINUOUS','GEOPHYSICAL'],
                    sample_rate=chan['sample_rate'], 
                    clock_drift_in_seconds_per_sample=1/(1e8*float(chan['sample_rate'])),
                    sensor     =make_obspy_equipment(chan['sensor'].equipment),
                    pre_amplifier=make_obspy_equipment(chan['preamplifier'].equipment),
                    data_logger=make_obspy_equipment(chan['datalogger'].equipment),
                    equipment  =None,
                    response   =response,
                    description=None,
                    comments=[channel_comment],
                    start_date = start_date,
                    end_date   = end_date,
                    restricted_status = None,
                    alternate_code=None,
                    data_availability=None
                )
            channels.append(channel)
            if debug:
                print(yaml.dump(channel))
        # CREATE STATION
        station_loc_code=getattr(self,'station_location_code','00')
        if station_loc_code in self.locations:
            sta_loc=self.locations[station_loc_code]
            obspy_lon,obspy_lat = calc_obspy_LonLats(sta_loc)
        else:
            print ("No valid location code for station, either set station_location_code or provide a location '00'")
            sys.exit()
    
    
        obspy_comments = make_obspy_comments(
                        self.comments,
                        self.supplements,
                        station_loc_code,
                        sta_loc
                    )
        # DEFINE Operator
        agency=self.operator['full_name']
        contacts=None
        if 'email' in self.operator:
            contacts=[obspy_util.Person(emails=[self.operator['email']])]
        website=self.operator.get('website',None)
        operator = obspy_util.Operator([agency],contacts,website)
    
        if debug:
            print(obspy_comments)
        sta=inventory.station.Station(
                    code      = self.code,
                    latitude  = obspy_lat,
                    longitude = obspy_lon,
                    elevation = obspy_types.FloatWithUncertaintiesAndUnit(
                                        sta_loc['position'][2],
                                        lower_uncertainty=sta_loc['uncertainties_m'][2],
                                        upper_uncertainty=sta_loc['uncertainties_m'][2]),
                    channels = channels,
                    site     = obspy_util.Site(getattr(self,'site','')),
                    vault    = sta_loc['vault'],
                    geology  = sta_loc['geology'],
                    equipments= [make_obspy_equipment(self.instrument.equipment)],
                    operators=[operator],
                    creation_date=start_date,   # Necessary for obspy to write StationXML
                    termination_date=end_date,
                    description=None,
                    comments = obspy_comments,
                    start_date = start_date,
                    end_date   = end_date,
                    restricted_status = None,
                    alternate_code=None,
                    data_availability=None,
                )
        if debug:
            print(sta)
        return sta
################################################################################       
class FDSN_NetworkInfo:
    """ Basic information about an FDSN network """
    def __init__(self,OBS_network_info):
        """ Initialize using obs-info network.yaml "network_info" field"""
        self.code=OBS_network_info['code']
        self.start_date=UTCDateTime(OBS_network_info['start_date'])
        self.end_date=UTCDateTime(OBS_network_info['end_date'])
        self.description=OBS_network_info['description']
        self.comments=OBS_network_info['comments']  # Should be a list
################################################################################       
class FDSN_EquipmentType:
    """ Duplicates StationXML EquipmentType """
    def __init__(self,equipment_dict,debug=False):
        """ Initialize from YAML OBS-info equipment dictionary"""
        self.type=None
        self.description=None
        self.manufacturer=None
        self.model=None
        self.serial_number=None
        self.vendor=None
        self.installation_date=None
        self.removal_date=None
        self.calibration_date=None
        if debug:
            print(equipment_dict)
        for key in equipment_dict:
            if not hasattr(self,key):
                raise NameError('No attribute "{}" in FDSN_EquipmentType'.key)
            else:
                setattr(self,key,equipment_dict[key])
    def merge(self,new):
        """ Merge two EquipmentType objects
    
            Takes values from "new" where they exist
            new should be a 
        """
        if not type(new) == FDSN_EquipmentType:
            print('Tried to merge with a non FDSN_EquipmentType')
            return
        for key in vars(new):
            if getattr(new,key):
                setattr(self,key,getattr(new,key))

################################################################################ 
# OBSPY-specific

def obspy_response_with_sensitivity(resp_stages,sensitivity,debug=False):

    true_sensitivity_input_units=None
    
    # HAVE TO MAKE OBSPY THINK ITS M/S FOR IT TO CALCULATE SENSITIVITY CORRECTLY FOR PRESSURE
    if "PA" in sensitivity['input_units'].upper():
        true_sensitivity_input_units=sensitivity['input_units']
        sensitivity['input_units']='M/S'
    response=inventory.response.Response(
                instrument_sensitivity= inventory.response.InstrumentSensitivity(\
                            sensitivity['guess'],
                            sensitivity['freq'],
                            input_units = sensitivity['input_units'],
                            output_units = sensitivity['output_units'],
                            input_units_description = sensitivity['input_units_description'],
                            output_units_description = sensitivity['output_units_description']),
                response_stages=resp_stages
    )
    #response.plot(min_freq=0.001)
    guesstimate=response.instrument_sensitivity.value
    response.recalculate_overall_sensitivity(sensitivity['freq'])
    if debug:
        calculated=response.instrument_sensitivity.value
        print("Guesstimated vs calculated sensitivity at {:g} Hz : {:.3g} vs {:.3g} ({:.1g}% difference)".format(
                    response.instrument_sensitivity.frequency,
                    guesstimate,
                    calculated,
                    100.*abs(guesstimate-calculated)/calculated,
                    )
                )
    if true_sensitivity_input_units:
        response.instrument_sensitivity.input_units=true_sensitivity_input_units
        
    return response

def make_obspy_response(my_response,debug=False):
    """
    Create an obspy response object from a response_yaml-based list of stages
    """
    resp_stages=[]
    i_stage=0
    sensitivity={'guess':1.}
    for stage in my_response:
        # DEFINE COMMON VALUES
        i_stage=i_stage+1
        resp=stage['response']
        gain=stage.get('gain',{})
        gain_value= float(gain.get('value',1.0))
        gain_frequency = float(gain.get('frequency',0.))
        if "input_units" in stage:
            input_units = stage['input_units']['name']
            input_units_description = stage['input_units']['description']
        else:
            input_units=None
        if 'output_units' in stage:
            output_units = stage['output_units']['name']
            output_units_description = stage['output_units']['description']
            sensitivity['output_units']=stage['output_units']['name']
            sensitivity['output_units_description']=\
                                stage['output_units'].get("description",None)
        else:
            output_units=None
        sensitivity['guess']=sensitivity['guess'] * gain_value
        if i_stage==1:
            sensitivity['input_units']=stage['input_units']['name']
            sensitivity['input_units_description']=\
                                stage['input_units'].get("description",None)
            sensitivity['freq']=gain_frequency
        resp_type=resp['type']
        if debug:
            print(i_stage,resp_type)
        if resp_type=='PolesZeros':
            lstr=resp['units'].lower()
            if "hertz" in lstr or "hz" in lstr:
                pz_type='LAPLACE (HERTZ)'
            elif 'z-transform' in lstr or 'digital' in lstr:
                pz_type='DIGITAL (Z-TRANSFORM)'
            elif 'rad' in lstr:
                pz_type='LAPLACE (RADIANS/SECOND)'
            else:
                raise ValueError('Unknown PoleZero response type: "{}"'.format(lstr))
            zeros = [float(t[0]) + 1j * float(t[1]) for t in resp['zeros']]
            poles = [float(t[0]) + 1j * float(t[1]) for t in resp['poles']]
            norm_freq = stage.get('normalization_frequency',gain.get('frequency',1.0))
            norm_factor=resp.get('normalization_factor',
                                    calc_norm_factor(zeros,poles,norm_freq,pz_type))
            if debug:
                print('  Z=',zeros,' P=',poles,' A0={:g} at {:g} Hz'.format(norm_factor,norm_freq))
            resp_stages.append(\
                inventory.response.PolesZerosResponseStage(\
                    i_stage,
                    gain_value, gain_frequency,
                    input_units, output_units,
                    pz_transfer_function_type = pz_type,
                    normalization_frequency = norm_freq,
                    normalization_factor = norm_factor,
                    zeros = zeros,
                    poles = poles,
                    input_units_description=input_units_description,
                    output_units_description=output_units_description,
                    description=stage['description']
                )
            )
        elif resp_type=="COEFFICIENTS" :
            delay=None
            correction=None
            offset=None
            input_sample_rate=None
            decimation_factor=None
            if stage['response']['type'].lower()=='hertz':
                cf_type='ANALOG (HERTZ)'
            elif stage['response']['type'].lower()=='digital':
                cf_type='DIGITAL'
                input_sample_rate=1./samp_interval
                decimation_factor=int(stage['decimation_factor'])
                offset=0,
                delay=resp.get('delay',0)*samp_interval
                if resp.get('corrected',False):
                    correction=delay
                else:
                    correction=0.
            else:
                cf_type='ANALOG (RADIANS/S)'
            resp_stages.append(\
                inventory.response.CoefficientsTypeResponseStage(\
                    i_stage,
                    gain_value, gain_frequency,
                    input_units, output_units,
                    cf_type,
                    numerator=float(resp['numerator']),
                    denominator=float(resp['denominator']),
                    input_units_description=input_units_description,
                    output_units_description=output_units_description,
                    description=stage['description'],
                    decimation_input_sample_rate=input_sample_rate,
                    decimation_factor=decimation_factor,
                    decimation_offset=0,
                    decimation_delay=delay,
                    decimation_correction=correction
                )
            )
        elif resp_type=="FIR" :
            samp_interval=float(stage['input_sampling_interval'])
            delay=resp.get('delay',0)*samp_interval
            if resp.get('corrected',False):
                correction=delay
            else:
                correction=0.            
            resp_stages.append(\
                inventory.response.FIRResponseStage(\
                    i_stage,
                    gain_value, gain_frequency,
                    'COUNTS', 'COUNTS',
                    symmetry= resp['symmetry'].upper(),
                    coefficients = [obspy_types.FloatWithUncertaintiesAndUnit(x) for x in resp['coefficients']],
                    input_units_description='Digital Counts',
                    output_units_description='Digital Counts',
                    description=stage['description'],
                    decimation_input_sample_rate=1./samp_interval,
                    decimation_factor=int(stage['decimation_factor']),
                    decimation_offset=0,
                    decimation_delay=delay,
                    decimation_correction=correction
                )
            )
        elif resp_type=="AD_CONVERSION" : 
            resp_stages.append(\
                inventory.response.CoefficientsTypeResponseStage(\
                    i_stage,
                    gain_value, gain_frequency,
                    input_units, output_units,
                    'DIGITAL',
                    numerator=[obspy_types.FloatWithUncertaintiesAndUnit(1.0)],
                    denominator=[],
                    input_units_description=input_units_description,
                    output_units_description=output_units_description,
                    description=stage['description'],
                    decimation_input_sample_rate=1./float(stage['output_sampling_interval']),
                    decimation_factor=1,
                    decimation_offset=int(stage.get('decimation_offset',0)),
                    decimation_delay=float(stage.get('decimation_delay',0.)),
                    decimation_correction=float(stage.get('decimation_correction',0.))
                )
            )
        elif resp_type=="ANALOG" :
            resp_stages.append(\
                inventory.response.ResponseStage(\
                    i_stage, 
                    gain_value, gain_frequency,
                    input_units, output_units,
                    input_units_description=input_units_description,
                    output_units_description=output_units_description,
                    description=stage['description']
                )
            )
        else:
            raise TypeError('UNKNOWN STAGE RESPONSE TYPE: {}'.format(rtype))
    response=obspy_response_with_sensitivity(resp_stages,sensitivity)
    if debug:
        print(response)
    return response

def make_obspy_equipment(equipment,
                            resource_id=None,debug=False):
    """
    Create obspy EquipmentType from obs_info.equipment
    
    """
    if type(equipment) == dict :
        equipment=FDSN_EquipmentType(equipment)
    if not equipment.description:
        raise RuntimeError('Your equipment variable does not have a "description"')
    obspy_equipment = obspy_util.Equipment(
        type =             equipment.type,
        description =      equipment.description,
        manufacturer =     equipment.manufacturer,
        vendor =           equipment.vendor,
        model =            equipment.model,
        serial_number =    equipment.serial_number,
        installation_date= equipment.installation_date,
        removal_date =     equipment.removal_date,
        calibration_dates= equipment.calibration_date,
        resource_id=resource_id
    )
    if debug:
        print(equipment)
        print(obspy_equipment)
    return obspy_equipment

def make_obspy_comments(comments,supplements,loc_code,location):
    """
    Create obspy comments from station information
    
    Also stuffs fields that are otherwise not put into StationXML:
         "supplement" elements as JSON strings, 
          "location:location_methods" 
    """
    obspy_comments = []
    for comment in comments:
        obspy_comments.append(obspy_util.Comment(comment))
    for key,val in supplements.items():
        obspy_comments.append(obspy_util.Comment(json.dumps({key:val})))        
    loc_comment = 'Using location "{}"'.format(loc_code)
    if 'localisation_method' in location:
        loc_comment = loc_comment + ', localised using : {}'.format(
                location['localisation_method'])
    obspy_comments.append(obspy_util.Comment(loc_comment))                    
    return obspy_comments
    
def calc_obspy_LonLats(location, debug=False): 
    """ Calculate obspy util.Latitude and util.Longitude"""
    longitude=float(location['position'][0])
    latitude=float(location['position'][1])
    meters_per_degree_lat = 1852.*60.
    meters_per_degree_lon = 1852.*60.*m.cos(latitude*m.pi/180.)
    lat_uncert=location['uncertainties_m'][1]/meters_per_degree_lat
    lon_uncert=location['uncertainties_m'][0]/meters_per_degree_lon
    # REDUCE UNCERTAINTIES TO 3 SIGNIFICANT FIGURES
    lat_uncert=float('{:.3g}'.format(lat_uncert))
    lon_uncert=float('{:.3g}'.format(lon_uncert))
    if debug:
        print('{:.3f}+-{:.5f}, {:.3f}+-{:.5f}'.format(longitude,lon_uncert,                                                    latitude,lat_uncert))
    obspy_lat  = obspy_util.Latitude(
                                latitude,
                                lower_uncertainty=lat_uncert,
                                upper_uncertainty=lat_uncert)    
    obspy_lon = obspy_util.Longitude(
                                longitude,
                                lower_uncertainty=lon_uncert,
                                upper_uncertainty=lon_uncert)    
    return obspy_lon,obspy_lat 
      
################################################################################ 
# OCA-JSON specific
################################################################################       
class OCA_Network:
    """OCA network description format"""           
    def __init__(self,obs_network,debug=False):
        """
        Create an OCA network object (contains stations without component details)
        """
        if debug:
            for key,station in obs_network.stations.items():
                print("B-Ca:",key,station.comments)
        self.dict=dict()
        self.__make_network_header(obs_network)
        self.__make_authors(obs_network)
        
        if debug:
            for key,station in obs_network.stations.items():
                print("B-Cb:",key,station.comments)
        self.dict['stations']=[]
        for key,station in obs_network.stations.items():
            if debug: 
                print("C:",key,station.comments)
            oca_station=self.__make_station_header(station)
            #oca_station={"open_date":'duh',"close_date":'der'}
            oca_station=self.__make_devices_and_channels(oca_station,
                                                station.instrument.das_components
                        )
            self.dict['stations'].append(oca_station)
    
    def __repr__(self) :        
        return "<OCA_Network: fdsn_code={}>".format(self.dict['network']['fdsn_code'])    
        
    def __make_network_header(self,obs_network):
        netinfo=obs_network.network_info
        # Forces authorship of comments to network.yaml revision author
        for comment in netinfo.comments:
            comments={"value" : comment, "authors":["auth1"]}
        self.dict['network'] = {
            "fdsn_code" :   netinfo.code,
            "temporary" :   True,
            "open_date" :   netinfo.start_date.isoformat(),
            "close_date" :  netinfo.end_date.isoformat(),
            "description" : netinfo.description,
            "comments" :    comments
        }
                
    def __make_authors(self,obs_network):
        """ Fills in author(s) information"""
        self.dict['comment_authors']=dict()
        i=0
        for author in obs_network.revision['authors']:
            i=i+1
            phones=list()
            if 'phones' in author:
                for phone in author["phones"]:
                    phones.append({"phone_number": phone}),
            au_dict = {
                "firstname": author['first_name'],
                "lastname": author['last_name'],
                "emails": [author.get('email','')],
                "phones": phones
            }
            self.dict['comment_authors']['auth'+str(i)]=au_dict         
            
    def __make_station_header(self,obs_station,debug=False):
        """ Makes OCA STATION HEADER
        returns station dictionary
         """
        oca_station=dict()
        if debug:
            print(obs_station.comments)
            print(len(obs_station.supplements))
        oca_comments=[x for x in obs_station.comments]
        for key,value in obs_station.supplements.items():
            if debug:
                print(key)
            oca_comments.append(json.dumps({ key : value }).replace('"',"'"))
        if debug:
            print('----')
        
        sta_position=obs_station.locations[obs_station.location_code]['position']
        oca_station= {
            'IR_code' : obs_station.code,
            'site' :      obs_station.site,
            'comments' :  oca_comments,
            'open_date' :   obs_station.start_date,
            'close_date' :  obs_station.end_date,
            'longitude' :   sta_position[0],
            'latitude' :    sta_position[1],
            'altitude' :    sta_position[2],
            'altitude_unit' : 'm',
            'first_install' : obs_station.start_date
        }
        return oca_station
               
    def __make_devices_and_channels(self,oca_station,das_components):
    
        oca_station['channels']=list()
        devices=dict()
        for das_code,values in das_components.items():
            devices, device_codes = self.__add_devices(devices,values)
            ###
            ch=self.__make_channel(das_code,device_codes,values,
                                        oca_station['open_date'],
                                        oca_station['close_date'])
            oca_station['channels'].append(ch)
        oca_station['installed_devices']=devices   
        return oca_station
        
    def __add_devices(self,devices,values,debug=False):
        """
        Find devices or add to dictionary of "installed devices"
        
        devices= existing dictionary of devices
        values = values corresponding to this das_component
        """
        codes=dict()
        if debug:
            print('===',values)
        
        sensor = self.__make_devicedict("sensor",values['sensor'].equipment)
        azimuth,dip = get_azimuth_dip(values['sensor'].seed_codes,values['orientation_code'])
        sensor["azimuth_error"]= azimuth[1]
        sensor["dip_error"]= dip[1]
        sensor["local_depth"]= 0
        sensor["vault"]= "seafloor"
        sensor["config"]= "single"
        devices,codes['sensor']=self.__find_append_device(devices,sensor,'sensor')
        
        anafilter = self.__make_devicedict("anafilter",values['preamplifier'].equipment)
        devices,codes['anafilter']=self.__find_append_device(devices,anafilter,'anafilter')
        
        das = self.__make_devicedict("das",values['datalogger'].equipment)
        devices,codes['das']=self.__find_append_device(devices,das,'das')
            
        return devices,codes
        
    def __make_devicedict(self,metatype,equipment):
        #if type(equipment) == dict:
        #    equipment=FDSN_EquipmentType(equipment)
        SN = equipment.serial_number
        devicedict = {
            "metatype": metatype,
            "manufacturer": equipment.manufacturer,
            "model": equipment.model,
            "serial_number": "unknown" if SN is None else SN
        }
        return devicedict

    def __find_append_device(self,devices,device,device_name)  : 
        """ 
        Find or append device to dictionary of devices 
    
        device codes are '{device_name}_N', where N is a counter for
        that type of device   
        """     
        n_matching_devices=0   
        for device_code,value in devices.items():
            if device_name not in device_code:
                continue
            else:
                n_matching_devices=n_matching_devices+1
                if device==value:
                    return devices, device_code             
        device_code = device_name + '_' + str(n_matching_devices+1)
        devices[device_code]=device
        return devices, device_code
       
    def __make_channel(self,das_code,device_codes,values,open_date,close_date,
                            debug=False) :
        if debug:
            print('das_code',das_code)
            print('device_codes',device_codes)
            print('values',values)
        das = das_code.split('_')
        das_component = das[0]
        if len(das)>1:
            das_connector = das[1]
        else:
            das_connector = '1'
        azimuth,dip=get_azimuth_dip(values['sensor'].seed_codes,
                                                values['orientation_code'])
        ana_filter_list=[]
        for comp_type in ["sensor","preamplifier","datalogger"]:
            if comp_type in values:
                if "analog_filter" in values[comp_type].response_files:
                    ana_filter_list.append(
                        {"analog_filter":values[comp_type].response_files['analog_filter'],
                        "component": "1"})
        ch= {
            "location_code" :     values['location_code'],
            "seed_code" :         make_channel_code(values['sensor'].seed_codes,
                                                    values['band_code'],
                                                    values['inst_code'],
                                                    values['orientation_code'],
                                                    values['sample_rate']),
            "sensor" :            device_codes['sensor'],
            "sensor_component" :  values['orientation_code'],
            "analog_filter_list": ana_filter_list,
            "das" :               device_codes['das'],
            "das_connector" :     das_connector,
            "das_component" :     das_component,
            "das_digital_filter" : values['datalogger'].reference_code,
            "data_format" :       "STEIM1",
            "polarity_reversal" : dip=="-90.0",
            "open_date" :         open_date,
            "close_date" :        close_date,
            "channel_flags" :     "CG"
        }
        return ch        
        
################################################################################ 
# OTHER Routines

def validate_OBS_YAML(yaml_file,schema_file,debug=False) :
    from jsonschema import validate   # Available from github
    # READ YAML file
    my_file=yaml.load(yaml_file)
    # READ YAML SCHEMA
    schema = json.load(schema_file)
    # VALIDATE AGAINST SCHEMA
    validate(my_file,schema)

def calc_norm_factor(zeros,poles,norm_freq,pz_type,debug=False) :
    """
    Calculate the normalization factor for give poles-zeros
    
    The norm factor A0 is calculated such that
                       sequence_product_over_n(s - zero_n)
            A0 * abs(------------------------------------------) === 1
                       sequence_product_over_m(s - pole_m)

    for s_f=i*2pi*f if the transfer function is in radians
            i*f     if the transfer funtion is in Hertz
    """
    
    A0 = 1. + 1j*0.
    if pz_type == 'LAPLACE (HERTZ)':
        s = 1j * norm_freq
    elif pz_type == 'LAPLACE (RADIANS/SECOND)':
        s = 1j * 2 * m.pi * norm_freq
    else:
        print("Don't know how to calculate normalization factor for z-transform poles and zeros!")
    for p in poles:
        A0 = A0 * (s - p)
    for z in zeros:
        A0 = A0 / (s - z)
        
    if debug:
        print('poles=',poles,', zeros=',zeros,'s={:g}, A0={:g}'.format(s,A0))
    
    A0=abs(A0)
    
    return A0
    
##################################################
def round_down_minute(date_time,min_offset):
    """
    Round down to nearest minute that is at least minimum_offset seconds earlier
    """
    dt=date_time-min_offset
    dt.second=0
    dt.microsecond=0
    return dt

def round_up_minute(date_time,min_offset):
    """
    Round up to nearest minute that is at least minimum_offset seconds later
    """
    dt=date_time+60+min_offset
    dt.second=0
    dt.microsecond=0
    return dt

def load_yaml(path,basepath=None,debug=False):
    """
    Loads a yaml element from referenced file
    
    root_symbol is interpreted as the file's root level
    If it is at the beginning of the reference, then the element is searched for
    in the current file.  If it is in the middle, then the element is searched
    for within the filename preceding it. 
     
    Inspired by JSON Pointers, but JSON Pointers use '#' as the root level
    We can't (for now), because the DBIRD-based file names are full of '#'s!
       
    input:
        path (str): path to the element (filename &/or internal path)
        basepath: full path to current file
                    This path (if any) will be prepended to the reference, as
                    referenced YAML files are assumed to be in (or referenced to
                    the same path as the referencing YAML files (like JSON Pointers) 
                    If it includes a filename, the filename will be sliced off.
    output:
        element: the requested yaml element
        basepath: the path of this file
    """
    filename=None
    
    if root_symbol in path:
        if path.count(root_symbol) > 1:
            raise RuntimeError('More than one occurence of "{}" in file reference "{}"'.format(
                    root_symbol,path))
        if path[0] == root_symbol:
            filename=''
            internal_path=path[1:]
        elif path[-1] == root_symbol:
            filename=path[0:-1]
            internal_path=''
        else:     
            A=path.split('$')
            filename=A[0]
            internal_path=A[1]
    else:
        raise RuntimeError(": no internal path in '{}'".format(path))
            
    if debug:
        print('path={}, basepath={}'.format(path, basepath))
        
#    if filename:
    if basepath:
        if os.path.isfile(basepath):
            current_path=os.path.dirname(basepath)
        else:
            current_path=basepath
        filename=os.path.join(current_path,filename)
    else:
        current_path=os.getcwd()
    if debug:
        print('filename={}, internal_path={}'.format(filename,internal_path))
        
    internal_paths=internal_path.split('/')    
    with open(filename,'r') as f:
        element=yaml.safe_load(f)[internal_paths[0]]
    
    if len(internal_paths) > 1:
        for key in internal_paths[1:] :
            if not key in element:
                raise RuntimeError("Internal path {} not found in file {}".format(\
                        internal_path,filename))
            else:
                element=element[key]
    if debug:
        print(type(element))        
    return element, os.path.abspath(os.path.dirname(filename))   
    
def make_channel_code(channel_seed_codes,
                        given_band_code,instrument_code,orientation_code,
                        sample_rate,
                        debug=False):
    """
        Make a channel code from sensor, instrument and network information
        
        channel_seed_codes is a dictionary from the instrument_component file
        given_band, instrument, and orientation codes are from the network file
        sample_rate is from the network_file
    """
    band_base=channel_seed_codes['band_base']
    if not len(band_base) == 1:
        raise NameError('Band code is not a single letter: {}'.format(band_code))
    if not instrument_code == channel_seed_codes['instrument']:
        raise NameError('instrument and component instrument_codes do not '\
                        'match: {}!={}'.format(inst_code,
                                        channel_seed_codes['instrument']))
    if not orientation_code in [key for key in channel_seed_codes['orientation']]:
        raise NameError('instrument and component orientation_codes do not '\
                        'match: {}!={}'.format(orientation_code,
                                        channel_seed_codes['orientation']))
    if band_base in 'FCHBMLVURPTQ':
        if sample_rate >=1000:
            band_code='F'
        elif sample_rate >=250:
            band_code='C'
        elif sample_rate >=80:
            band_code='H'
        elif sample_rate >=10:
            band_code='B'
        elif sample_rate > 1 :
            band_code='M'
        elif sample_rate > .3 :
            band_code='L'
        elif sample_rate > .03 :
            band_code='V'
        elif sample_rate > .003 :
            band_code='U'
        elif sample_rate >= .0001 :
            band_code='R'
        elif sample_rate >= .00001 :
            band_code='P'
        elif sample_rate >= .000001 :
            band_code='T'
        else :
            band_code='Q'
    elif band_base in 'GDES':
        if sample_rate >=1000:
            band_code='G'
        elif sample_rate >=250:
            band_code='D'
        elif sample_rate >=80:
            band_code='E'
        elif sample_rate >=10:
            band_code='S'
        else:
            raise ValueError('Short period instrument has sample rate < 10 sps')
    else:
        raise NameError('Unknown band code: {}'.format(band_code))
    if band_code != given_band_code :
        raise NameError('Band code calculated from component and sample rate'\
            ' does not match that given in network file: {} versus {}'.format(
                                    band_code,given_band_code))
    if debug:
        print(band_code)
    channel_code =  band_code+instrument_code+orientation_code
    return channel_code

def get_azimuth_dip(channel_seed_codes,orientation_code):
    " Returns azimuth and dip [value,error] pairs "
    if orientation_code in channel_seed_codes['orientation']:
        azimuth=    channel_seed_codes['orientation'][orientation_code]['azimuth']
        azimuth =   [float(x) for x in azimuth]
        dip=        channel_seed_codes['orientation'][orientation_code]['dip']
        dip =       [float(x) for x in dip]
    else:
        raise NameError('orientation code "{}" not found in '\
                'component seed_codes.orientation'.format(orientation_code)) 
    return azimuth,dip