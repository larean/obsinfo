"""
Instrument_components class

nomenclature:
    A "measurement instrument" is a means of recording one physical parameter,
        from sensor through dac
    An "instrument" is composed of one or more measurement instruments
"""
# Standard library modules
# import math as m
import os.path
# import sys

# Non-standard modules
import yaml
# import obspy.core.util.obspy_types as obspy_types
# import obspy.core.inventory as inventory
# import obspy.core.inventory.util as obspy_util
# from obspy.core.utcdatetime import UTCDateTime

# obsinfo modules
from ..misc.info_files import load_information_file, root_symbol
from ..misc.FDSN import equipment_type as FDSN_equipment_type


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
        self.instrument_blocks = \
            temp["instrument_components"]["instrument_blocks"]

    def __repr__(self):
        return "<Instrument_components: {}>".format(self.filename)

    def __load_specific_component(self, component, serial_number,
                                  debug=False):
        component_tree = self.instrument_blocks[component.type]
        if "specific" not in component_tree:
            return component
        elif serial_number not in component_tree["specific"]:
            return component
        specific = component_tree["specific"][serial_number]
        if debug:
            print("[{}][{}]=".format(component.type, serial_number))
            print("specific=", specific)
        if "response" in specific:
            for key in specific["response"]:
                component["response"][key] = specific["response"][key]
        if "equipment" in specific:
            component.equipment.merge(FDSN_equipment_type(specific["equipment"]))
        return default_component

    def get_component(self, block_type, ref_code, config=None,
                      serial_number=None, get_responses=True):
        """
        Return one instrument_component
    
        :param block_type: 'datalogger','preamplifier' or 'sensor'
        :param ref_code: component reference code_list
        :param config: component configuration
        :param serial_number: componet serial number
        :param get_responses: return with responses filled in
        :type get_responses: bool
        
        :returns: Instrument_component object
        """
        components=self.instrument_blocks[block_type]
        if ref_code not in components:
            return None
            
        # LOAD BASE COMPONENT
        sample_rate = components[ref_code].get("sample_rate",None)
        component = Instrument_component(components[ref_code], self.basepath,
                                         sample_rate=sample_rate)

        component.ref_code = ref_code
        component.type = block_type
        if serial_number:
            component.equipment.serial_number = serial_number
            # LOAD SPECIFIC COMPONENT, IF IT EXISTS
            component = self.__load_specific_component(component, serial_number)
        return component

    def print_elements(self, elem_type):
        """
        Print summary of one Instrument_Component block
        
        :param elem_type: type of block to print('sensor', "preamplifier' or
                          'datalogger')
        """
        for key, element in \
                sorted(self.instrument_blocks[elem_type].items()):
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
            configs=[]
            if "serial_numbers" in element:
                SNs.extend(sorted(element["serial_numbers"]))
            if "configurations" in element:
                for config_name, config in element["configurations"].items():
                    configs.append(config_name)
                    if "serial_numbers" in config:
                        SNs.extend(sorted(config["serial_numbers"]))
            print(f'{key}: {description}')
            print('  ' + yaml.dump({"configurations": configs},
                                   indent=4),end='')
            print('  ' + yaml.dump({"specified SNs": sorted(set(SNs))},
                                   indent=4),end='')
 
# 
#     def verify_individuals(self):
#         """ Verify that all "specific" instruments have a generic counterpart
#         
#             returns true if so, false + error message if not
#         """
#         checksOut = True
#         for block_type in sorted(self.instrument_blocks.keys()):
#             subcomponents = self.instrument_blocks[block_type]
#             if "specific" in subcomponents:
#                 no_error_for_type = True
#                 for model in subcomponents["specific"].keys():
#                     if model not in subcomponents["generic"]:
#                         if no_error_for_type:
#                             print("  {:>15}: ".format(block_type), end="")
#                             no_error_for_type = False
#                         checksOut = False
#                         print(
#                             15 * " "
#                             + '"{}" is in "specific" but not in \
#                                     "generic"'.format(
#                                 model
#                             )
#                         )
#         return checksOut

    def verify_source_files(self, print_names=False, debug=False):
        """
        Verify that cited response files exist and count citations
        
        :returns: total_files, total_found, total_cites
        :rtype: tuple
        """
        print("Searching for response files")
        files_dict = dict()
        for block in self.instrument_blocks.values():
            files_dict = self._check_response_files(files_dict, block,
                                                    self.basepath,
                                                    print_names)
        if debug:
            print(files_dict)
        total_files, total_found, total_cites = 0, 0, 0
        for filename, value in sorted(files_dict.items()):
            total_files = total_files + 1
            n_cites = value["n_cites"]
            total_cites = total_cites + n_cites
            if value["exists"]:
                total_found = total_found + 1
            if print_names:
                if value["exists"]:
                    print("        FOUND ",end='')
                else:
                    print("    NOT FOUND ",end='')
                print(f"({n_cites:2d} cites): {filename}")
        return total_files, total_found, total_cites

    def _check_response_files(self, files_dict, component_dict,
                               resp_dir, print_names):
        """
        Extracts response filenames from each component of an instrument_block
        
        :param files_dict: filenames with subfields 'n_cites' and 'exists'
        :type  files_dict: dict
        :param component_dict: components in an instrument block
        :type component_dict: dict
        """
        for component in component_dict.values():
            files_dict = self._test_response_files(files_dict, component,
                                                   resp_dir)
            if "configurations" in component:
                files_dict = self._test_response_files(files_dict,
                    component['configurations'], resp_dir, print_names)
                if "serial_numbers" in component['configurations']:
                    files_dict = self._test_response_files(files_dict,
                        component['configurations']['serial_numbers'],
                        resp_dir, print_names)
            if "serial_numbers" in component:
                files_dict = self._test_response_files(files_dict,
                    component['serial_numbers'],
                    resp_dir, print_names)
        return files_dict

    def _test_response_files(self, files_dict, component,
                             resp_dir, debug=False):
        """
        Extracts filenames from response_stages of current component
        
        Adds each filename to a dictionary of filenames.  Returns the dict 
        """
        if "response_stages" in component:
            for file_ref in component["response_stages"]:
                if debug:
                    print(file_ref)
                filename = file_ref["$ref"]
                if filename in files_dict:
                    files_dict[filename]["n_cites"] += 1
                else:
                    files_dict[filename] = dict(n_cites=1,
                        exists=os.path.isfile(os.path.join(resp_dir,
                                                           filename)))
        return files_dict


class Instrument_component:
    """ One obsinfo instrument component 
    
        Inputs:
            component_dict: generic component dictionary from 
                            instrument_components information file
            
    """

    def __init__(self, component_dict, basepath, component_type=None,
                 ref_code=None, sample_rate=None, debug=False):
        """ 
        Reads in an instrument_components file_ref
        
        :param component_dict: generic component dictionary from 
                               instrument_components information file
        :param basepath: full path of directory containing
                         instrument_components file
        :param component_type: component type ('datalogger','preamplifier'
                               or 'sensor')
        :param ref_code: component ref code
        """
        if debug:
            print(basepath)
        self.basepath = basepath
        self.equipment = FDSN_equipment_type(component_dict["equipment"])
        if "seed_codes" in component_dict:
            self.seed_codes = component_dict["seed_codes"]
        self.response_superstages = component_dict["response_stages"]
        self.type = component_type
        self.ref_code = ref_code
        self.sample_rate = sample_rate 
        self.response = None

    def __repr__(self):
        return "<OBS_Instrument_Component: {}>".format(self.ref_code)

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
