#!/usr/bin/env python3
""" 
Print complete stations from information in network.yaml file
"""
#from ruamel import yaml
#import yaml
#import pprint
#import sys
#import re
from obsinfo.network import network

network_file='../Information_Files/campaigns/MYCAMPAIGN/MYCAMPAIGN.INSU-IPGP.network.yaml'

##############################################################################
##############################################################################

# READ IN NETWORK INFORMATION
network=network(network_file)
print(network)
       
for name,station in network.stations.items():
    print('='*80)
    print('Station {}:'.format(name))
    #print(station)    
    station.fill_instrument(network.instrumentation_file,
                            referring_file=network_file
                        )
    
    print(station)
