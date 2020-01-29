#!/usr/bin/env python3
""" 
Make Geoazur-OCA JSON station file from OBS info files
"""
import json
import obs_info

network_file='../information_files/CAMPAIGN.FACILITY.network.yaml'
##############################################################################
##############################################################################

# READ IN NETWORK INFORMATION
network=obs_info.OBS_Network(network_file)
oca_dict=network.make_oca_dict(referring_file=network_file)
print(json.dumps(oca_dict,indent=4))

