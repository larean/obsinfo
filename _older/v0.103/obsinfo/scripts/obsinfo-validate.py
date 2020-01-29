#! env python3
# -*- coding: utf-8 -*-
"""
Validate an obsinfo information file

Validates a file named *.{TYPE}.json or *.{TYPE}.yaml against the 
obsinfo schema.{TYPE}.json file.

{TYPE} can be campaign, network, instrumentation, instrument-components or
response

Example
=======

To validate the network file MYCAMPAIGN.MYFACILITY.network.yaml:

   obsinfo-validate MYCAMPAIGN.MYFACILITY.network.yaml
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
            
    validate.validate(args.info_file,format=args.format,type=args.type,verbose=args.verbose)
 
if __name__ == "__main__":
    main()
   