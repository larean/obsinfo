""" 
Print complete stations from information in network.yaml file

nomenclature:
    A "measurement instrument" is a means of recording one physical parameter,
        from sensor through dac
    An "instrument" is composed of one or more measurement instruments
        
Should modify the code to treat $ref as a placeholder for the associated object
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

from .instrumentation import instrumentation as oi_instrumentation
from ..instrument_components import instrument_components as oi_instrument_components
from ..misc import FDSN

################################################################################       
class instrument:
    """ One instrument from instrumentation.yaml file"""
    def __init__(self,filename,station_instrument,referring_file=None,
                    debug=False):
        """ Load an instrument 
    
        Inputs:
            station_instrument: is an OBS_Station.instrument dictionary
                    station_instrument['reference_code'] must correspond to
                        a key in instrumentation['instruments'])        
        """
    
        instrumentation=oi_instrumentation(filename,referring_file)
        if debug:
            print(60*"=")
            print(type(station_instrument))
            pprint.pprint(station_instrument)
                
        generic=self.__get_generic_instrument(instrumentation,
                                    station_instrument['reference_code'])
        
        # SET ATTRIBUTES
        self.basepath=         instrumentation.basepath
        self.format_version=   instrumentation.format_version
        self.revision=         instrumentation.revision
        self.facility=         instrumentation.facility
        self.components_file = instrumentation.components_file

        self.reference_code= station_instrument['reference_code']
        self.serial_number=  station_instrument['serial_number']
        self.equipment=      FDSN.equipment_type(generic['equipment'])
        self.das_components= generic['das_components']

        # SET SPECIFIC ATTRIBUTES (IF ANY)
        specific=self.__get_specific_instrument(instrumentation)
        if specific:
            self.__load_specific_instrument(specific)
        self.equipment.serial_number=self.serial_number
        self.__update_das_components(station_instrument)
                    
    def __repr__(self) :
        return "<  {}: reference_code={}, serial_number={}, {:d} channels >".format(
                                                    __name__,
                                                    self.reference_code, 
                                                    self.serial_number, 
                                                    len(self.das_components))

    def __get_generic_instrument(self,instrumentation,reference_code) :
        generics = instrumentation.instruments['generic'] 
        if reference_code not in generics:
            raise NameError('"{}" not in generic instrumentation list'.\
                            format(reference_code))
        return generics[reference_code]
        
    def __get_specific_instrument(self,instrumentation) :
        specifics = instrumentation.instruments.get('specific',None) 
        if not specifics:
            return None
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
        # INCORPORATE SPECIFIC CHANNEL VALUES
        for loc_key,value in station_instrument['channel_codes_locations'].items():
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
                                    'in each "channel_codes_locations" declaration'\
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
        for block_type in ['sensor','datalogger','preamplifier']:
            if block_type in chan_values:
                for key in chan_values[block_type]:
                    dc[block_type][key]=chan_values[block_type][key]
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
        components=oi_instrument_components(components_file,referring_file)
    
        for key in self.das_components:
            self.fill_channel(key,components)
        self.resource_id=self.facility['reference_name'] + \
                                    components.revision['date']

    def fill_channel(self, channel_key,components, debug=False):
        """ Replace channel component strings with the actual components 
        
            components is an OBS_Instrument_Components object 
                    (direct from *_instrument_components.yaml)
        """
        channel=self.das_components[channel_key]
        if debug:
            print('Channel=',channel)
        for block_type in ['datalogger','preamplifier','sensor'] :
            if block_type == 'preamplifier' and block_type not in channel:
                print('component type "{}" absent, ignored'.format(block_type))
            if debug:
                print('Component=',block_type, channel[block_type])
            reference_code = channel[block_type]['reference_code']
            serial_number=channel[block_type].get('serial_number',None)
            if debug:
                print("components=",components)

            channel[block_type]= components.get_component(block_type,
                                                            reference_code,
                                                            serial_number)
            if not channel[block_type]:
                raise NameError("Component not found: type:{}, "\
                                "reference_code:{}, serial_number:{}".format(
                                block_type,reference_code,serial_number))

    def modify_sensors(self, sensor_dict, referring_file=None):
        """ Modify sensors within an instrument
        Inputs:
            sensor_dict: dictionary with key = component, val=[reference_code, serial_number]
        """
        
        components,path=load_information_file(self,components_file+root_symbol+'instrument_components/instrument_blocks',
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
                print(yaml.dump(channel))
            channel['sensor'].fill_responses()
            channel['preamplifier'].fill_responses()
            channel['datalogger'].fill_responses()
            if debug:
                print('channel {} has : {:d} sensor,{:d} preamp,{:d} logger stages'.format(\
                    name,
                    len(channel['sensor'].response),
                    len(channel['preamplifier'].response),
                    len(channel['datalogger'].response)))
                #print(channel)
            channel['response']=[]
            channel['response'].extend(channel['sensor'].response) 
            channel['response'].extend(channel['preamplifier'].response) 
            channel['response'].extend(channel['datalogger'].response) 
               
