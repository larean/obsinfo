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
import pprint
# import sys

# Non-standard modules
import yaml
# import obspy.core.util.obspy_types as obspy_types
# import obspy.core.inventory as inventory
# import obspy.core.inventory.util as obspy_util
# from obspy.core.utcdatetime import UTCDateTime

# obsinfo modules
from ..misc.info_files import (load_information_file, root_symbol,
                               info_dict_configure, dict_update)
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

    def __load_specific_component(self, component, serial_number=None,
                                  debug=False):
        """
        Return a component specified by serial number and config
        
        :param component: Instrument_component
        :param serial_number: desired serial number
        :param config: Desired configuration
        :type serial_number,config: str
        """
        
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
        :param serial_number: component serial number
        :param get_responses: return with responses filled in
        :type get_responses: bool
        
        :returns: Instrument_component object
        """
        components=self.instrument_blocks[block_type]
        if ref_code not in components:
            return None
        
        # Fill in config and serial number
        component = components[ref_code]
        # First check serial number
        if serial_number:
            component['equipment']['serial_number'] = serial_number
        component = info_dict_configure(component, config, serial_number)
                    
        # Return as Instrument_component
        return Instrument_component(component, self.basepath, block_type,
                                    ref_code)

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
            if configs:
                print('  ' + yaml.dump({"configurations": configs},
                                       indent=8),end='')
            if SNs:
                print('  ' + yaml.dump({"specified SNs": sorted(set(SNs))},
                                       indent=8),end='')
 
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
                                    self.basepath,print_names)
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
                 ref_code=None, config=None, serial_number=None, debug=False):
        """ 
        Create an Instrument_component object
        
        :param component_dict: component dictionary from instrument_components
                               information file, selected using ref_code
                               and customized using config and serial_number
        :param basepath: full path of directory containing
                         instrument_components file
        :param component_type: component type ('datalogger','preamplifier'
                               or 'sensor')
        :param ref_code: ref code used to access this component
        :param config: configuration code used to customize this component
        :param serial_number: serial_number used to customize this component
        """
        if debug:
            print(basepath)
        self.basepath = basepath
        self.type = component_type
        self.ref_code = ref_code
        self.config = config
        self.serial_number = serial_number
#         print(60*'=')
#         pprint.pprint(component_dict)
#         print(f'config={config}, serial_number={serial_number}')
        # Modify component dict for specific configuration/serial number
        component_dict=info_dict_configure(component_dict, config, 
                                           serial_number)
#         print(60*'=')
#         pprint.pprint(component_dict)
        self.equipment = FDSN_equipment_type(component_dict["equipment"])
        self.seed_codes = component_dict.get("seed_codes", None)
        self.response_superstages = component_dict.get("response_stages", None)
        self.sample_rate = component_dict.get("sample_rate", None)
#         self.configurations = component_dict.get("configurations", None)
#         self.serial_numbers = component_dict.get("serial_numbers", None)
        self.response = None

    def __repr__(self):
        return "<OBS_Instrument_Component: {}>".format(self.ref_code)

    def fill_responses(self):
        """ Fill in instrument responses from references"""
        # print("self.response_superstages=", end="")
        # print(yaml.dump(self.response_superstages))
        self.__read_response_yamls()
        # print("self.response=", end="")
        # print(yaml.dump(self.response))

    def __read_response_yamls(self):
        """
        READ INSTRUMENT RESPONSES FROM RESPONSE_YAML FILES
        """
        # print(self)
        self.response = {'decimation_info':None,'stages':list()}
        #print("{:d} superstage files for the component".format(
        #            len(self.response_superstages)))
        #print(self.response_superstages)
        for superstage in self.response_superstages:
            superstage_file = superstage["$ref"]
            # print("Reading superstage file {}".format(superstage_file))
            response, temp = load_information_file(
                superstage_file + root_symbol + "response", self.basepath
            )
            self.response['decimation_info'] = response['decimation_info'] if 'decimation_info' in response else None
            for stage in response['stages']:
                # IF STAGE FILTER IS A "$ref", READ AND INJECT THE REFERRED FILE
                if "$ref" in stage["filter"]:
                    # READ REFERRED FILE
                    filter_ref = os.path.join(os.path.split(superstage_file)[0],
                                              stage["filter"]["$ref"])
                    # print("filter file ref:", filter_ref)
                    filter, temp = load_information_file(filter_ref, self.basepath)
                    # MAKE SURE IT'S THE SAME TYPE, IF SO INJECT
                    stage["filter"] = filter
                self.response['stages'].append(stage)
            # print("{:d} stages read".format(len(stages)))
        # print("{:d} total stages in component".format(len(self.response)))
        # print(yaml.dump(self.response))
