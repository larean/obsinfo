"""
Instrument_components class

nomenclature:
    A "measurement instrument" is a means of recording one physical parameter,
        from sensor through dac
    An "instrument" is composed of one or more measurement instruments
"""
# Standard library modules
import math as m
import os.path
import sys

# Non-standard modules
import yaml
import obspy.core.util.obspy_types as obspy_types
import obspy.core.inventory as inventory
import obspy.core.inventory.util as obspy_util
from obspy.core.utcdatetime import UTCDateTime

# obsinfo modules
from ..misc.info_files import load_information_file, root_symbol
from ..misc.FDSN import equipment_type as FDSN_equipment_type


################################################################################
class Instrument_components:
    """ Everything in a instrument_components information file"""

    def __init__(self, filename, referring_file=None, debug=False):
        """ Read instrument_components information file"""
        temp, basepath = load_information_file(filename, referring_file)
        if debug:
            print(basepath)
        self.basepath = basepath
        self.filename = filename
        self.revision = temp["revision"]
        self.format_version = temp["format_version"]
        # self.facility_reference_name=temp['facility_reference_name']
        self.instrument_blocks = temp["instrument_components"]["instrument_blocks"]

    def __repr__(self):
        return "<Instrument_components: {}>".format(self.filename)

    def __load_specific_component(self, component, serial_number, debug=False):
        if not "specific" in self.instrument_blocks[component.type]:
            return component
        elif not serial_number in self.instrument_blocks[component.type]["specific"]:
            return component
        specific = self.instrument_blocks[component.type]["specific"][serial_number]
        if debug:
            print("[{}][{}]=".format(component.type, serial_number))
            print("specific=", specific)
        if "response" in specific:
            for key in specific["response"]:
                component["response"][key] = specific["response"][key]
        if "equipment" in specific:
            component.equipment.merge(FDSN_equipment_type(specific["equipment"]))
        return component

    def __check_response_files(
        self, files_dict, component_dict, resp_dir, print_names, debug=False
    ):
        if debug:
            print(files_dict)
            print(component_dict)
        if "generic" in component_dict:
            for component in component_dict["generic"].values():
                files_dict = self.__test_response_files(
                    files_dict, component, resp_dir, print_names
                )
        else:
            print('No generic objects for component type "{}"'.format(block_type))
        if "specific" in component_dict:
            for model in component_dict["specific"].values():
                for component in model.values():
                    files_dict = self.__test_response_files(
                        files_dict, component, resp_dir, print_names
                    )
        return files_dict

    def __test_response_files(
        self, files_dict, component, resp_dir, print_names, debug=False
    ):
        #         if debug:
        #             print('')
        #             print(component)
        if "response_stages" in component:
            for file_ref in component["response_stages"]:
                if debug:
                    print(file_ref)
                filename = file_ref["$ref"]
                if filename in files_dict:
                    files_dict[filename]["n_cites"] = (
                        files_dict[filename]["n_cites"] + 1
                    )
                else:
                    files_dict[filename] = dict(n_cites=1, exists=None)
                    if not os.path.isfile(os.path.join(resp_dir, filename)):
                        files_dict[filename]["exists"] = False
                    else:
                        files_dict[filename]["exists"] = True
        return files_dict

    def get_component(
        self, block_type, reference_code, serial_number=None, get_responses=True
    ):
        """ get one instrument_component
    
            inputs:
                block_type: 'datalogger','preamplifier' or 'sensor'
                reference_code:
                serial_number: optional
                get_responses: return with responses filled in [True]
            output:
                instrument_component: Instrument_component object 
                                            OR 
                                      list of possible component names
        """
        if reference_code not in self.instrument_blocks[block_type]["generic"]:
            code_list = []
            for generic_code in self.instrument_blocks[block_type]["generic"]:
                if (reference_code + "_") in generic_code:
                    code_list.append(generic_code)
            if not code_list:
                code_list = None
            return code_list
        # LOAD GENERIC COMPONENT
        sample_rate = self.instrument_blocks[block_type]["generic"][reference_code]["sample_rate"] if "sample_rate" in self.instrument_blocks[block_type]["generic"][reference_code] else None
        component = Instrument_component(
            self.instrument_blocks[block_type]["generic"][reference_code], self.basepath, sample_rate=sample_rate
        )

        component.reference_code = reference_code
        component.type = block_type
        if serial_number:
            component.equipment.serial_number = serial_number
            # LOAD SPECIFIC COMPONENT, IF IT EXISTS
            component = self.__load_specific_component(component, serial_number)
        return component

    def print_elements(self, elem_type):
        """ prints one type of InstrumentComponent (descriptions and  serial numbers)
        type = ('sensor', "preamplifier' or 'datalogger')
        """
        for key, element in sorted(
            self.instrument_blocks[elem_type]["generic"].items()
        ):
            description = None
            if "equipment" in element:
                equipment = element["equipment"]
                if type(equipment) == dict:
                    equipment = FDSN_equipment_type(equipment)
                description = equipment.description
            if not description:
                if "description" in element:
                    description = element["description"]
                else:
                    description = "None provided"
            SNs = []
            if "specific" in self.instrument_blocks[elem_type]:
                if key in self.instrument_blocks[elem_type]["specific"]:
                    SNs = sorted(self.instrument_blocks[elem_type]["specific"][key])
            # output={'    model':key,'description':description,'specified_serial_numbers':SNs}
            # print(yaml.dump(output,indent=10,width=80))
            print(f'{key}: description="{description}", specified_SNs={SNs}')

    def verify_individuals(self):
        """ Verify that all "specific" instruments have a generic counterpart
        
            returns true if so, false + error message if not
        """
        checksOut = True
        for block_type in sorted(self.instrument_blocks.keys()):
            subcomponents = self.instrument_blocks[block_type]
            if "specific" in subcomponents:
                no_error_for_type = True
                for model in subcomponents["specific"].keys():
                    if model not in subcomponents["generic"]:
                        if no_error_for_type:
                            print("  {:>15}: ".format(block_type), end="")
                            no_error_for_type = False
                        checksOut = False
                        print(
                            15 * " "
                            + '"{}" is in "specific" but not in \
                                    "generic"'.format(
                                model
                            )
                        )
        return checksOut

    def verify_source_files(self, print_names=False, debug=False):
        """ Verify that all response files exist
        
            returns true if so, false + error message if not
            also returns number of files listed
        """
        print("Searching for response files")
        files_dict = dict()
        for block_type in self.instrument_blocks:
            files_dict = self.__check_response_files(
                files_dict,
                self.instrument_blocks[block_type],
                self.basepath,
                print_names,
            )
        if debug:
            print(files_dict)
        total_files = 0
        total_found = 0
        total_cites = 0
        for filename, value in sorted(files_dict.items()):
            total_files = total_files + 1
            n_cites = value["n_cites"]
            total_cites = total_cites + n_cites
            if value["exists"]:
                total_found = total_found + 1
                if print_names:
                    if n_cites == 1:
                        print("        FOUND ( 1 cite ): {}".format(filename))
                    else:
                        print(
                            "        FOUND ({:2d} cites): {}".format(n_cites, filename)
                        )
            else:
                if n_cites == 1:
                    print("    NOT FOUND ( 1 cite ): {}".format(filename))
                else:
                    print("    NOT FOUND ({:2d} cites): {}".format(n_cites, filename))
        return total_files, total_found, total_cites

class Instrument_component:
    """ One obsinfo instrument component 
    
        Inputs:
            component_dict: generic component dictionary from 
                            instrument_components information file
            
    """

    def __init__(
        self,
        component_dict,
        basepath,
        component_type=None,
        reference_code=None,
        sample_rate = None,
        debug=False,
    ):
        """ Inputs:
                component_dict: generic component dictionary from 
                                instrument_components information file
                basepath: full path of directory containing Instrument_Components file
                component_type = component type ('datalogger','preamplifier' or 'sensor')
                reference_code = component reference code
            
        """
        if debug:
            print(basepath)
        self.basepath = basepath
        self.equipment = FDSN_equipment_type(component_dict["equipment"])
        if "seed_codes" in component_dict:
            self.seed_codes = component_dict["seed_codes"]
        self.response_superstages = component_dict["response_stages"]
        self.type = component_type
        self.reference_code = reference_code
        self.sample_rate = sample_rate 
        self.response = None

    def __repr__(self):
        return "<OBS_Instrument_Component: {}>".format(self.reference_code)

    def fill_responses(self, debug=False):
        """ Fill in instrument responses from references"""
        if debug:
            print("self.response_superstages=", end="")
            print(yaml.dump(self.response_superstages))
        self.__read_response_yamls()
        if debug:
            print("self.response=", end="")
            print(yaml.dump(self.response))

    def __read_response_yamls(self, debug=False):
        """ READ INSTRUMENT RESPONSES FROM RESPONSE_YAML FILES
    
        Input:
            directory: base directory of response_yaml files
        """
        self.response = {'decimation_info':None,'stages':list()}
        if debug:
            print(
                "{:d} superstage files for the component".format(
                    len(self.response_superstages)
                )
            )
        for superstage in self.response_superstages:
            superstage_file = superstage["$ref"]
            if debug:
                print("Reading superstage file {}".format(superstage_file))
            response, temp = load_information_file(
                superstage_file + root_symbol + "response", self.basepath
            )
            self.response['decimation_info'] = response['decimation_info'] if 'decimation_info' in response else None
            for stage in response['stages']:
                # IF STAGE FILTER IS A "$ref", READ AND INJECT THE REFERRED FILE
                if "$ref" in stage["filter"]:
                    # READ REFERRED FILE
                    filter_ref = os.path.join(
                        os.path.split(superstage_file)[0], stage["filter"]["$ref"]
                    )
                    if debug:
                        print("filter file ref:", filter_ref)
                    filter, temp = load_information_file(filter_ref, self.basepath)
                    # MAKE SURE IT'S THE SAME TYPE, IF SO INJECT
                    stage["filter"] = filter
                self.response['stages'].append(stage)
            if debug:
                print("{:d} stages read".format(len(stages)))
        if debug:
            print("{:d} total stages in component".format(len(self.response)))
            print(yaml.dump(self.response))

    def __read_response_yamls_old(self, debug=False):
        """ READ INSTRUMENT RESPONSES FROM RESPONSE_YAML FILES
    
        Input:
            directory: base directory of response_yaml files
        """
        self.response = list()
        if debug:
            print(
                "{:d} superstage files for the component".format(
                    len(self.response_superstages)
                )
            )
        for superstage in self.response_superstages:
            superstage_file = superstage["$ref"]
            if debug:
                print("Reading superstage file {}".format(superstage_file))
            stages, temp = load_information_file(
                superstage_file + root_symbol + "response/stages", self.basepath
            )
            for stage in stages:
                # IF STAGE FILTER IS A "$ref", READ AND INJECT THE REFERRED FILE
                if "$ref" in stage["filter"]:
                    # READ REFERRED FILE
                    filter_ref = os.path.join(
                        os.path.split(superstage_file)[0], stage["filter"]["$ref"]
                    )
                    if debug:
                        print("filter file ref:", filter_ref)
                    filter, temp = load_information_file(filter_ref, self.basepath)
                    # MAKE SURE IT'S THE SAME TYPE, IF SO INJECT
                    stage["filter"] = filter
                self.response.append(stage)
            if debug:
                print("{:d} stages read".format(len(stages)))
        if debug:
            print("{:d} total stages in component".format(len(self.response)))
            print(yaml.dump(self.response))
