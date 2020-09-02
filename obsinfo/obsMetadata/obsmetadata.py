""" 
obsinfo information file routines, contained in superclass OBSMetadata for generality
"""
# Standard library modules
import json
import pprint
from pathlib import Path, PurePath 
import sys
import pkg_resources

# Non-standard modules
import jsonschema
import jsonref
import yaml

# Local modules
from ..misc import yamlref
"""from ..info_dict import InfoDict"""

root_symbol = "#"
VALID_FORMATS = ["JSON", "YAML"]
VALID_TYPES = [
    "campaign",
    "network",
    "station",
    "instrumentation",
    "datalogger",
    "preamplifier",
    "sensor",
    "response",
    "stage",
    "filter",
]


class ObsMetadata(object):
    def list_valid_types():
        """
        Returns a list of valid information file types
        """
        return VALID_TYPES


    def get_information_file_type(filename):
        """
        Determines the type of a file, assuming that the filename is "*.{TYPE}.{SOMETHING}
        """
    
        #the_type = filename.split(".")[-2].split("/")[-1].lower()
        stem_file = PurePath(filename).stem
        the_type = (PurePath(stem_file).suffix)[1:]
        
        if the_type in VALID_TYPES:
            return the_type
        print(f"Unknown type: {the_type}")
        sys.exit(1)
    
    
    def validate(filename, format=None, type=None, verbose=False,
                 schema_file=None, quiet=False):
        """
        Validates a YAML or JSON file against schema
        type: "network", "datalogger", "preamplifier", "sensor", "response", "filter"
        format: "JSON" or "YAML"
        
        if type and/or format are not provided, tries to figure them out from the
        filename, which should be "*{TYPE}.{FORMAT}
        """
    
        if quiet:
            verbose = False
    
        if not type and not schema_file:
            type = ObsMetadata.get_information_file_type(filename)
    
        if verbose:
            print(f"instance = {filename}")
        elif not quiet:
            print(f"instance = {filename}")
             # {PurePath("").name(filename)} ... ")
    
        instance = ObsMetadata.read_json_yaml_ref(filename, format=format)
        # instance = read_json_yaml(filename, format=format)
    
        if not schema_file:
            base_file = type + ".schema.json"
            #schema_file = pkg_resources.resource_filename(
            #    "obsinfo", PurePath(home).joinpath("data", "schemas", base_file)
            #)
            #base_path = schema_file.parent
            home = Path("").resolve()
            schema_file = PurePath(home).joinpath("data", "schemas", base_file)
        base_uri = base_file.as_uri()
        #base_uri = f"file:{base_path}/"
        # base_uri = f"file://{base_path}/"
        # print(base_uri)
        with open(schema_file, "r") as f:
            try:
                schema = yamlref.loads(f.read(), base_uri=base_uri, jsonschema=True)
                # schema = jsonref.loads(f.read(), base_uri=base_uri, jsonschema=True)
            except json.decoder.JSONDecodeError as e:
                print(f"JSONDecodeError: Error loading JSON schema file: {schema_file}")
                print(str(e))
                return False
            except:
                print(f"Error loading JSON schema file: {schema_file}")
                print(sys.exc_info()[1])
                return False
    
        # Lazily report all errors in the instance
        # ASSUMES SCHEMA IS DRAFT-04 (I couldn't get it to work otherwise)
        try:
            # if verbose:
            #     print(f"instance = {filename}")
            # elif not quiet:
            #     print(f"instance = {os.path.basename(filename)} ... ", end="")
    
            if verbose:
                print(f"schema =   {PurePath.name(schema_file)}")
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
                return False
            else:
                if not quiet:
                    print("OK")
                return True
        except jsonschema.ValidationError as e:
            if quiet:
                # IF HAVE TO PRINT ERROR MESSAGE, PRINT INTRO TOO
                print(f"instance = {filename}")
            else:
                print("")
            print("\t" + e.message)
            return False
    
    
    def get_information_file_format(filename):
        """
        Determines if the information file is in JSON or YAML format
        
        Assumes that the filename is "*.{FORMAT}
        """
    
        suffix = PurePath(filename).suffix
        format = suffix[1:].upper()
        if format in VALID_FORMATS:
            return format
        print("Unknown format: {format}")
        sys.exit(1)
    
    
    def read_json_yaml(filename, format=None, debug=False):
        """ Reads a JSON or YAML file.  Does NOT use jsonReference """
        if not format:
            format = ObsMetadata.get_information_file_format(filename)
    
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
            format = ObsMetadata.get_information_file_format(filename)
    
        home = Path("")
        base_path = PurePath.joinpath(home.resolve(),filename)
        base_uri = base_path.as_uri()
        #base_uri = f"file:{base_path}/"
        # print(f'read_json_yaml_ref: base_uri={base_uri}')
        with open(filename, "r") as f:
            return yamlref.load(f, base_uri=base_uri)
    
    def read_info_file(filename, format=None):
        """
        Reads an information file
        """
        """"A = InfoDict(_read_json_yaml_ref(filename, format))
        A.propagate()  # Makes all subdicts InfoDicts"""
        A = ObsMetadata.read_json_yaml_ref(filename, format)
        return A
                
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
            "-t", "--type", choices=VALID_TYPES, default=None,
            help="Forces information file type (overrides interpreting from filename)",
        )
        parser.add_argument(
            "-f", "--format", choices=VALID_FORMATS, default=None,
            help="Forces information file format (overrides interpreting from filename)",
        )
        parser.add_argument(
            "-s", "--schema", default=None,
            help="Schema file (overrides interpreting from filename)",
        )
        parser.add_argument(
            "-v", "--verbose", action="store_true", help="increase output verbosity"
        )
        args = parser.parse_args()
    
        validate(args.info_file, format=args.format, type=args.type,
                schema_file=args.schema, verbose=args.verbose)
        
    def to_obspy(self):
        return(self)
    