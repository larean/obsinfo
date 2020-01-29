import yaml
import pprint

network_file='EMSOMOMAR2016.network.yaml'
instrument_file='INSU-IPGP.instrumentation.yaml'

with open(network_file,'r') as f:
  stations=yaml.load(f)['Stations']
with open(instrument_file,'r') as f:
  instruments=yaml.load(f)['instruments']
  
pp=pprint.PrettyPrinter(width=131, compact=True)

for name,station in stations.items():
  # Find associated instrument
  inst_name=station['instrument']['name']
  inst_SN  =station['instrument']['serial_number']
  # Allow Serial Number to match wildcard
  if inst_SN not in instruments[inst_name]:
    inst_SN='??'
  # Put instrument values in station
  station['instrument']['parameters']=instruments[inst_name][inst_SN]
  # Print result
  print('='*80)
  print('Station {}:'.format(name))
  pp.pprint(station)
  print('')