#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Creates StationXML files from a network file and instrumentation file tree

Example
=======

obsinfo-make_STATIONXML MYCAMPAIGN.MYFACILTY.network.yaml

"""
from argparse import ArgumentParser
from obsinfo.network import network as oi_network
import os.path

def main(argv=None):
    parser = ArgumentParser( description=__doc__)
    parser.add_argument( 'network_file', help='Network information file')
    parser.add_argument( '-d', '--dest_path', 
                help='Destination folder for StationXML files')
    #parser.add_argument( '-v', '--verbose',action="store_true",
    #            help='increase output verbosiy')
    args = parser.parse_args()
    
    if args.dest_path:
        if not os.path.exists(args.dest_path):
            os.mkdir(args.dest_path)

    # READ IN NETWORK INFORMATION
    network=oi_network(args.network_file)
    print(network)

    for station in network.stations:
        network.write_stationXML(station,args.dest_path)

         
if __name__ == "__main__":
    main()
   