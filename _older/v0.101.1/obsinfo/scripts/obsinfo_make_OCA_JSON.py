#!/usr/bin/env python3
""" 
Make Geoazur-OCA JSON station file from OBS info files
"""
import json
import obsinfo
import obsinfo_OCA
import os, os.path

network_file='../files/CAMPAIGN.FACILITY.network.yaml'
destination_folder = 'outputs'
debug=False
##############################################################################
##############################################################################
if not os.path.exists(destination_folder):
    os.mkdir(destination_folder)

# READ IN NETWORK INFORMATION
network=obsinfo.OBS_Network(network_file)
print(network)
oca_dict=obsinfo_OCA.OCA_Network(network).dict
#.make_oca_dict(referring_file=network_file)

if debug:
    print(json.dumps(oca_dict,indent=4))
    
# WRITE TO FILE
fname=os.path.join(destination_folder,f'{network.network_info.code}_OCA.json')
print("Writing to", fname)    
with open(fname,'w') as f:
    f.write(json.dumps(oca_dict,indent=4))

