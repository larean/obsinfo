""" 
Validate information files

"""
# Standard library modules
import json
import pprint
import os.path
import sys
import pkg_resources

# Non-standard modules
import jsonschema
import jsonref
import yaml

# obsinfo modules
from .misc import get_information_file_format
from ..network import network
from ..instrumentation import instrumentation
from ..instrument_components import instrument_components

VALID_TYPES=['campaign','network','instrumentation','instrument-components',
             'response','filter']
################################################################################ 

def list_valid_types():
    """
    Returns a list of valid information file types
    """
    return VALID_TYPES

################################################################################ 

def get_information_file_type(filename):
    """
    Determines the type of a file, assuming that the filename is "*.{TYPE}.{SOMETHING}
    """

    the_type = filename.split('.')[-2].split('/')[-1].lower()
    if the_type in VALID_TYPES:
        return the_type
    print(f'Unknown type: {the_type}')
    sys.exit(1)
################################################################################ 
def validate(filename,format=None, type=None,verbose=False):
    """
    Validates a YAML or JSON file against schema
    type: "network", "instrumentation","response", "instrument-components","filter"
    format: "JSON" or "YAML"
    
    if type and/or format are not provided, tries to figure them out from the
    filename, which should be "*{TYPE}.{FORMAT}
    """

    if not format:
        format=get_information_file_format(filename)
    if not type:
        type = get_information_file_type(filename)

    with open(filename,'r') as f:
        if format=='YAML':
            instance=yaml.safe_load(f)
        else:
            instance=json.load(f)
    
    SCHEMA_FILE=pkg_resources.resource_filename('obsinfo',f'../data/schemas/{type}.schema.json')    
    base_path=os.path.dirname(SCHEMA_FILE)
    base_uri=f'file://{base_path}/' 
    with open(SCHEMA_FILE,'r') as f:
        schema=jsonref.loads(f.read(),base_uri=base_uri,jsonschema=True)
        
        
        
    # Lazily report all errors in the instance
    # ASSUMES SCHEMA IS DRAFT-04 (I couldn't get it to work otherwise)
    try:
        print(f'instance = {filename}',end='')
        if verbose:
            print('')
        else:
            print('..',end='')
        if verbose:
            print(f'schema =   {os.path.basename(SCHEMA_FILE)}')
            print('\tTesting schema ...',end='')
        v = jsonschema.Draft4Validator(schema)
        if verbose:
            print('OK')
            print( '\tTesting instance...',end='')
        if not v.is_valid(instance):
            print('')
            for error in sorted(v.iter_errors(instance), key=str):
                print('\t',end='')
                for elem in error.path:
                    print(f"['{elem}']",end='')
                print(f': {error.message}')
        else:
            print('OK')
    except jsonschema.ValidationError as e:
        print('')
        print('\t'+e.message)

    return 
    
################################################################################ 
def print_summary(filename,format=None, type=None,verbose=False):
    """
    Print a summary of an information file
    type: "network", "instrumentation","response", "instrument-components","filter"
    format: "JSON" or "YAML"
    
    if type and/or format are not provided, figures them out from the
    filename, which should be "*{TYPE}.{FORMAT}
    """

    if not format:
        format=get_information_file_format(filename)
    if not type:
        type = get_information_file_type(filename)

    with open(filename,'r') as f:
        if format=='YAML':
            instance=yaml.safe_load(f)
        else:
            instance=json.load(f)
    
    print(f'\nFILENAME: {filename}')
    if type=='network':
        instance=network(filename)
        _print_summary_network(instance,filename)
    elif type=='instrumentation':
        instance=instrumentation(filename)
        _print_summary_instrumentation(instance)
    elif type=='instrument-components':
        instance=instrument_components(filename)
        _print_summary_instrument_components(instance)
    else:
        _print_summary_other(instance[type])

################################################################################ 
def _print_summary_network(network,network_file):
    """ Print summary information about a network """
    print(network)        
    for name,station in network.stations.items():
        print('='*80)
        print(f'Station {name}:')
        print(station)
        
################################################################################ 
def _print_summary_instrumentation(instrumentation):
    """ Print summary information about an instrumentation file """
    print(f"FACILITY: {instrumentation.facility['reference_name']}")
    print(f'REVISION: {instrumentation.revision}')
    # PRINT INSTRUMENTS
    print('\n' + 20*'=')
    print('INSTRUMENTS:')
    instrumentation.print_elements()

    # VERIFY THAT INSTRUMENTS & SENSORS LISTED IN "individuals" EXIST in "models"
    print(20*'=')
    if instrumentation.verify_individuals():
        print('All instruments have a generic counterpart')

    # VERIFY THAT REFERRED TO FILES EXIST
    print('\n' + 20*'=')
    print('Checking dependencies on instrument_components_file')
    file_exists,n_components,n_found,n_cites = instrumentation.check_dependencies(print_names=True)
    if not file_exists :
        print(f'Instrument_Components file not found: {instrumentation.components_file}')
    elif n_components==n_found :
        print('Found all {:d} specied functional components ({:d} total cites)'\
                ''.format(n_components,n_cites))
    else:
        print('MISSING {:d} of {:d} specied functional components '\
                ''.format(n_components-n_found,n_components))
                
################################################################################ 
def _print_summary_instrument_components(instance):
    """ Print summary information about an instrument_components file """
    print(f'FORMAT_VERSION: {instance.format_version}')
    print(f'REVISION: {instance.revision}')
    # PRINT INSTRUMENTS
    print(10*'=')
    print('DATALOGGERS:')
    instance.print_elements('datalogger')
    print(10*'=')
    print('PREAMPLIFIERS:')
    instance.print_elements('preamplifier')
    print(10*'=')
    print('SENSORS:')
    instance.print_elements('sensor')

    # VERIFY THAT COMPONENTS LISTED IN "specific" EXIST in "generic"
    print(10*'=')
    if instance.verify_individuals():
        print('All specific components have a generic counterpart')

    # VERIFY THAT REFERRED TO FILES EXIST
    print(10*'=')
    n_files, n_found, n_cites = instance.verify_source_files(print_names=True)
    if n_files==n_found:
        print('Found all {:d} specified source files ({:d} total citations)'\
                        ''.format(n_files,n_cites))
    else:
        print('MISSING {:d} of {:d} specified source files'\
                        ''.format(n_files-n_found,n_files))  
                              
################################################################################ 
def _print_summary_other(instance):
    """ Print summary information about a generic information file """
    pp = pprint.PrettyPrinter(indent=1,depth=2,compact=True)
    pp.pprint(instance)
