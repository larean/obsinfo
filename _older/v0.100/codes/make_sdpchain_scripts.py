#!/usr/bin/env python3
""" 
Print stationXML from information in network.yaml file

"""
#import yaml
import obsinfo
#from obspy.core import inventory
import os, os.path


network_file='../files/CAMPAIGN.FACILITY.network.yaml'
destination_folder = 'outputs'

##############################################################################
##############################################################################
if not os.path.exists(destination_folder):
    os.mkdir(destination_folder)

# READ IN NETWORK INFORMATION
network=obsinfo.OBS_Network(network_file)
print(network)

for station in network.stations:
    network.write_processing_blocks(station,destination_folder)
    
