#!/usr/bin/env python3
""" 
Print stationXML from information in network.yaml file

STILL NEED TO RESOLVE WHY SENSITIVITY IS VERY DIFFERENT FROM GUESSTIMATED
"""
#from ruamel import yaml
import yaml
import obs_info
from obspy.core import inventory


network_file='../information_files/CAMPAIGN.FACILITY.network.yaml'
debug=False

##############################################################################
##############################################################################

# READ IN NETWORK INFORMATION
network=obs_info.OBS_Network(network_file)

for name,station in network.stations.items():
    print('='*80)
    print('Station {}:'.format(name))
    
    print("Loading and filling station")    
    station.fill_Instrument(network.instrumentation_file,
                            referring_file=network_file)
    
    print("Creating obsPy inventory object")    
    my_inv= network.make_obspy_inventory([station],'INSU-IPGP OBS Park')

    if debug:
        print(yaml.dump(my_inv))

    print("Writing to StationXML")    
    my_inv.write('{}.{}.STATION.xml'.format(
                                        network.network_info.code,
                                        name),
                            'STATIONXML')

