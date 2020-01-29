#!/usr/bin/env python3
""" 
Print stationXML from information in network.yaml file
"""
import obsinfo.network as oi_network
import obsinfo.addons.SDPCHAIN as SDPCHAIN
import os, os.path


network_file='../files/CAMPAIGN.FACILITY.network.yaml'
destination_folder = 'outputs'

##############################################################################
##############################################################################
if not os.path.exists(destination_folder):
    os.mkdir(destination_folder)

# READ IN NETWORK INFORMATION
network=oi_network(network_file)
print(network)

for station in network.stations:
    SDPCHAIN.write_processing_blocks(station,destination_folder)
    
