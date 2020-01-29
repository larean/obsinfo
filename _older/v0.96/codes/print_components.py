#!/usr/bin/env python3
import yaml
import pprint
from obs_info import OBS_InstrumentComponents

components_file='../information_files/FACILITY.instrument_components.yaml'

components=OBS_InstrumentComponents(components_file)

print('\nFILENAME: {}'.format(components_file))
print('FACILITY: {}'.format(components.facility['reference_name']))
print('REVISION: {} ({})'.format(components.revision['date'],
                            components.revision['author']))
# PRINT INSTRUMENTS
print('\n===========')
print('DATALOGGERS:')
components.printElements('datalogger')
print('\n===========')
print('PREAMPLIFIERS:')
components.printElements('preamplifier')
print('\n===========')
print('SENSORS:')
components.printElements('sensor')

# VERIFY THAT COMPONENTS LISTED IN "specific" EXIST in "generic"
print('\n===========')
if components.verifyIndividuals():
    print('All specific components have a generic counterpart')