import yaml
import pprint

instrument_file='INSU-IPGP.instrumentation.yaml'
printInstrumentation=False

######################################
def printElements(insts,type):
    # prints elements, their descriptions and their serial numbers
    # insts = instrumentation tree
    # type = element type ('instrument','sensor', ...)
    for key,element in sorted(insts['models'][type].items()):
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
        if type in insts['individuals']:
            if key in insts['individuals'][type]:
                SNs= sorted(insts['individuals'][type][key])        
        output={' model':key,'description':description,'specified_serial_numbers':SNs}
        print(yaml.dump(output,width=70))
###############################################################################
def verifyIndividuals(insts):
    print('CROSS-CHECKING INDIVIDUALS AND MODELS')
    for element,models in sorted(insts['individuals'].items()):
        print('  {:>15}: '.format(element),end='')
        checksOut=True
        for model in models:
            if model not in insts['models'][element]:
                if checksOut:
                    print('')
                checksOut=False
                print(15*' ' +'"{}" is in individuals but not in models'.format(model))
        if checksOut :
            print("All individuals exist in models")            
###############################################################################
###############################################################################
# READ INSTRUMENTATION FILE
with open(instrument_file,'r') as f:
  insts=yaml.load(f)['instrumentation']

if printInstrumentation:
    print(yaml.dump(insts))

print('\nFILENAME: {}'.format(instrument_file))
print('FACILITY: {}'.format(insts['facility']['reference_name']))
print('REVISION: {} ({})'.format(insts['revision']['date'],insts['revision']['author']))
# PRINT INSTRUMENTS
print('\nINSTRUMENTS:')
printElements(insts,'instrument')

# PRINT SENSORS
print('\nSENSORS:')
printElements(insts,'sensor')

# VERIFY THAT INSTRUMENTS & SENSORS LISTED IN "individuals" EXIST in "models"
verifyIndividuals(insts)