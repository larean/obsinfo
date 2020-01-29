""" 
Print complete stations from information in network.yaml file

nomenclature:
    A "measurement instrument" is a means of recording one physical parameter,
        from sensor through dac
    An "instrument" is composed of one or more measurement instruments
    
    version 0.99
    
I need to modify the code so that it treats a $ref as a placeholder for the associated object
"""
# Standard library modules
import math as m
import json
import pprint
import os.path
import sys

# Non-standard modules
import yaml
import obspy.core.util.obspy_types as obspy_types
import obspy.core.inventory as inventory
import obspy.core.inventory.util as obspy_util
from obspy.core.utcdatetime import UTCDateTime

root_symbol='#'
VALID_FORMATS=['JSON','YAML']

################################################################################ 
# Miscellaneous Routines

def validate_YAML(yaml_file,schema_file,debug=False) :
    from jsonschema import validate   # Available from github
    # READ YAML file
    my_file=yaml.load(yaml_file)
    # READ YAML SCHEMA
    schema = json.load(schema_file)
    # VALIDATE AGAINST SCHEMA
    validate(my_file,schema)

def calc_norm_factor(zeros,poles,norm_freq,pz_type,debug=False) :
    """
    Calculate the normalization factor for give poles-zeros
    
    The norm factor A0 is calculated such that
                       sequence_product_over_n(s - zero_n)
            A0 * abs(------------------------------------------) === 1
                       sequence_product_over_m(s - pole_m)

    for s_f=i*2pi*f if the transfer function is in radians
            i*f     if the transfer funtion is in Hertz
    """
    
    A0 = 1. + 1j*0.
    if pz_type == 'LAPLACE (HERTZ)':
        s = 1j * norm_freq
    elif pz_type == 'LAPLACE (RADIANS/SECOND)':
        s = 1j * 2 * m.pi * norm_freq
    else:
        print("Don't know how to calculate normalization factor for z-transform poles and zeros!")
    for p in poles:
        A0 = A0 * (s - p)
    for z in zeros:
        A0 = A0 / (s - z)
        
    if debug:
        print('poles=',poles,', zeros=',zeros,'s={:g}, A0={:g}'.format(s,A0))
    
    A0=abs(A0)
    
    return A0
    
##################################################
def round_down_minute(date_time,min_offset):
    """
    Round down to nearest minute that is at least minimum_offset seconds earlier
    """
    dt=date_time-min_offset
    dt.second=0
    dt.microsecond=0
    return dt

##################################################
def round_up_minute(date_time,min_offset):
    """
    Round up to nearest minute that is at least minimum_offset seconds later
    """
    dt=date_time+60+min_offset
    dt.second=0
    dt.microsecond=0
    return dt

################################################################################ 

def get_information_file_format(filename):
    """
    Determines if the information file is in JSON or YAML format
    
    Assumes that the filename is "*.{FORMAT}
    """

    format = filename.split('.')[-1].upper()
    if format in VALID_FORMATS:
        return format
    print('Unknown format: {format}')
    sys.exit(1)
                
##################################################
def read_json_yaml(filename,format=None,debug=False):
    """ Reads a JSON or YAML file """
    if not format:
        format=get_information_file_format(filename)

    with open(filename,'r') as f:
        if format=='YAML':
            try:
                element=yaml.safe_load(f)
            except:
                print(f"Error loading JSON schema file: {SCHEMA_FILE}")
                print(sys.exc_info()[1])
                return
        else:
            try:
                element=json.load(filename)
            except JSONDecodeError as e:
                print(f"JSONDecodeError: Error loading JSON schema file: {SCHEMA_FILE}")
                print(str(e))
                return
            except:
                print(f"Error loading JSON schema file: {SCHEMA_FILE}")
                print(sys.exc_info()[1])
                return

    return element
        
##################################################
def load_information_file(reference,source_file=None,
                            root_symbol=root_symbol,debug=False):
    """
    Loads all (or part) of an information file
    
    input:
        reference (str): path to the element (filename &/or internal element path)
        source_file (str): full path of referring file (if any)
    output:
        element: the requested element
        base_file: the path of this file
        
    root_symbol is interpreted as the file's root level
     - If it is at the beginning of the reference, the element is searched for
        in source_file.
     - If it is in the middle of the reference, the element is searched for within the
        filename preceding it. 
     - If it is at the end (or absent), then the entire file is loaded 
     
    Based on JSON Pointers
       
    """
    
    # Figure out filename, absolute path and path inside file
    filename=None
    if root_symbol in reference:
        if reference.count(root_symbol) > 1:
            raise RuntimeError('More than one occurence of "{}" in file reference "{}"'.format(
                    root_symbol,reference))
        if reference[0] == root_symbol:
            filename=''
            internal_path=reference[1:]
        elif reference[-1] == root_symbol:
            filename=reference[0:-1]
            internal_path=''
        else:     
            A=reference.split(root_symbol)
            filename=A[0]
            internal_path=A[1]
    else:
        filename=reference
        internal_path=''            
    if debug:
        print('LOAD_INFORMATION_FILE(): reference={}, source_file={}'.format(reference, source_file))        
    if source_file:
        if os.path.isfile(source_file):
            current_path=os.path.dirname(source_file)
        else:
            current_path=source_file
        filename=os.path.join(current_path,filename)
    else:
        current_path=os.getcwd()
    if debug:
        print('LOAD_INFORMATION_FILE(): filename={}, internal_path={}'.format(filename,internal_path))

    # READ IN FILE
    element=read_json_yaml(filename)
        
    # BREAK OUT THE REQUESTED PART
    if internal_path:
        for key in internal_path.split('/') :
            if not key in element:
                raise RuntimeError("Internal path {} not found in file {}".format(\
                        internal_path,filename))
            else:
                element=element[key]

    # RETURN RESULT
    if debug:
        print("LOAD_YAML(): ",type(element))        
    return element, os.path.abspath(os.path.dirname(filename))   
   
##################################################
# def load_yaml(path,basepath=None,debug=False):
#     """
#     Loads a yaml element (or all elements) from referenced file
#     
#     root_symbol is interpreted as the file's root level
#      - If it is at the beginning of the reference, the element is searched for
#         in the current file.
#      - If it is in the middle, then the element is searched for within the
#         filename preceding it. 
#      - If it is at the end, then the entire yaml file is loaded 
#      
#     Inspired by JSON Pointers, but JSON Pointers use '#' as the root level
#     We can't (for now), because the DBIRD-based file names are full of '#'s!
#        
#     input:
#         path (str): path to the element (filename &/or internal path)
#         basepath: full path to current file
#                     This path (if any) will be prepended to the reference, as
#                     referenced YAML files are assumed to be in (or referenced to
#                     the same path as the referencing YAML files (like JSON Pointers) 
#                     If it includes a filename, the filename will be sliced off.
#     output:
#         element: the requested yaml element
#         basepath: the path of this file
#     """
#     print("load_yaml should be replaced by load_information_file")
#     filename=None
#     
#     if root_symbol in path:
#         if path.count(root_symbol) > 1:
#             raise RuntimeError('More than one occurence of "{}" in file reference "{}"'.format(
#                     root_symbol,path))
#         if path[0] == root_symbol:
#             filename=''
#             internal_path=path[1:]
#         elif path[-1] == root_symbol:
#             filename=path[0:-1]
#             internal_path=''
#         else:     
#             A=path.split(root_symbol)
#             filename=A[0]
#             internal_path=A[1]
#     else:
#         raise RuntimeError(": no internal path in '{}'".format(path))
#             
#     if debug:
#         print('LOAD_YAML(): path={}, basepath={}'.format(path, basepath))
#         
# #    if filename:
#     if basepath:
#         if os.path.isfile(basepath):
#             current_path=os.path.dirname(basepath)
#         else:
#             current_path=basepath
#         filename=os.path.join(current_path,filename)
#     else:
#         current_path=os.getcwd()
#     if debug:
#         print('LOAD_YAML(): filename={}, internal_path={}'.format(filename,internal_path))
#         
#     if not internal_path:
#         with open(filename,'r') as f:
#             element=yaml.safe_load(f)
#     else:
#         internal_paths=internal_path.split('/')    
#         with open(filename,'r') as f:
#             element=yaml.safe_load(f)[internal_paths[0]]
#     
#         if len(internal_paths) > 1:
#             for key in internal_paths[1:] :
#                 if not key in element:
#                     raise RuntimeError("Internal path {} not found in file {}".format(\
#                             internal_path,filename))
#                 else:
#                     element=element[key]
#     if debug:
#         print("LOAD_YAML(): ",type(element))        
#     return element, os.path.abspath(os.path.dirname(filename))   
#     
##################################################
def make_channel_code(channel_seed_codes,
                        given_band_code,instrument_code,orientation_code,
                        sample_rate,
                        debug=False):
    """
        Make a channel code from sensor, instrument and network information
        
        channel_seed_codes is a dictionary from the instrument_component file
        given_band, instrument, and orientation codes are from the network file
        sample_rate is from the network_file
    """
    band_base=channel_seed_codes['band_base']
    if not len(band_base) == 1:
        raise NameError('Band code is not a single letter: {}'.format(band_code))
    if not instrument_code == channel_seed_codes['instrument']:
        raise NameError('instrument and component instrument_codes do not '\
                        'match: {}!={}'.format(inst_code,
                                        channel_seed_codes['instrument']))
    if not orientation_code in [key for key in channel_seed_codes['orientation']]:
        raise NameError('instrument and component orientation_codes do not '\
                        'match: {}!={}'.format(orientation_code,
                                        channel_seed_codes['orientation']))
    if band_base in 'FCHBMLVURPTQ':
        if sample_rate >=1000:
            band_code='F'
        elif sample_rate >=250:
            band_code='C'
        elif sample_rate >=80:
            band_code='H'
        elif sample_rate >=10:
            band_code='B'
        elif sample_rate > 1 :
            band_code='M'
        elif sample_rate > .3 :
            band_code='L'
        elif sample_rate > .03 :
            band_code='V'
        elif sample_rate > .003 :
            band_code='U'
        elif sample_rate >= .0001 :
            band_code='R'
        elif sample_rate >= .00001 :
            band_code='P'
        elif sample_rate >= .000001 :
            band_code='T'
        else :
            band_code='Q'
    elif band_base in 'GDES':
        if sample_rate >=1000:
            band_code='G'
        elif sample_rate >=250:
            band_code='D'
        elif sample_rate >=80:
            band_code='E'
        elif sample_rate >=10:
            band_code='S'
        else:
            raise ValueError('Short period instrument has sample rate < 10 sps')
    else:
        raise NameError('Unknown band code: {}'.format(band_code))
    if band_code != given_band_code :
        raise NameError('Band code calculated from component and sample rate'\
            ' does not match that given in network file: {} versus {}'.format(
                                    band_code,given_band_code))
    if debug:
        print(band_code)
    channel_code =  band_code+instrument_code+orientation_code
    return channel_code

##################################################
def get_azimuth_dip(channel_seed_codes,orientation_code):
    " Returns azimuth and dip [value,error] pairs "
    if orientation_code in channel_seed_codes['orientation']:
        azimuth=    channel_seed_codes['orientation'][orientation_code]['azimuth.deg']
        azimuth =   [float(x) for x in azimuth]
        dip=        channel_seed_codes['orientation'][orientation_code]['dip.deg']
        dip =       [float(x) for x in dip]
    else:
        raise NameError('orientation code "{}" not found in '\
                'component seed_codes.orientation'.format(orientation_code)) 
    return azimuth,dip