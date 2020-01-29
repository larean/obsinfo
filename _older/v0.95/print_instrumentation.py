#!/usr/bin/env python3
import yaml
import pprint

instrument_file='../information_files/FACILITY.instrumentation.yaml'
dumpFull=False

######################################
def printElements(insts):
    # prints elements, their descriptions and their serial numbers
    # insts = instrumentation tree
    for key,element in sorted(insts['models']['generic'].items()):
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
        if key in insts['models']['specific']:
            SNs= sorted(insts['models']['specific'][key])        
        output={' model':key,'description':description,'specified_serial_numbers':SNs}
        print(yaml.dump(output,width=70))
###############################################################################
def verifyIndividuals(insts):
    print('CROSS-CHECKING INDIVIDUALS AND MODELS')
    checksOut=True
    for model,SNs in sorted(insts['models']['specific'].items()):
        if model not in insts['models']['generic']:
            checksOut=False
            print(15*' ' +'"{}" model in "specific" has no generic counterpart'.format(model))
    if checksOut :
        print("All specific instruments have a generic counterpart")            
###############################################################################
###############################################################################
# READ INSTRUMENTATION FILE
with open(instrument_file,'r') as f:
  insts=yaml.load(f)['instrumentation']

if dumpFull:
    print(yaml.dump(insts))
    print('='*80 + '\n')

print('\nFILENAME: {}'.format(instrument_file))
print('FACILITY: {}'.format(insts['facility']['reference_name']))
print('REVISION: {} ({})'.format(insts['revision']['date'],insts['revision']['author']))
# PRINT INSTRUMENTS
print('\n' + 20*'=')
print('INSTRUMENTS:')
printElements(insts)

# VERIFY THAT INSTRUMENTS & SENSORS LISTED IN "individuals" EXIST in "models"
print('\n' + 20*'=')
verifyIndividuals(insts)