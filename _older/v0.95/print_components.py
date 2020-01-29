#!/usr/bin/env python3
import yaml
import pprint

components_file='../information_files/FACILITY.instrumentation_components.yaml'
dumpFull=False

######################################
def printElements(insts,type):
    # prints elements, their descriptions and their serial numbers
    # insts = instrumentation tree
    # type = element type ('instrument','sensor', ...)
    for key,element in sorted(insts['models']['generic'][type].items()):
        #if 'equipment' in insts['models'][type][key]:
        if 'equipment' in element:
            if 'description' in element['equipment']:
                description = element['equipment']['description']
            else: 
                description = 'None'
        elif 'description' in element:
            description = element['description']
        else:
            description = 'None (not even an equipment field)'
        SNs=[]
        if type in insts['models']['specific']:
            if key in insts['models']['specific'][type]:
                SNs= sorted(insts['models']['specific'][type][key])        
        output={' model':key,'description':description,'specified_serial_numbers':SNs}
        print(yaml.dump(output,width=70))
###############################################################################
def verifyIndividuals(insts):
    print('CROSS-CHECKING INDIVIDUALS AND MODELS')
    for element,models in sorted(insts['models']['specific'].items()):
        print('  {:>15}: '.format(element),end='')
        checksOut=True
        for model in models:
            if model not in insts['models']['generic'][element]:
                if checksOut:
                    print('')
                checksOut=False
                print(15*' ' +'"{}" is in "specific" but not in "generic"'.format(model))
        if checksOut :
            print("All specific instruments have a generic counterpart")            
###############################################################################
###############################################################################
# READ COMPONENTS FILE
with open(components_file,'r') as f:
  components=yaml.load(f)['instrumentation_components']

if dumpFull:
    print(yaml.dump(insts))

print('\nFILENAME: {}'.format(components_file))
print('FACILITY: {}'.format(components['facility']['reference_name']))
print('REVISION: {} ({})'.format(components['revision']['date'],components['revision']['author']))
# PRINT INSTRUMENTS
print('\n===========')
print('DATALOGGERS:')
printElements(components,'datalogger')
print('\n===========')
print('PREAMPLIFIERS:')
printElements(components,'preamplifier')
print('\n===========')
print('SENSORS:')
printElements(components,'sensor')

# VERIFY THAT COMPONENTS LISTED IN "specific" EXIST in "generic"
print('\n===========')
verifyIndividuals(components)