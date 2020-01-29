#!/usr/bin/env python3
import yaml
import pprint
from obs_info import OBS_InstrumentComponents

components_file='../obs-info/FACILITY.instrument-components.yaml'

components=OBS_InstrumentComponents(components_file)

print('\nFILENAME: {}'.format(components_file))
print('FACILITY: {}'.format(components.facility_reference_name))
print('REVISION: {}'.format(components.revision))
# PRINT INSTRUMENTS
print(10*'=')
print('DATALOGGERS:')
components.print_elements('datalogger')
print(10*'=')
print('PREAMPLIFIERS:')
components.print_elements('preamplifier')
print(10*'=')
print('SENSORS:')
components.print_elements('sensor')

# VERIFY THAT COMPONENTS LISTED IN "specific" EXIST in "generic"
print(10*'=')
if components.verify_individuals():
    print('All specific components have a generic counterpart')

# VERIFY THAT REFERRED TO FILES EXIST
print(10*'=')
n_files, n_found, n_cites = components.verify_source_files(print_names=True)
if n_files==n_found:
    print('Found all {:d} specified source files ({:d} total citations)'\
                    ''.format(n_files,n_cites))
else:
    print('MISSING {:d} of {:d} specified source files'\
                    ''.format(n_files-n_found,n_files))