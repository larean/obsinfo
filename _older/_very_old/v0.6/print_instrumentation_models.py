import yaml

instrument_file='INSU-IPGP.instrumentation.yaml'

with open(instrument_file,'r') as f:
  insts=yaml.load(f)['instrumentation']

# import pprint
# pp=pprint.PrettyPrinter(width=131, compact=True)
# pp.pprint(insts)

print('Facility: {}'.format(insts['facility']['short_name']))
print('version: {}'.format(insts['version']))
print('models:')
models=insts['models']
for model in sorted(models):
    print('  - "{}"'.format(model))
    print('     SNs '.format(model),end='')
    for sn in sorted(models[model]):
        print('"'+sn+'"', end=', ')
    print('')
