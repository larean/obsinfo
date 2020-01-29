#!/usr/bin/env python3
""" 
Print complete stations from information in network.yaml file
"""
#from ruamel import yaml
import yaml
import sys
import obs_info

network_file='../information_files/CAMPAIGN.FACILITY.network.yaml'
debug=True

##############################################################################
##############################################################################

# READ IN NETWORK INFORMATION
network=obs_info.read_network(network_file)
       
for name,station in network['stations'].items():
    print('='*80)
    print('Station {}:'.format(name))
    
    # LOAD INSTRUMENT INTO STATION, WITHOUT SPECIFIC COMPONENT INFORMATION    
    instrument,facility=obs_info.load_instrument(network['instrumentation_file'],
                                    station['instrument']['model'],
                                    station['instrument']['serial_number'],
                                    referring_file=network_file)
    station['fdsn_code']=network['network_info']['code']
    print(yaml.dump(station))
    instrument=obs_info.stuff_variables(instrument,station)
    station['instrument'] = instrument
    
    # CREATE OCA-STYLE JSON STRING FOR THE STATION
    oca_sta=obs_info.make_oca_station(station)
    
    print(json.dumps(oca_sta))

    if debug:
        print(yaml.dump(instrument))
    
