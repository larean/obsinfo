""" 
Print complete stations from information in network.yaml file
"""
import yaml
import pprint
import sys
import os.path
import re

network_file='EXAMPLE.INSU-IPGP.network.yaml'
# Stations to be completely printed, accepts regular expressions
fullPrint_stations='LSVHI'  # Just one stations
#fullPrint_stations='LS.*'  # All stations starting with "LS"
fullPrint_stations='.+' # All stations

pp=pprint.PrettyPrinter(width=131)

##################################################
def fill_channels(instrument, components, debug=False):
    """ Replace channel component strings with the actual components """
    if debug:
        pp.pprint(instrument)
        pp.pprint(components)
    for chan in instrument['channels'].values():
        if debug:
            print(chan)
        chan['datalogger']=components['datalogger'][chan['datalogger']]
        chan['ana_filter']=components['ana_filter'][chan['ana_filter']]
        chan['azi_dip']=   components['azi_dip'][chan['azi_dip']]
        if chan['sensor'] in components['sensor']:
            chan['sensor']=    components['sensor'][chan['sensor']]
        else:
            print("'{}' not found in instrumentation['models']['sensor']".format(
                chan['sensor']))
            sys.exit(2)
        if debug:
            print(chan)
    return instrument

##################################################
def load_instrument(instrument_file,inst_model, inst_serial_number):
    """ Load an instrument from a YAML instrumentation information file
    
    Inputs:
        instrument_file: name of the instrumentation file
        inst_model: The instrument model (must correspond to a key in 
                    instrumentation['models'][instrument])
        inst_serial_number: The instrument serial number.  If it corresponds to
                    a key in instrumentation['models'][inst_model], then the
                    instrument is modified as specified there.  If not, just
                    inserts the serial number into instrument['equipment']
        
    Output:
        instrument: the modified instrument object
        variables: a list of variable names (values which can be set to
                   something specified in the network file)
    """
    with open(instrument_file,'r') as f:
        tree=yaml.load(f)['instrumentation']
#     instruments=         tree['models']['instrument']
#     components=          tree['models']['component']
    models =         tree['models']
    instruments=models['instrument']
    instruments_specific=tree['individuals']['instrument']
    sensors_specific=    tree['individuals']['sensor']
    # Find instrument model
    instrument=instruments[inst_model]
    if debug:
#         pp.pprint(instruments)
#         pp.pprint(components)
        pp.pprint(models)
        pp.pprint(instruments_specific)
        pp.pprint(instrument)
    instrument=fill_channels(instrument,models)
    # If the instrument serial number is specified in the instrumentation file, load it
    if inst_serial_number in instruments_specific[inst_model]:
        for channel,mods in instruments_specific[inst_model][inst_serial_number].items() :
            for component,values in mods.items() :
                type=values['model']
                SN=values['serial_number']
                if not type:  # No type specified, just change serial number
                    instrument['channels'][channel][component]['serial_number']=SN
                else:
                    instrument['channels'][channel][component]=models[component][type]
                    instrument['channels'][channel][component]['serial_number']=SN
                    # Sensors can also have specific parameters according to their serial number
                    if component=='sensor' and SN in sensors_specific[type]:
                        for key in sensors_specific[type][SN].keys():
                            instrument['channels'][channel]['sensor'][key]=sensors_specific[type][SN][key]        
    else:
        print('''Serial number {} not found for instrument model {}\
, using standard model'''.format(inst_serial_number,inst_model))
    instrument['equipment']['serial_number']=inst_serial_number
    return instrument, tree['variables']

##################################################
def modify_sensors(instrument_file,instrument, sensor_dict):
    """ Modify sensors within an instrument
    
    Inputs:
        instrument_file: name of the instrumentation file
        instrument: The initial instrument object
        sensor_dict: dictionary with key = component, val=[model, serial_number]
        
    Output:
        instrument: the modified instrument object
    """
        
    with open(instrument_file,'r') as f:
        sensors         =yaml.load(f)['instrumentation']['models']['sensor']
    with open(instrument_file,'r') as f:
        sensors_specific=yaml.load(f)['instrumentation']['individuals']['sensor']
    for channel, values in sensor_dict.items():
        model=values['model']
        SN=values['serial_number']
        instrument['channels'][channel]['sensor']=sensors[model].copy()
        instrument['channels'][channel]['sensor']['serial_number']=SN
        print('Setting {} {} SN to {}'.format(channel,model,SN))
        if model in sensors_specific:
            if SN in sensors_specific[model]:
                for key,value in sensors_specific[model][SN].items():
                    print('Setting {} to {}'.format(key,value))
                    instrument['channels'][channel]['sensor'][key]=value        
            
    return instrument

##################################################
def stuff_variables(instrument,variables,station):
    for variable in variables:
        if variable in station:
            value=str(station[variable])
            replacetext='{'+variable+'}'
            print('replacing "{}" by "{}"'.format(replacetext,value))
            # Make a string representation of the instrument
            inst_str=yaml.dump(instrument)
            #print(inst_str)
            # change all occurences of {variable} to value
            inst_str=inst_str.replace(replacetext,value)
            #print(inst_str)
            # convert instrument back to pythonic
            instrument=yaml.load(inst_str)
        else:
            print("variable '{}' was not found in station's top level")
    return instrument

##################################################
def read_responses(filenames,directory) : 
    """ READ INSTRUMENT RESPONSE FROM RESPONSE_YAML FILE"""
    stages=list()
    for filename in filenames:    
        # Read in list of stages  
        with open(os.path.join(directory,filename),'r') as f:
            file_stages=yaml.load(f)['stages']

        for stage in file_stages:
            # IF STAGE HAS AN "INCLUDE" KEY, READ AND INJECT THE REFERRED FILE
            if 'include' in stage['response']:
                # READ REFERRED FILE
                include_file = os.path.join(directory,stage['response']['include'])
                with open(include_file,'r') as f:
                    response=yaml.load(f)['response']
                # MAKE SURE IT'S THE SAME TYPE, IF SO INJECT
                if stage['response']['type'] == response['type'] :
                    stage['response']=response
                else:
                    print("Error, response and its included file don't have the same type") 
                    print('   "{}" : "{}" versus "{}"'.format(filename,
                                                    stage['response']['type'],
                                                    response['type']) )
    stages.append(file_stages)
    return stages
    
##################################################
def fill_responses(instrument,response_directory) :
    for name,channel in instrument['channels'].items() :
        channel['response'] = read_responses(channel['sensor']['response_files'],response_directory)
        channel['response'].append(read_responses(channel['ana_filter']['response_files'],response_directory))
        channel['response'].append(read_responses(channel['datalogger']['response_files'],response_directory))
    return instrument

# OPTIONAL FUTURE METHOD IF CHANGE TO SEPARATE SPECIFICATION OF RESPONSE FILES
#     for channel in instrument['channels'] :
#         channel['response']=list()
#         for response_file in channel['response_files'] :
#             channel['response'].append(read_response(response_file))
    
##############################################################################
##############################################################################
debug=False
with open(network_file,'r') as f:
  stations=yaml.load(f)['network']['stations']
with open(network_file,'r') as f:
  instrument_file=yaml.load(f)['network']['instrumentation_file']
  
with open(instrument_file,'r') as f:
    response_directory=yaml.load(f)['instrumentation']['response_directory']
    
for name,station in stations.items():
    print('='*80)
    print('Station {}:'.format(name))
    if debug:
        pp.pprint(station['instrument'])
    instrument,variables=load_instrument(
                    instrument_file,
                    station['instrument']['model'],
                    station['instrument']['serial_number'])
    if 'sensors' in station:
        instrument = modify_sensors(instrument_file,
                    instrument,
                    station['sensors'])
    # Stuff any instrument variables
    instrument=stuff_variables(instrument,variables,station)
    # Read in instrument responses
    instrument=fill_responses(instrument,response_directory)
        
    # Put instrument values in station
    station['instrument_parameters']=station['instrument']
    station['instrument']=instrument
    #print(name)
    if re.search(fullPrint_stations,name):
        #pp.pprint(station)
        print("DUMPING STATION OBJECT:")
        #pprint.pprint(station)
        print(yaml.dump(station))
    print('')