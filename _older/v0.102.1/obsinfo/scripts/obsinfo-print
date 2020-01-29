#! env python3
# -*- coding: utf-8 -*-
"""
Prints summary of an information file

Also confirms existence of referenced file(s)

Example
=======

To validate the network file MYCAMPAIGN.MYFACILITY.network.yaml:

   obsinfo-print MYCAMPAIGN.MYFACILITY.network.yaml
"""
from argparse import ArgumentParser
import obsinfo.misc.validate as validate

valid_types=validate.list_valid_types()
valid_formats=['json','yaml']

def main(argv=None):
    parser = ArgumentParser( description=__doc__)
    parser.add_argument( 'info_file', help='Information file')
    parser.add_argument( '-t', '--type', choices=valid_types, default=None,
        help='Forces information file type (overrides interpreting from filename)')
    parser.add_argument( '-f', '--format', choices=valid_formats, default=None,
        help='Forces information file format (overrides interpreting from filename)')
    parser.add_argument( '-v', '--verbose',action="store_true",
        help='increase output verbosiy')
    args = parser.parse_args()
    
        
    validate.print_summary(args.info_file,format=args.format,type=args.type,verbose=args.verbose)
 
if __name__ == "__main__":
    main()
   