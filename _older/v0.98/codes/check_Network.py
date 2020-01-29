#!/usr/bin/env python3
""" 
Print complete stations from information in network.yaml file
"""
#from ruamel import yaml
import yaml
import pprint
import sys
import re
from obs_info import OBS_Network,OBS_Station

network_file='../obs-info/CAMPAIGN.FACILITY.network.yaml'

##############################################################################
##############################################################################

# READ IN NETWORK INFORMATION
network=OBS_Network(network_file)
print(network)
       
for name,station in network.stations.items():
    print('='*80)
    print('Station {}:'.format(name))
    #print(station)    
    station.fill_instrument(network.instrumentation_file,
                            referring_file=network_file
                        )
    
    print(station)
