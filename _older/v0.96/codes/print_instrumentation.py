#!/usr/bin/env python3
import yaml
import pprint
from obs_info import OBS_Instrumentation

instrument_file='../information_files/FACILITY.instrumentation.yaml'

instrumentation=OBS_Instrumentation(instrument_file)

print('\nFILENAME: {}'.format(instrument_file))
print('FACILITY: {}'.format(instrumentation.facility['reference_name']))
print('REVISION: {} ({})'.format(instrumentation.revision['date'],
                                instrumentation.revision['author']))
# PRINT INSTRUMENTS
print('\n' + 20*'=')
print('INSTRUMENTS:')
instrumentation.printElements()

# VERIFY THAT INSTRUMENTS & SENSORS LISTED IN "individuals" EXIST in "models"
print('\n' + 20*'=')
if instrumentation.verifyIndividuals():
    print('All instruments have a generic counterpart')

# VERIFY THAT ANY "DOWNSTREAM" dependencies work (filenames, components called...)
# if instrumentation.checkDependencies():
#     print('Filename dependencies check out')