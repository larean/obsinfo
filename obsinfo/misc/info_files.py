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

# Local modules
from .yamlref import load as yamlref_load

root_symbol = "#"
VALID_FORMATS = ["JSON", "YAML"]
VALID_TYPES = [
    "campaign",
    "network",
    "instrumentation",
    "datalogger",
    "preamplifier",
    "sensor",
    "response",
    "filter",
]


def list_valid_types():
    """
    Returns a list of valid information file types
    """
    return VALID_TYPES


def get_information_file_type(filename):
    """
    Determines the type of a file, assuming that the filename is "*.{TYPE}.{SOMETHING}
    """

    the_type = filename.split(".")[-2].split("/")[-1].lower()
    if the_type in VALID_TYPES:
        return the_type
    print(f"Unknown type: {the_type}")
    sys.exit(1)


def info_dict_configure(in_dict, config=None, serial_number=None):
    """
    Update an information file dict by configuration and/or serial number
    
    Assumes that the input dict has one (or both) of the fields "configurations"
    and/or "serial_numbers" ("configurations" can also have "serial_numbers"
    inside.
    
    Removes the "configurations" and "serial_numbers" fields from the dict
    and updates its remaining fields with values provided in the following order:
        1) serial_numbers/{serial_number}
        2) configurations/{config}
        3) configurations/{config}/serial_numbers/{serial_number}
        
    :param in_dict: input dictionary
    :param config: the desired configuration
    :param serial_number: the desired serial number
    :type config, serial_number: str
    :returns out_dict: dictionary modified for specific configuration and SN
    """
    if "serial_numbers" in in_dict:
        if serial_number:
            if serial_number in in_dict["serial_numbers"]:
                in_dict = dict_update(in_dict, 
                                      in_dict["serial_numbers"][serial_number])
        del in_dict["serial_numbers"]
    if "configurations" in in_dict:
        if config:
            if config in in_dict["configurations"]:
                dict_config = in_dict["configurations"][config]
                in_dict = dict_update(in_dict, dict_config)
                if "serial_numbers" in dict_config:
                    if serial_number:
                        if serial_number in dict_config["serial_numbers"]:
                            in_dict = dict_update(in_dict,
                                dict_config["serial_numbers"][serial_number])
            else:
                raise NameError('Configuration "{}" absent from {}'.format(\
                                config, in_dict["configurations"].keys()))
        del in_dict["configurations"]
    elif config:
        print(f'Configuration "{config}" requested, but no configurations!')
        # pprint.pprint(in_dict)
    return in_dict


def dict_update(orig_dict, update_dict, allow_overwrite=True):
    """
    Update a dict with values in a second dict
    
    Assumes both dictionaries have the same structure, keeps values in
    orig_dict that are not provided in update_dict, and updates or adds
    values that are provided.  Drills recursively through dicts inside
    the orig_dict, only changing fields specified in update_dict
    
    :param orig_dict: The original dictionary
    :param update_dict: dictionary with fields to update_dict
    :param allow_overwrite: allow a field that was originally a dict to be 
                     overwritten by a field that is not a dict
    :type allow_overwrite: bool
    
    >>> dict_update({'a': 'j', 'b': {'c': 5, 'd': 6}}, {'b': {'d': 2, 'e': 3}})
    {'a': 'j', 'b': {'c': 5, 'd': 2, 'e': 3}}
    
    >>> dict_update({'a': 'j', 'b': {'c': 5, 'd': 6}}, {'a': 5, 'c': [1, 3]})
    {'a': 5, 'b': {'c': 5, 'd': 6}, 'c': [1, 3]}
    """
    for key,value in update_dict.items():
        if key not in orig_dict:
            orig_dict[key] = value
        else:
            if isinstance(orig_dict[key],dict):
                # if the original value is itself a dictionary
                if isinstance(value,dict):
                    # if replacement value is a dictionary, recurse
                    orig_dict[key] = dict_update(orig_dict[key], value)
                else:
                    # if replacement value is not a dictionary
                    if allow_overwrite:
                        # replace & warn
                        orig_dict[key] = value
                        warnings.warn(
                            f'input dict field "{key}" was a dict, ' +
                            'replaced by a non-dict')
                    else:
                        # reject & warn
                        warnings.warn(
                            f'replacement field "{key}" not inserted into ' +
                            'original because original was a dict and ' +
                            'replacement was not')
            else:
                orig_dict[key] = value
    return orig_dict
    
def validate(filename, format=None, type=None, verbose=False, quiet=False):
    """
    Validates a YAML or JSON file against schema
    type: "network", "datalogger", "preamplifier", "sensor", "response", "filter"
    format: "JSON" or "YAML"
    
    if type and/or format are not provided, tries to figure them out from the
    filename, which should be "*{TYPE}.{FORMAT}
    """

    if quiet:
        verbose = False

    if not type:
        type = get_information_file_type(filename)

    instance = read_json_yaml(filename, format=format)

    SCHEMA_FILE = pkg_resources.resource_filename(
        "obsinfo", f"data/schemas/{type}.schema.json"
    )
    base_path = os.path.dirname(SCHEMA_FILE)
    base_uri = f"file://{base_path}/"
    with open(SCHEMA_FILE, "r") as f:
        try:
            schema = jsonref.loads(f.read(), base_uri=base_uri, jsonschema=True)
        except json.decoder.JSONDecodeError as e:
            print(f"JSONDecodeError: Error loading JSON schema file: {SCHEMA_FILE}")
            print(str(e))
            return False
        except:
            print(f"Error loading JSON schema file: {SCHEMA_FILE}")
            print(sys.exc_info()[1])
            return False

    # Lazily report all errors in the instance
    # ASSUMES SCHEMA IS DRAFT-04 (I couldn't get it to work otherwise)
    try:
        if verbose:
            print(f"instance = {filename}")
        elif not quiet:
            print(f"instance = {filename} ... ", end="")

        if verbose:
            print(f"schema =   {os.path.basename(SCHEMA_FILE)}")
            print("\tTesting schema ...", end="")

        v = jsonschema.Draft4Validator(schema)

        if verbose:
            print("OK")
            print("\tTesting instance ...", end="")
        if not v.is_valid(instance):
            if quiet:
                # IF HAVE TO PRINT ERROR MESSAGE, PRINT INTRO TOO
                print(f"instance = {filename}")
            else:
                print("")
            for error in sorted(v.iter_errors(instance), key=str):
                print("\t\t", end="")
                for elem in error.path:
                    print(f"['{elem}']", end="")
                print(f": {error.message}")
            print("\tFAILED")
        else:
            if not quiet:
                print("OK")
    except jsonschema.ValidationError as e:
        if quiet:
            # IF HAVE TO PRINT ERROR MESSAGE, PRINT INTRO TOO
            print(f"instance = {filename}")
        else:
            print("")
        print("\t" + e.message)

    return True


def get_information_file_format(filename):
    """
    Determines if the information file is in JSON or YAML format
    
    Assumes that the filename is "*.{FORMAT}
    """

    format = filename.split(".")[-1].upper()
    if format in VALID_FORMATS:
        return format
    print("Unknown format: {format}")
    sys.exit(1)


def read_json_yaml(filename, format=None, debug=False):
    """ Reads a JSON or YAML file.  Does NOT use jsonReference """
    if not format:
        format = get_information_file_format(filename)

    with open(filename, "r") as f:
        if format == "YAML":
            try:
                element = yaml.safe_load(f)
            except:
                print(f"Error loading YAML file: {filename}")
                print(sys.exc_info()[1])
                return
        else:
            try:
                element = json.load(f)
            except JSONDecodeError as e:
                print(f"JSONDecodeError: Error loading JSON file: {filename}")
                print(str(e))
                return
            except:
                print(f"Error loading JSON file: {filename}")
                print(sys.exc_info()[1])
                return

    return element

def read_json_yaml_ref(filename, format=None, debug=False):
    """ Reads a JSON or YAML file using jsonReference """
    if not format:
        format = get_information_file_format(filename)

    with open(filename, "r") as f:
        return yamlref_load(f, base_uri='file:' + filename)


def load_information_file(
    reference, source_file=None, root_symbol=root_symbol, debug=False):
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
    filename = None
    if root_symbol in reference:
        if reference.count(root_symbol) > 1:
            raise RuntimeError(
                'More than one occurence of "{}" in file reference "{}"'.format(
                    root_symbol, reference
                )
            )
        if reference[0] == root_symbol:
            filename = ""
            internal_path = reference[1:]
        elif reference[-1] == root_symbol:
            filename = reference[0:-1]
            internal_path = ""
        else:
            A = reference.split(root_symbol)
            filename = A[0]
            internal_path = A[1]
    else:
        filename = reference
        internal_path = ""
    if debug:
        print(
            "LOAD_INFORMATION_FILE(): reference={}, source_file={}".format(
                reference, source_file
            )
        )
    if source_file:
        if os.path.isfile(source_file):
            current_path = os.path.dirname(source_file)
        else:
            current_path = source_file
        filename = os.path.join(current_path, filename)
    else:
        current_path = os.getcwd()
    if debug:
        print(
            "LOAD_INFORMATION_FILE(): filename={}, internal_path={}".format(
                filename, internal_path
            )
        )

    # MAKE SURE THAT IT CONFORMS TO SCHEMA
    validate(filename, quiet=True)

    # READ IN FILE
    element = read_json_yaml(filename)

    # BREAK OUT THE REQUESTED PART
    if internal_path:
        for key in internal_path.split("/"):
            if not key in element:
                raise RuntimeError(
                    "Internal path {} not found in file {}".format(
                        internal_path, filename
                    )
                )
            else:
                element = element[key]

    # RETURN RESULT
    if debug:
        print("LOAD_YAML(): ", type(element))
    return element, os.path.abspath(os.path.dirname(filename))


def _validate_script(argv=None):
    """
    Validate an obsinfo information file

    Validates a file named *.{TYPE}.json or *.{TYPE}.yaml against the 
    obsinfo schema.{TYPE}.json file.

    {TYPE} can be campaign, network, instrumentation, instrument_components or
    response
    """
    from argparse import ArgumentParser

    parser = ArgumentParser(prog="obsinfo-validate", description=__doc__)
    parser.add_argument("info_file", help="Information file")
    parser.add_argument(
        "-t",
        "--type",
        choices=VALID_TYPES,
        default=None,
        help="Forces information file type (overrides interpreting from filename)",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=VALID_FORMATS,
        default=None,
        help="Forces information file format (overrides interpreting from filename)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="increase output verbosiy"
    )
    args = parser.parse_args()

    validate(args.info_file, format=args.format, type=args.type, verbose=args.verbose)
