""" 
Print complete stations from information in network.yaml file
"""
#from ruamel import yaml
import sys
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

##################################################
def read_network(network_file,referring_file=None):
#     with open(network_file,'r') as f:
#         network=yaml.safe_load(f)['network']
    network=load_yaml(network_file+root_symbol+'network',referring_file)
    
    # Place the station codes within the stations
    for key,station in network['stations'].items():
        station['code']=key
  
    return network

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
            print('Error: more than one occurence of "{}" in file reference'.format(
                    root_symbol))
            sys.exit(2)
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
        print("Error: no internal path in '{}'".format(path))
        sys.exit(2)
            
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
            print('Error: internal path given without referring file')
            sys.exit(2)
    if debug:
        print('filename={}, internal_path={}'.format(filename,internal_path))
        
    internal_paths=internal_path.split('/')    
    with open(filename,'r') as f:
        element=yaml.safe_load(f)[internal_paths[0]]
    
    if len(internal_paths) > 1:
        for key in internal_paths[1:] :
            if not key in element:
                print('Error: internal path {} not found in file {}'.format(\
                        internal_path,filename))
            else:
                element=element[key]
            
    return element
        
##################################################
def load_station(station,instrument_file,referring_file=None):
    """
    Loads a station (instrument, components, responses)
    """
    instrument,facility=load_instrument(instrument_file,
                                    station['instrument']['model'],
                                    station['instrument']['serial_number'],
                                    referring_file=referring_file)
    instrument=stuff_variables(instrument,station)
    print("Loading components")
    instrument=load_components(instrument,referring_file)
    #instrument=stuff_variables(instrument,station)
    if 'sensors' in station:
        print("Adding custom sensors")
        instrument = modify_sensors(instrument, station['sensors'],referring_file)
    print("Filling in instrument responses")
    instrument=fill_responses(instrument,referring_file)        
    station['instrument']=instrument
    station['operator']=facility
    return station

##################################################
def fill_channels(instrument, components, debug=False):
    """ Replace channel component strings with the actual generic components """
    for channel in instrument['channels'].values():
        if debug:
            print(channel)
        for component_name in ['datalogger','preamplifier','sensor'] :
            model_name = channel[component_name]['model']
            SN=channel[component_name].get('serial_number',None)
            # FIRST FILL IN GENERIC COMPONENTS
            #print(component_name,model_name)
            channel[component_name]= components['generic'][component_name][model_name]
            # NEXT LOOK FOR SPECIFIC COMPONENTS
            if SN:
                channel[component_name]['equipment']['serial_number']=SN
                if component_name in components['specific']:
                    if SN in components['specific'][component_name]:
                        specific=components['specific'][component_name]
                        if 'response' in specific:
                            for key in specific['response']:
                                channel[component_name]['response'][key]= specific['response'][key] 
                        if 'equipment' in specific:
                            for key in specific['equipment']:
                                channel[component_name]['equipment'][key]= specific['equipment'][key] 
            
        if debug:
            print(chan)
    return instrument

##################################################
def load_instrument(instrument_file,model_name,serial_number,referring_file=None,
    debug=False):
    """ Load an instrument 
    
    Inputs:
        instrument_file: name of the instrumentation file
        model_name: The instrument model (must correspond to a key in 
                    instrumentation['models'][instrument])
        
    Output:
        instrument: one instrument, with components filled in (but not responses)
        facility: the instrument's facility information
    """
    
    # READ IN INSTRUMENTATION INFORMATION
#     with open(instrument_file,'r') as f:
#         instrumentation=yaml.safe_load(f)['instrumentation']
    instrumentation=load_yaml(instrument_file + root_symbol + 'instrumentation',
                                referring_file)
        
    # LOAD GENERIC INSTRUMENT MODEL
    instrument=instrumentation['models']['generic'][model_name]
    instrument['components_file']=instrumentation['components_file']
    instrument['variables']=instrumentation['variables']

    if debug:
        print(yaml.dump(instrument))

    # LOAD SPECIFIC INSTRUMENT MODEL, IF IT EXISTS
    if model_name in instrumentation['models']['specific']:
        specific_model=instrumentation['models']['specific'][model_name]
        if serial_number in specific_model:
            for chan_loc_code,components in specific_model[serial_number]['channels'].items() :
                for component,values in components.items() :
                    if 'model' in values:
                        instrument['channels'][chan_loc_code][component]['model'] = values['model']
                    if 'serial_number' in values :
                        instrument['channels'][chan_loc_code][component]['serial_number']=values['serial_number']
                    else:
                        SN=None
                    if debug:
                        print(chan_loc_code, component)
                        pprint.pprint(instrument['channels'][chan_loc_code])
        else:
            print('''Serial number {} not found for instrument model {}, using standard model'''.format(\
                        serial_number,model_name))

    # SET SERIAL NUMBER
    instrument['equipment']['serial_number']=serial_number
    
    # FILL IN AZIMUTH AND DIP FOR EACH CHANNEL
    azi_dip = instrumentation['azi_dip']
    for key,channel in instrument['channels'].items():
        if debug:
            pprint.pprint(azi_dip)
            print(key, channel['azi_dip'])
        channel['azi_dip']=azi_dip[channel['azi_dip']['model']]
        
    if debug:
        pprint.pprint(instrument)
    return instrument, instrumentation['facility']
        
##################################################
def load_components(instrument,referring_file=None) :
    """
    Load components into instrument
        
    Inputs:
        instrument: One instrument, read in by load_generic_instrument
    """
    #READ IN COMPONENTS INFORMATION
#     with open(instrument['components_file'],'r') as f:
#         components=yaml.safe_load(f)['instrumentation_components']
    components=load_yaml(instrument['components_file']+root_symbol+'instrumentation_components',
                        referring_file)
    
    instrument=fill_channels(instrument,components['models'])
    instrument['response_directory']=components['response_directory']
    # Create a resource ID ("equipment with the same ID should contain the same
    #    information / be derived from the same base instruments") [stationxml.xsd]
    instrument['resource_id']=components['facility']['reference_name'] + \
                                components['revision']['date']
    
    return instrument

##################################################
def modify_sensors(instrument, sensor_dict, referring_file=None):
    """ Modify sensors within an instrument
    
    Inputs:
        instrument: The input instrument object
        sensor_dict: dictionary with key = component, val=[model, serial_number]
        
    Output:
        instrument: the modified instrument object
    """
        
#     with open(instrument['components_file'],'r') as f:
#         components =yaml.safe_load(f)['instrumentation_components']['models']
    components=load_yaml(instrument['components_file']+root_symbol+'instrumentation_components',
                        referring_file)
    sensors_generic = components['generic']['sensor']
    sensors_specific= components['specific']['sensor']
    
    for channel, values in sensor_dict.items():
        model=values['model']
        SN=values['serial_number']
        instrument['channels'][channel]['sensor']=sensors_generic[model].copy()
        instrument['channels'][channel]['sensor']['serial_number']=SN
        print('Setting {} {} SN to {}'.format(channel,model,SN))
        if model in sensors_specific:
            if SN in sensors_specific[model]:
                for key,value in sensors_specific[model][SN].items():
                    print('Setting {} to {}'.format(key,value))
                    instrument['channels'][channel]['sensor'][key]=value        
            
    return instrument

##################################################
def stuff_variables(instrument,station):
    for variable in instrument['variables']:
        if variable in station:
            value=str(station[variable])
            replacetext='{'+variable+'}'
            print('replacing "{}" by "{}"'.format(replacetext,value))
            # Make a string representation of the instrument
            inst_str=yaml.dump(instrument)
            # change all occurences of {variable} to value
            inst_str=inst_str.replace(replacetext,value)
            # convert instrument back to pythonic
            instrument=yaml.safe_load(inst_str)
        else:
            print("variable '{}' was not found in station's top level")
    return instrument

##################################################
def read_responses_yaml(component,directory,subcomponent_list,
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
                   
#             with open(os.path.join(directory,filename),'r') as f:
#                 file_stages=yaml.safe_load(f)['stages']
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
                        print("Error, response and its included file don't have the same type") 
                        print('   "{}" : "{}" versus "{}"'.format(filename,
                                                        stage['response']['type'],
                                                        response['type']) )
            if debug:
                #print(file_stages)
                print("{:d} stages read".format(len(file_stages)))
                
            stages.extend(file_stages)
        
    if debug:
        print("{:d} total stages in component".format(len(stages)))
        print(yaml.dump(stages))
    return stages
    
##################################################
def fill_responses(instrument,referring_file=None) :
    for name,channel in instrument['channels'].items() :
        #print(channel['sensor'])
        channel['response']=[]
        stages=read_responses_yaml( channel['sensor'], 
                                    instrument['response_directory'],
                                    ['sensor','analog_filter'],
                                    referring_file)
        if len(stages) > 0:
            channel['response'].extend(stages) 
        stages=read_responses_yaml( channel['preamplifier'],  
                                    instrument['response_directory'],
                                    ['analog_filter'],
                                    referring_file)
        if len(stages) > 0:
            channel['response'].extend(stages) 
        stages=read_responses_yaml( channel['datalogger'], 
                                    instrument['response_directory'],
                                    [   'analog_filter',
                                        'digitizer',
                                        'digital_filter'
                                    ],
                                    referring_file)
        if len(stages) > 0:
            channel['response'].extend(stages) 
    return instrument

##################################################
def make_obspy_inventory(network,stations=None,source=None,debug=False):
    """
    Make an obspy inventory object, possibly with a subset of station names
    """
    
    my_net=make_obspy_network(network,stations)
    
    if not source:
        source = network['revision']['author']['first_name'] +\
                     ' ' +\
                 network['revision']['author']['last_name']
    my_inv = inventory.inventory.Inventory(
                    [my_net],
                    source
    )
    return my_inv
##################################################
def make_obspy_network(network,stations,debug=False):
    """
    Make an obspy network object, possibly with a subset of station names
    """
     
    obspy_stations=[]    
    for station in stations:
            obspy_stations.append(make_obspy_station(station))
    
    net_info=network['network_info']
    temp=net_info.get('comments',None)
    if temp:
        comments=[]
        for comment in temp:
            comments.append(obspy_util.Comment(comment))
    my_net = inventory.network.Network(net_info['code'],
                                obspy_stations,
                                description=net_info.get('description',None),
                                comments=comments,
                                start_date=UTCDateTime(net_info['start_date']),
                                end_date=UTCDateTime(net_info['end_date']))
    return my_net

##################################################
def make_obspy_station(station,debug=False):
    """
    Create an obspy station object from a fully informed station
    """
    # CREATE CHANNELS

    if debug:
        print(yaml.dump(station))
    channels=[]
    resource_id=station['instrument']['resource_id']
    for key,chan in station['instrument']['channels'].items():
        response=make_obspy_response(chan['response'])
        loc_code=key.split(':')[1]
        location = station['locations'][loc_code]
        obspy_lon,obspy_lat = calc_obspy_LonLats(location)
        start_date=None
        end_date=None
        # Give at least 3 seconds margin around start and end dates
        if 'start_date' in station:
            if station['start_date']:
                start_date=round_down_minute(UTCDateTime(station['start_date']),3)
        if 'end_date' in station:
            if station['end_date']:
                end_date=round_up_minute(UTCDateTime(station['end_date']),3)
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
                sample_rate=station['sample_rate'], 
                clock_drift_in_seconds_per_sample=1/(1e8*float(station['sample_rate'])),
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
    station_loc_code=station.get('station_location_code','00')
    if station_loc_code in station['locations']:
        sta_loc=station['locations'][station_loc_code]
        obspy_lon,obspy_lat = calc_obspy_LonLats(sta_loc)
    else:
        print ("No valid location code for station, either set station_location_code or provide a location '00'")
        sys.exit()
    
    
    obspy_comments = make_obspy_comments(
                    station['comments'],
                    station['supplements'],
                    station_loc_code,
                    sta_loc
                )
    # DEFINE Operator
    agency=station['operator']['full_name']
    contacts=None
    if 'email' in station['operator']:
        contacts=[obspy_util.Person(emails=[station['operator']['email']])]
    website=station['operator'].get('website',None)
    operator = obspy_util.Operator([agency],contacts,website)
    
    if debug:
        print(obspy_comments)
    sta=inventory.station.Station(
                code      = station['code'],
                latitude  = obspy_lat,
                longitude = obspy_lon,
                elevation = obspy_types.FloatWithUncertaintiesAndUnit(
                                    sta_loc['position'][2],
                                    lower_uncertainty=sta_loc['uncertainties_m'][2],
                                    upper_uncertainty=sta_loc['uncertainties_m'][2]),
                channels = channels,
                site     = obspy_util.Site(station.get('site','')),
                vault    = sta_loc['vault'],
                geology  = sta_loc['geology'],
                equipments= [make_obspy_equipment(station['instrument']['equipment'])],
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
    
##################################################
def make_oca_station(station):
    """
    Create an OCA station object (corresponds to a station without component details)
    """
    oca_station=dict()
    station['location_code']=station.get('location_code','00')
    # STATION INFORMATION SECTION
    oca_station['iris_code']= station['fdsn_code']
    oca_station['site']= station['site']
    oca_station['comments']= station['comments']
    for key,value in station['supplements'].items():
        oca_station['comments'].extend(json.dumps({ key : value }))
    oca_station['open_date']= station['start_date']
    oca_station['longitude']=station['locations'][station['location_code']]['position'][0]
    oca_station['latitude']= station['locations'][station['location_code']]['position'][1]
    oca_station['altitude']= station['locations'][station['location_code']]['position'][2]
    oca_station['altitude_unit']= 'm'
    oca_station['first_install']= station['start_date']
    oca_station['close_date']= station['end_date']
    
    # "CHANNELS" AND "INSTALLED DEVICES" SECTION
    das_list=[]
    sensor_list=[]
    oca_station['channels']=[]
    oca_station['installed_devices'] = {}
    for key,values in station['instrument']['channels'].items():
        # FIRST  CHECK IF IDENTICAL DAS AND/OR SENSOR HAVE ALREADY BEEN SPECIFIED
        # IF SO, USE THEIR "INSTALLED DEVICE" CODE(S)
        # IF NOT, CREATE A NEW "INSTALLED DEVICE" CODE
        das = {         'model':values['datalogger']['model'],
                'serial_number':values['datalogger']['serial_number']}
        sensor = {         'model':values['sensor']['model'],
                'serial_number':values['sensor']['serial_number']}
        if das in [x['values'] for x in das_list] :
            das_code=[x['das_code'] for x in das_list if das==x['values']][0]
        else:
            das_code = 'i{:d}_das'.format(len(das_list)+1)
            das_list.append({"das_code":das_code , "values":das})
            # FILL UP A DAS DESCRIPTION DICTIONARY
            temp={}
            oca_station['installed_devices'][das_code]=temp.copy()
        if sensor in [x['values'] for x in sensor_list] :
            sensor_code=[x['das_code'] for x in sensor_list if sensor==x['values']][0]
        else:
            sensor_code = 'i{:d}_sensor'.format(len(sensor_list)+1)
            sensor_list.append({"sensor_code":sensor_code , "values":sensor})
            # FILL UP A SENSOR DESCRIPTION DICTIONARY
            temp={}
            oca_station['installed_devices'][sensor_code]=temp.copy()
        ch=[]
        ch["location_code"] = key.split(':')[1]
        ch["iris_code"] = key.split(':')[0]
        ch["sensor"] = sensor_code
        ch["sensor_component"] = key.split(':')[0][-1:]
        ch["das"] = das_code
        ch["das_connector"] = "1" # ??????
        ch["das_component"] = "1" # ?????
        ch["das_digital_filter"] = values['digital_filter']
        ch["data_format"] = "STEIM1"
        ch["polarity_reversal"] = dip=="-90.0"
        ch["open_date"] = station['start_date']
        ch["close_date"] = station['end_date']
        ch["channel_flags"]="CG"
        oca_station['channels'].append(ch.copy())
        
    return oca_station
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
    
    Works for station:equipment, but not for station:channel:preamplifier or
    datalogger or sensor.  Because lacking dates or resource id?
    """
    if not 'description' in equipment:
        print('ERROR: your equipment variable does not have a "description"')
        sys.exit(2)
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
