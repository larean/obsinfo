#!/usr/bin/env python3
""" 
Print stationXML from information in network.yaml file

"""
#from ruamel import yaml
import yaml
import obs_info
from obspy.core import inventory
import os, os.path


network_file='../obs-info/CAMPAIGN.FACILITY.network.yaml'
network_file='../obs-info/ALPARRAY-OBS.INSU-IPGP.network.yaml'
debug=False
destination_folder = 'outputs'

##############################################################################
##############################################################################
if not os.path.exists(destination_folder):
    os.mkdir(destination_folder)
# READ IN NETWORK INFORMATION
network=obs_info.OBS_Network(network_file)

for name,station in network.stations.items():
    print('='*80)
    print('Station {}:'.format(name))
    
    print("Loading and filling station")    
    station.fill_instrument(network.instrumentation_file,
                            referring_file=network_file)
    
    print("Creating obsPy inventory object")    
    my_inv= network.make_obspy_inventory([station],'INSU-IPGP OBS Park')

    if debug:
        print(yaml.dump(my_inv))

    fname=os.path.join(destination_folder,
                    '{}.{}.STATION.xml'.format(network.network_info.code,name))
    print("Writing to", fname)    
    my_inv.write(fname,'STATIONXML')

