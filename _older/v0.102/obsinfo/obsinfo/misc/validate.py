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
import yaml

################################################################################ 

def __determine_format(filename):
    """
    Determines the format of a file, assuming that the filename is "*.{FORMAT}
    """

    format = filename.split('.')[-1].upper()
    if format in ['JSON','YAML']:
        return format
    print('Unknown format: {format}')
    sys.exit(1)
        
################################################################################ 

def __determine_type(filename):
    """
    Determines the type of a file, assuming that the filename is "*.{TYPE}.{SOMETHING}
    """

    the_type = filename.split('.')[-2].lower()
    if the_type in ['campaign',
                  'network',
                  'instrumentation',
                  'response',
                  'instrument-components',
                  'filter']:
        return the_type
    print('Unknown type: {the_type}')
    sys.exit(1)
        
################################################################################ 
def validate(filename,format=None, type=None):
    """
    Validates a YAML or JSON file against schema
    type: "network", "instrumentation","response", "instrument-components","filter"
    format: "JSON" or "YAML"
    
    if type and/or format are not provided, tries to figure them out from the
    filename, which should be "*{TYPE}.{FORMAT}
    """

    if not format:
        format=__determine_format(filename)
    if not type:
        type = __determine_type(filename)

    if format=='YAML':
        root=yaml.load(filename)
    else:
        root=json.load(filename)
    
    SCHEMA_FILE=pkg_resources.resource_filename('obsinfo',f'data/schemas/{type}.schema.json')    
    schema=json.load(SCHEMA_FILE)
    validate(root,schema)
    return 