#!/usr/bin/env python3
""" 
Print complete stations from information in network.yaml file
"""
#from ruamel import yaml
import yaml
import pprint
import sys
import re
import obs_info

network_file='../information_files/CAMPAIGN.FACILITY.network.yaml'
# Stations to be completely printed, accepts regular expressions
fullPrint_stations='LSVHIrt'  # Just one stations
#fullPrint_stations='LS.*'  # All stations starting with "LS"
fullPrint_stations='.+' # All stations
fullPrint_depth = None     # 'None' gives everything, 3 gives a short summary
debug=False

pp=pprint.PrettyPrinter(width=131)

##############################################################################
##############################################################################

# READ IN NETWORK INFORMATION
network=obs_info.read_network(network_file)
       
for name,station in network['stations'].items():
    print('='*80)
    print('Station {}:'.format(name))
    if debug:
        pp.pprint(station['instrument'])
        
    station=obs_info.load_station(station,network['instrumentation_file'],referring_file=network_file)
    
    if re.search(fullPrint_stations,name):
        if fullPrint_depth:
            print("DUMPING FIRST {:d} LEVELS OF STATION OBJECT:".format(fullPrint_depth))
            pprint.pprint(station,depth=fullPrint_depth)
        else:
            print("DUMPING FULL STATION OBJECT:")
            print(yaml.dump(station))
    print('')