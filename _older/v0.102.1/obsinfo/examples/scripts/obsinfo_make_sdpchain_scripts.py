#!/usr/bin/env python3
""" 
Print stationXML from information in network.yaml file
"""
from obsinfo.network import network as oi_network
from obsinfo.addons import LCHEAPO as LCHEAPO
from obsinfo.addons import SDPCHAIN as SDPCHAIN
import os, os.path


network_file='../data/campaigns/MYCAMPAIGN/MYCAMPAIGN.INSU-IPGP.network.yaml'
destination_folder = 'outputs'

stations_base='/Volumes/PARC_OBS_HTFS/2018.AlpArray/2018.AlpArray/'
sdpchain_base='/Users/crawford/_Work/Parc_OBS/3_Development/Data_and_Metadata/SDPCHAIN/Software_IPGP-INSU_v20170222_modWayne/BUILD/SDPCHAIN/'
lc2ms_dir = '/Users/crawford/_Work/Parc_OBS/3_Development/Data_and_Metadata/SDPCHAIN/Software_IPGP-INSU_v20170404/INSTALL/lc2ms'
ms2sds_dir= sdpchain_base + 'MS2SDS'
msdrift_dir=sdpchain_base + 'MSDRIFT'


##############################################################################
##############################################################################
# MAKE FOLDER FOR SCRIPTS
if not os.path.exists(destination_folder):
    os.mkdir(destination_folder)

# READ IN NETWORK INFORMATION
network=oi_network(network_file)
print(network)

for name,station in network.stations.items():
    print("\t"+str(station))
    station_dir=os.path.join(stations_base,name)
    script_1=LCHEAPO.process_script(station,station_dir,
                                    lc2ms_dir)
    script_2=SDPCHAIN.process_script(station,station_dir,
                                    msdrift_dir,ms2sds_dir,
                                    include_header=False)
    fname=os.path.join(destination_folder,'process_'+name+'.sh')
    with open(fname,'w') as f:
        f.write(script_1)
        f.write('\n')
        f.write(script_2)
        f.close()
        
    
