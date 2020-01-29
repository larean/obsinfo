#!/usr/bin/env python3
""" 
Print stationXML from information in network.yaml file

"""
#import yaml
from obsinfo.network import network as oi_network
#from obsinfo.StationXML import StationXML
#from obspy.core import inventory
import os, os.path


network_file='../files/campaigns/MYCAMPAIGN/MYCAMPAIGN.FACILITY.network.yaml'
network_file='/Users/crawford/_Work/Parc_OBS/7_Missions/2017.AlpArray/2_after/ALPARRAY-OBS.INSU-IPGP.network.yaml'
destination_folder = 'outputs'

##############################################################################
##############################################################################
if not os.path.exists(destination_folder):
    os.mkdir(destination_folder)

# READ IN NETWORK INFORMATION
network=oi_network(network_file)
print(network)

for station in network.stations:
    network.write_stationXML(station,destination_folder)
    
