""" 
Print complete stations from information in network.yaml file
"""
#from ruamel import yaml
import sys
import copy
#from ruamel import yaml
import yaml
import math as m
import json
import pprint
import os.path
import obspy.core.util.obspy_types as obspy_types
import obspy.core.inventory as inventory
import obspy.core.inventory.util as obspy_util
from obspy.core.utcdatetime import UTCDateTime

root_symbol='$'

################################################################################       
    
class OBS_Network:
    """ Everything contained in a network.yaml file"""
    def __init__(self,filename,referring_file=None,debug=False):
        temp=load_yaml(filename+root_symbol+'network',referring_file) 
        self.revision=temp['revision'].copy()
        self.facility=temp['facility']
        self.network_info=FDSN_Network_Info(temp['network_info'])
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
            station.partial_fill_Instrument(self.instrumentation_file,
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
class FDSN_Network_Info:
    """ Basic information about an FDSN network """
    def __init__(self,OBS_network_info):
        """ Initialize using obs-info network.yaml "network_info" field"""
        self.code=OBS_network_info['code']
        self.start_date=UTCDateTime(OBS_network_info['start_date'])
        self.end_date=UTCDateTime(OBS_network_info['end_date'])
        self.description=OBS_network_info['description']
        self.comments=OBS_network_info['comments']  # Should be a list
################################################################################       
class OBS_Instrumentation:
    """ Everything in an instrumentation.yaml file
    
    Functions are very similar to those in instrument_components: should there 
    be a shared class?
    """
    def __init__(self,filename,referring_file=None):
        temp=load_yaml(filename+root_symbol+'instrumentation',
                        referring_file)
        self.revision=temp['revision']
        self.facility=temp['facility']
        self.components_file=temp['components_file']
        self.variables=temp['variables']
        self.azi_dip=temp['azi_dip']
        self.instruments=temp['instruments']
    def __repr__(self) :
        return "<OBS_Instrumentation: facility={}>".format(\
                    self.facility['reference_name'])    
    def printElements(self):
        """ prints all instruments (descriptions and  serial numbers)
        """
        for key,element in sorted(self.instruments['generic'].items()):
            description=None
            if 'equipment' in element:
                if 'description' in element['equipment']:
                    description = element['equipment']['description']
            if not description and 'description' in element:
                description = element['description']
            else:
                description = 'None provided'
            SNs=[]
            if 'specific' in self.instruments:
                if key in self.instruments['specific']:
                    SNs= sorted(self.instruments['specific'][key])        
            output={' model':key,'description':description,'specified_serial_numbers':SNs}
            print(yaml.dump(output,width=70))
            
    def verifyIndividuals(self):
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
        
################################################################################       
class OBS_InstrumentComponents:
    """ Everything in a instrument_components file"""
    def __init__(self,filename,referring_file=None):
        temp=load_yaml(filename+root_symbol+'instrument_components',
                        referring_file)
        self.revision=temp['revision']
        self.facility=temp['facility']
        self.response_directory=temp['response_directory']
        self.functional_components=temp['functional_components']
    def __repr__(self) :
        return "<OBS_InstrumentComponents: facility={}>".format(\
                    self.facility['reference_name'])    
    def printElements(self,type):
        """ prints one type of InstrumentComponent (descriptions and  serial numbers)
        type = ('sensor', "preamplifier' or 'datalogger')
        """
        for key,element in sorted(self.functional_components[type]['generic'].items()):
            description=None
            if 'equipment' in element:
                if 'description' in element['equipment']:
                    description = element['equipment']['description']
            if not description and 'description' in element:
                description = element['description']
            else:
                description = 'None provided'
            SNs=[]
            if 'specific' in self.functional_components[type]:
                if key in self.functional_components[type]['specific']:
                    SNs= sorted(self.functional_components[type]['specific'][key])        
            output={' model':key,'description':description,'specified_serial_numbers':SNs}
            print(yaml.dump(output,width=70))
            
    def verifyIndividuals(self):
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
                        print(15*' ' +'"{}" is in "specific" but not in "generic"'.format(model))
        return checksOut
        
################################################################################       
class OBS_Instrument:
    """ One instrument from instrumentation.yaml file"""
    def __init__(self,filename,reference_code,serial_number,referring_file=None,
                    debug=False):
        """ Load an instrument 
    
        Inputs:
            instrument_file: name of the instrumentation file
            reference_code: The instrument reference_code (must correspond to a key in 
                        instrumentation['instruments'])        
        """
    
        # READ IN INSTRUMENTATION
        instrumentation=load_yaml(filename + root_symbol + 'instrumentation',
                                    referring_file)
        generic = instrumentation['instruments']['generic']
        
        # LOAD GENERIC INSTRUMENT MODEL
        self.equipment=generic[reference_code]['equipment']
        self.channels=generic[reference_code]['channels']
        self.components_file=instrumentation['components_file']
        self.variables=instrumentation['variables']
        self.facility=instrumentation['facility']
        self.revision=instrumentation['revision']
        self.reference_code=reference_code
        self.serial_number=serial_number

        if debug:
            print(self)

        # LOAD SPECIFIC INSTRUMENT, IF IT EXISTS
        if reference_code in instrumentation['instruments']['specific']:
            if serial_number in instrumentation['instruments']['specific'][reference_code]:
                specific=instrumentation['instruments']['specific'][reference_code][serial_number]
                for chan_loc_code,components in specific['channels'].items() :
                    for component,values in components.items() :
                        if 'reference_code' in values:
                            self.channels[chan_loc_code][component]['reference_code'] = values['reference_code']
                        if 'serial_number' in values :
                            self.channels[chan_loc_code][component]['serial_number'] = values['serial_number']
                        if debug:
                            print(chan_loc_code, component)
                            pprint.pprint(self.channels[chan_loc_code])
            else:
                print('''Serial number {} not found for instrument reference code {}, using standard instrument'''.format(\
                            serial_number,reference_code))

        # SET SERIAL NUMBER
        self.equipment['serial_number']=serial_number
    
        # SET AZIMUTH AND DIP FOR EACH CHANNEL
        azi_dip = instrumentation['azi_dip']
        for key,channel in self.channels.items():
            if debug:
                pprint.pprint(azi_dip)
                print(key, channel['azi_dip'])
            azi_dip_code = channel['azi_dip']['reference_code']
            if azi_dip_code in azi_dip:
                channel['azi_dip']=azi_dip[azi_dip_code]
            else:
                raise RuntimeError('{} is not a valid azi_dip reference code'.azi_dip_code)
                    
    def __repr__(self) :
        return "<  OBS_Instrument: reference_code={}, serial_number={}, {:d} channels >".format(
                                                    self.reference_code, 
                                                    self.serial_number, 
                                                    len(self.channels))
    def load_components(self,referring_file=None) :
        """
        Load components into instrument
        """
        components=OBS_InstrumentComponents(self.components_file,referring_file)
    
        self.fill_channels(components.functional_components)
        self.response_directory=components.response_directory
        self.resource_id=components.facility['reference_name'] + \
                                    components.revision['date']
    def fill_channels(self, functional_components, debug=False):
        """ Replace channel component strings with the actual components 
        
            functional_components is direct from instrument_components.yaml
        """
        for channel in self.channels.values():
            if debug:
                print(channel)
            for component_type in ['datalogger','preamplifier','sensor'] :
                reference_code = channel[component_type]['reference_code']
                serial_number=channel[component_type].get('serial_number',None)
                # FIRST FILL IN GENERIC COMPONENTS
                channel[component_type]= functional_components[component_type]['generic'][reference_code]
                channel[component_type]['reference_code']=reference_code
                # NEXT LOOK FOR SPECIFIC COMPONENTS
                if serial_number:
                    channel[component_type]['equipment']['serial_number']=serial_number
                    if 'specific' in functional_components[component_type]:
                        if serial_number in functional_components[component_type]['specific']:
                            specific=functional_components[component_type]['specific'][serial_number]
                            if 'response' in specific:
                                for key in specific['response']:
                                    channel[component_type]['response'][key]= specific['response'][key] 
                            if 'equipment' in specific:
                                for key in specific['equipment']:
                                    channel[component_type]['equipment'][key]= specific['equipment'][key] 
    def modify_sensors(self, sensor_dict, referring_file=None):
        """ Modify sensors within an instrument
        Inputs:
            sensor_dict: dictionary with key = component, val=[reference_code, serial_number]
        """
        
        components=load_yaml(self,components_file+root_symbol+'instrument_components/functional_components',
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
    def stuff_variables(self,station,debug=False):
        # Replaces variable names within self.channels
        for variable_name in self.variables:
            if variable_name in station.__dict__.keys():
                value=str(getattr(station,variable_name))
                replacetext='{'+variable_name+'}'
                if debug:
                    print('replacing "{}" by "{}"'.format(replacetext,value))
                yaml_str=yaml.dump(self.channels)
                yaml_str=yaml_str.replace(replacetext,value)
                self.channels=yaml.safe_load(yaml_str)
            else:
                print("variable '{}' was not found in station's top level")
    def fill_responses(self,referring_file=None) :
        for name,channel in self.channels.items() :
            channel['response']=[]
            stages=read_response_yamls( channel['sensor'], 
                                        self.response_directory,
                                        ['sensor','analog_filter'],
                                        referring_file)
            if len(stages) > 0:
                channel['response'].extend(stages) 
            stages=read_response_yamls( channel['preamplifier'],  
                                        self.response_directory,
                                        ['analog_filter'],
                                        referring_file)
            if len(stages) > 0:
                channel['response'].extend(stages) 
            stages=read_response_yamls( channel['datalogger'], 
                                        self.response_directory,
                                        [   'analog_filter',
                                            'digitizer',
                                            'digital_filter'
                                        ],
                                        referring_file)
            if len(stages) > 0:
                channel['response'].extend(stages) 
               
################################################################################       
class OBS_Station:
    """a station from the network.yaml file"""           
    def __init__(self,station_dict,station_code,network_code):
        """ station_dict is straight out of the network.yaml file"""
        # COULD THIS ALL BE DONE USING COLLECTIONS:NAMEDTUPLE???
        self.notes=station_dict['notes']
        self.site=station_dict['site']
        self.start_date=station_dict['start_date']
        self.end_date=station_dict['end_date']
        self.instrument=station_dict['instrument']
        self.comments=station_dict['comments']
        self.sample_rate=station_dict['sample_rate']
        self.locations=station_dict['locations']
        self.supplements=station_dict['supplements']
        self.code=station_code
        self.network_code=network_code
        # If no location_code set, use '00' (maybe should use only if '00'
        # exists, otherwise use single provided location code)
        self.location_code=station_dict.get('location_code','00')
        if 'sensors' in station_dict:
            self.sensors=station_dict['sensors']
        else:
            self.sensors=None
    def __repr__(self) :
        if hasattr(self.instrument,'channels'):
            txt =       "< OBS_Station: code={}, instrument=\n".format(
                                                                self.code)
            txt = txt + "      {} >".format(self.instrument)
            return txt
        else:
            txt =       "< OBS_Station: code={},".format(self.code)
            txt = txt + " instrument= ['{}','{}']\n".format(
                        self.instrument['reference_code'],
                        self.instrument['serial_number'])
            return txt
    def fill_Instrument(self,instrument_file,referring_file=None):
        """ Fills in instrument information """
        self.instrument=OBS_Instrument(instrument_file,
                            self.instrument['reference_code'],
                            self.instrument['serial_number'],
                            referring_file=referring_file)
        self.instrument.stuff_variables(self)
        self.instrument.load_components(referring_file)
        if self.sensors:
            print("Adding custom sensors")
            self.instrument.modify_sensors(self.sensors,referring_file)
        self.instrument.fill_responses(referring_file)
        self.operator=self.instrument.facility
        
    def partial_fill_Instrument(self,instrument_file,referring_file=None):
        """ Fills in instrument information, but without specific component information """
        self.instrument=OBS_Instrument(instrument_file,
                            self.instrument['reference_code'],
                            self.instrument['serial_number'],
                            referring_file=referring_file)
        self.instrument.stuff_variables(self)
        self.instrument.load_components(referring_file)
        #if self.sensors:
        #    print("Adding custom sensors")
        #    self.instrument.modify_sensors(self.sensors,referring_file)
        #self.instrument.fill_responses(referring_file)
        #self.operator=self.instrument.facility
    def make_obspy_station(self,debug=False):
        """
        Create an obspy station object from a fully informed station
        """
        # CREATE CHANNELS

        if debug:
            print(self)
        channels=[]
        resource_id=self.instrument.resource_id
        for key,chan in self.instrument.channels.items():
            response=make_obspy_response(chan['response'])
            loc_code=key.split(':')[1]
            location = self.locations[loc_code]
            obspy_lon,obspy_lat = calc_obspy_LonLats(location)
            start_date=None
            end_date=None
            # Give at least 3 seconds margin around start and end dates
            if hasattr(self,'start_date'):
                if self.start_date:
                    start_date=round_down_minute(UTCDateTime(self.start_date),3)
            if hasattr(self,'end_date'):
                if self.end_date:
                    end_date=round_up_minute(UTCDateTime(self.end_date),3)
            if False:
                print(key)
                print(yaml.dump(chan))
            #print(location)
            if 'localisation_method' in location:
                channel_comment=obspy_util.Comment('Localised using : {}'.format(
                        location['localisation_method']))
            channel = inventory.channel.Channel(
                    code = key.split(':')[0],
                    location_code  = loc_code,
                    latitude  = obspy_lat,
                    longitude = obspy_lon,
                    elevation = obspy_types.FloatWithUncertaintiesAndUnit(
                                        location['position'][2],
                                        lower_uncertainty=location['uncertainties_m'][2],
                                        upper_uncertainty=location['uncertainties_m'][2]),
                    depth     = location['depth'],
                    azimuth   = chan['azi_dip']['azimuth'],
                    dip       = chan['azi_dip']['dip'],
                    types      =['CONTINUOUS','GEOPHYSICAL'],
                    sample_rate=self.sample_rate, 
                    clock_drift_in_seconds_per_sample=1/(1e8*float(self.sample_rate)),
                    sensor     =make_obspy_equipment(chan['sensor']['equipment']),
                    pre_amplifier=make_obspy_equipment(chan['preamplifier']['equipment']),
                    data_logger=make_obspy_equipment(chan['datalogger']['equipment']),
                    equipment  =None,
                    response   =response,
                    description=None,
                    comments=[channel_comment],
                    start_date = start_date,
                    end_date   = end_date,
                    restricted_status = None,
                    alternate_code=None,
                    data_availability=None,
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
                                                station.instrument.channels
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
            'iris_code' : obs_station.code,
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
               
    def __make_devices_and_channels(self,oca_station,obs_channels):
    
        oca_station['channels']=list()
        devices=dict()
        for ch_code,values in obs_channels.items():
            devices, device_codes = self.__add_devices(devices,values)
            ###
            ch=self.__make_channel(ch_code,device_codes,values,
                                        oca_station['open_date'],
                                        oca_station['close_date'])
            oca_station['channels'].append(ch)
        oca_station['installed_devices']=devices   
        return oca_station
        
    def __add_devices(self,devices,values,debug=False):
        """
        Find devices or add to dictionary of "installed devices"
        
        devices= existing dictionary of devices
        values = values corresponding to this channel
        """
        codes=dict()
        if debug:
            print('===',values)
        
        sensor = self.__make_devicedict("sensor",values['sensor']['equipment'])
        sensor["azimuth_error"]= 180
        sensor["dip_error"]= 1
        sensor["local_depth"]= "0??"
        sensor["vault"]= "seafloor"
        sensor["config"]= "?single?"
                devices,codes['sensor']=self.__find_append_device(devices,sensor,'sensor')
        
        anafilter = self.__make_devicedict("anafilter",values['preamplifier']['equipment'])
        devices,codes['anafilter']=self.__find_append_device(devices,anafilter,'anafilter')
        
        das = self.__make_devicedict("das",values['datalogger']['equipment'])
        devices,codes['das']=self.__find_append_device(devices,das,'das')
            
        return devices,codes
        
    def __make_devicedict(metatype,equipment):
        devicedict = {
            "metatype": metatype,
            "manufacturer": equipment['manufacturer'],
            "model": equipment['model'],
            "serial_number": equipment['serial_number']
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
       
    def __make_channel(self,ch_code,device_codes,values,open_date,close_date) :
        ch= {
            "location_code" :     ch_code.split(':')[1],
            "iris_code" :         ch_code.split(':')[0],
            "sensor" :            device_codes['sensor'],
            "sensor_component" :  ch_code.split(':')[0][-1:],
            "das" :               device_codes['das'],
            "das_connector" :     "?1?", # ??????
            "das_component" :     "?1?", # ?????
            "das_digital_filter" : values['datalogger']['reference_code'],
            "azimuth" :           values['azi_dip']['azimuth'],
            "dip" :               values['azi_dip']['dip'],
            "data_format" :       "STEIM1",
            "polarity_reversal" : values['azi_dip']['dip']=="-90.0",
            "open_date" :         open_date,
            "close_date" :        close_date,
            "channel_flags" :     "CG"
        }
        return ch        
         
##################################################
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
##################################################
def load_yaml(path,referring_file=None,debug=False):
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
        referring_file: current file's full name, possible including it's path
                    This path (if any) will be prepended to the reference, as
                    referenced YAML files are assumed to be in (or referenced to
                    the same path as the referencing YAML files (like JSON Pointers) 
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
        print('path={}, referring_file={}'.format(path, referring_file))
        
    if filename:
        if referring_file:
            current_path=os.path.dirname(referring_file)
            filename=os.path.join(current_path,filename)
        else:
            current_path=os.getcwd()
    else:
        if referring_file:
            filename=referring_file
        else:
            raise RuntimeError("Internal path given without referring file")
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
            
    return element
        
def read_response_yamls(component,directory,subcomponent_list,
                        referring_file=None,debug=False) : 
    """ READ INSTRUMENT RESPONSES FROM RESPONSE_YAML FILES
    
    Input:
        component: component with dictionary of reponses in ['response']
        subcomponent_list: ordered list of possible response subcomponents
        directory: base directory of response_yaml files
    """
    stages=list()
    for subcomponent in subcomponent_list:    
        if subcomponent in component['response']:    
            filename=component['response'][subcomponent]
            if debug:
                print("Reading subcomponent '{}' from {}".format(\
                    subcomponent,os.path.join(directory,filename)))
                   
            file_stages=load_yaml(os.path.join(directory,filename)+root_symbol+'stages',
                        referring_file)
            for stage in file_stages:
                # IF STAGE HAS AN "INCLUDE" KEY, READ AND INJECT THE REFERRED FILE
                if 'include' in stage['response']:
                    # READ REFERRED FILE
                    include_file = os.path.join(directory,stage['response']['include'])
                    #with open(include_file,'r') as f:
                    #    response=yaml.safe_load(f)['response']
                    response=load_yaml(include_file+root_symbol+'response',referring_file)
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
                
            stages.extend(file_stages)
        
    if debug:
        print("{:d} total stages in component".format(len(stages)))
        print(yaml.dump(stages))
    return stages
    


##################################################
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
##################################################
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
                print('Unknown PoleZero response type: "{}"'.format(lstr))
                sys.exit(2)
            zeros = [float(t.split(',')[0]) + 1j * float(t.split(',')[1]) for t in resp['zeros']]
            poles = [float(t.split(',')[0]) + 1j * float(t.split(',')[1]) for t in resp['poles']]
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
            print('UNKNOWN STAGE RESPONSE TYPE: {}'.format(rtype))
            sys.exit()
    
    response=obspy_response_with_sensitivity(resp_stages,sensitivity)
    if debug:
        print(response)
            
    return response
##################################################
def make_obspy_equipment(equipment,installation_date=None,removal_date=None,
                            resource_id=None,debug=False):
    """
    Create obspy EquipmentType from obs_info.equipment
    
\    """
    if not 'description' in equipment:
        raise RuntimeError('Your equipment variable does not have a "description"')
    obspy_equipment = obspy_util.Equipment(
        type=          equipment.get('type',None),
        description=   equipment.get('description',None),
        manufacturer=  equipment.get('manufacturer',None),
        vendor=        equipment.get('vendor',None),
        model=         equipment.get('model',None),
        serial_number= equipment.get('serial_number',None),
        installation_date=installation_date,
        removal_date=removal_date,
        calibration_dates= equipment.get('calibration_date',None),
        resource_id=resource_id
    )
    if debug:
        print(equipment)
        print(obspy_equipment)
    return obspy_equipment
##################################################
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
    
##################################################
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
        print('{:.3f}+-{:.5f}, {:.3f}+-{:.5f}'.format(longitude,lon_uncert,
                                                    latitude,lat_uncert))
    obspy_lat  = obspy_util.Latitude(
                                latitude,
                                lower_uncertainty=lat_uncert,
                                upper_uncertainty=lat_uncert)    
    obspy_lon = obspy_util.Longitude(
                                longitude,
                                lower_uncertainty=lon_uncert,
                                upper_uncertainty=lon_uncert)
    
    
    return obspy_lon,obspy_lat 
