"""
Print complete stations from information in network.yaml file

nomenclature:
    A "measurement instrument" is a means of recording one physical parameter,
        from sensor through dac
    An "instrument" is composed of one or more measurement instruments
"""
# Standard library modules
# import math as m
# import json
import pprint
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
from ..misc import FDSN
from ..instrument_components import Instrument_components


class Instrumentation:
    """ Everything in an instrumentation.yaml file

    Functions are very similar to those in instrument_components: should there
    be a shared class?
    """

    def __init__(self, filename, referring_file=None):
        temp, basepath = load_information_file(filename, referring_file)

        self.basepath = basepath
        self.format_version = temp["format_version"]
        self.revision = temp["revision"]
        self.facility = temp["instrumentation"]["facility"]
        self.components_file =\
            temp["instrumentation"]["instrument_components"]["$ref"]
        self.instruments = temp["instrumentation"]["instruments"]

    def __repr__(self):
        return "<OBS_Instrumentation: facility={}>".format(
            self.facility["reference_name"]
        )

    def __components_exist(self, components_dict, instrument,
                           components, print_names, debug=False):
        for das_component in instrument["das_components"].values():
            if debug:
                print(yaml.dump(das_component))
            for key, values in das_component.items():
                if "reference_code" in values:
                    ref_code = values["reference_code"]
                    if ref_code in components_dict:
                        components_dict[ref_code]["n_cites"] = (
                            components_dict[ref_code]["n_cites"] + 1
                        )
                    else:
                        components_dict[ref_code] = dict(n_cites=1,
                                                         exists=None,
                                                         component_type=key,
                                                         config_list=False)
                        if debug:
                            print("components=", components)
                        component = components.get_component(key, ref_code)
                        if component:
                            components_dict[ref_code]["exists"] = True
                            if type(component) == list:
                                components_dict[ref_code]["config_list"] = [
                                    x[len(ref_code) + 1] for x in component
                                ]
                        else:
                            components_dict[ref_code]["exists"] = False
        return components_dict

    def print_elements(self, debug=False):
        """ prints all instruments (descriptions and  serial numbers)
        """
        for key, element in sorted(self.instruments["generic"].items()):
            description = None
            if debug:
                print(element)
            if "equipment" in element:
                equipment = element["equipment"]
                if type(equipment) == dict:
                    equipment = FDSN.equipment_type(equipment)
                description = equipment.description
            if not description:
                if "description" in element:
                    description = element["description"]
                else:
                    description = "None provided"
            SNs = []
            if "specific" in self.instruments:
                if key in self.instruments["specific"]:
                    SNs = sorted(self.instruments["specific"][key])
            print(f'{key}: description="{description}", specified_SNs={SNs}')

#     def verify_individuals(self):
#         """ Verify that all "specific" instruments have a generic counterpart
#
#             returns true if so, false + error message if not
#         """
#         checksOut = True
#         no_error_for_type = True
#         if "specific" in self.instruments:
#             for model in self.instruments["specific"].keys():
#                 if model not in self.instruments["generic"]:
#                     if no_error_for_type:
#                         print("  {:>15}: ".format(block_type), end="")
#                         no_error_for_type = False
#                     checksOut = False
#                     print(
#                           15 * " "  +
#                           f'"{:model}" is in "specific" but not in "generic"'
#                     )
#         return checksOut

    def check_dependencies(self, print_names=False, debug=False):
        """ Verify that the components file exists and contains requested components

            Prints error message if anything fails
            returns:
                file_exists: true if file exists, false otherwise
                components_exist: true if all components exist, false otherwise
                n_components: number of components checked (including repeats)
        """
        comp_file = os.path.join(self.basepath, self.components_file)
        if not os.path.isfile(comp_file):
            print(f'Intrument_components file not found: "{comp_file}"')
            return False, False, None
        components = Instrument_components(comp_file)
        if debug:
            print("check_dependencies:components=", components)
        components_dict = dict()
        for instrument in self.instruments["generic"].values():
            if debug:
                print(yaml.dump(instrument))
            components_dict = self.__components_exist(
                components_dict, instrument, components, print_names
            )
        total_components = 0
        total_found = 0
        total_cites = 0
        for ref_code, value in sorted(components_dict.items()):
            total_components = total_components + 1
            n_cites = value["n_cites"]
            total_cites = total_cites + n_cites
            if n_cites == 1:
                cite_str = "1 cite"
            else:
                cite_str = f"{n_cites:2d} cites"
            if value["exists"]:
                # comments = ""
                total_found = total_found + 1
                if print_names:
                    print(f"        FOUND ({cite_str}): {ref_code}")
            else:
                print(f"    NOT FOUND ({cite_str}): {ref_code}")
        config_header_written = False
        for ref_code, value in sorted(components_dict.items()):
            if value["config_list"]:
                if not config_header_written:
                    print(" **Some component citations must be completed in "
                          "the network.yaml file.")
                    config_header_written = True
                print(" **   - Stations using instruments containing: " +
                      f"the {ref_code} {value['component_type']}")
                print(" **                              must specify: " +
                      f"{value['component_type']}_config")
                print(" **                   using one of the values: " +
                      f"{value['config_list']}")
        return True, total_components, total_found, total_cites


class Instrument:
    """ One instrument from instrumentation.yaml file"""

    def __init__(self, filename, inst_dict, referring_file=None,
                 debug=False):
        """
        Load an instrument

        Inputs:
            inst_dict: is an OBS_Station.instrument dictionary
                    inst_dict['ref_code'] must correspond to
                        a key in instrumentation['instruments'])
        """

        if debug:
            print(60 * "=")
            print(type(inst_dict))
            pprint.pprint(inst_dict)

        instrumentation = Instrumentation(filename, referring_file)

        # SET ATTRIBUTES
        self.updated_from_serial_number = False
        self.config_description = None
        self.basepath = instrumentation.basepath
        self.format_version = instrumentation.format_version
        self.revision = instrumentation.revision
        self.facility = instrumentation.facility
        self.components_file = instrumentation.components_file

        self.ref_code = inst_dict["ref_code"]
        self.serial_number = inst_dict.get("serial_number", None)
        inst = self.__get_instrument(instrumentation, self.ref_code)

        self.base_channel = inst["base_channel"]
        self.das_channels = inst["das_channels"]
        # SET SPECIFIC ATTRIBUTES (IF ANY)
        if 'config' in inst_dict:
            self._update_from_config(inst_dict['config'], inst)
            if 'serial_number' in inst_dict:
                self._update_from_serial_number(inst_dict['serial_number'],
                                                inst['configuration'])
        if not self.updated_from_serial_number:
            if 'serial_number' in inst_dict:
                self._update_from_serial_number(
                    inst_dict['serial_number'], inst)
#         specific = self.__get_specific_instrument(instrumentation)
#         if specific:
#             self.__load_specific_instrument(specific)
#        self.__update_das_components(inst_dict)
        self.equipment = FDSN.equipment_type(inst["equipment"])
        if self.config_description:
            self.equipment.description = self.equipment.description +\
                f" [config: {self.config_description}]"
        self.equipment.serial_number = self.serial_number

    def __repr__(self):
        return f"<{__name__}: reference_code={self.reference_code}, " +\
               f"serial_number={self.serial_number}, " +\
               f"{len(self.das_components):d} channels >"

    def __get_instrument(self, instrumentation, ref_code):

        if self.ref_code not in instrumentation.instruments:
            raise NameError(f'"{self.ref_code}" not in instrumentation')
        return instrumentation.instruments[self.ref_code]

    def _update_from_config(self, config_ref, inst):
        if 'configurations' not in inst:
            raise NameError('You specified an instrument configuration' +
                            'but there are none')
        if config_ref not in inst['configurations']:
            raise NameError('No instrument configuration "{config_ref}"')
        config = inst['configurations'][config_ref]
        if 'description' in config:
            self.config_description = config['description']
        if 'base_channel' in config:
            self._update_base_channel(config['base_channel'])
        if 'das_channels' in config:
            self._update_das_channels(config['das_channels'])

    def _update_base_channel(self, new_base_info):
        """ Update instrument base_channel """
        # datalogger_ref, preamplifier_ref and/or sensor_ref
        for key, val in new_base_info.items():
            for subval in val.items():
                self.base_channel[key][val] = subval

    def _update_das_channels(self, new_das_info):
        """ Update instrument das_channels """
        # das channel codes
        for channel_code, keys in new_das_info.items:
            if channel_code not in self.das_channels:
                NameError(f"Unknown channel code: {channel_code}")
            for key, val in keys.items:
                if key == 'orientation_code':
                    self.das_channels[channel_code].orientation_code = val
                else:
                    for subval in val.items():
                        self.das_channels[channel_code][key][val] = subval

#     def __load_specific_instrument(self, specific, debug=False):
#         reference_code = self.reference_code
#         serial_number = self.serial_number
#         if "orientation_codes" in specific:
#             for or_code, inst_spec in specific["orientation_codes"].items():
#                 das_comp = self.__find_dc_key(or_code)
#                 if debug:
#                     print("or_code=",or_code,
#                           "das_comp=",das_comp,
#                           "inst_spec=",inst_spec)
#                 self.__inject_measurement_instrument_parameters(das_comp,
#                                                                 inst_spec)
#         elif "das_channels" in specific:
#             for das_comp, inst_spec in specific["das_channels"].items():
#                 if debug:
#                     print("das_comp=", das_comp, "inst_spec=", inst_spec)
#                 self.__inject_measurement_instrument_parameters(das_comp,
#                                                                 inst_spec)
#         else:
#             raise NameError(
#                 'Neither "orientation_codes" nor "das_channels" \
#                     found for specific instrument {} {}'.format(
#                     reference_code, serial_number)
#             )

    def __update_das_components(self, inst_dict, debug=False):
        # INCORPORATE SPECIFIC CHANNEL VALUES
        for loc_key, value in inst_dict["channel_codes_locations"].items():
            das_component = value.get("das_component", None)
            dc_key = self.__find_dc_key(loc_key[2], das_component)
            self.__insert_codes(dc_key, loc_key)
            self.__update_das_component(dc_key, value)

    def __find_dc_key(self, orientation_code, das_component=None, debug=False):
        """ finds the das_component corresponding to the orientation code

            Also validates that the orientation code is possible and unique,
            using das_channel if necessary
        """
        if das_component:
            return das_component
        dc_key = None
        das_orientation_codes = []
        for key, value in self.das_components.items():
            das_orientation_codes.append(value["orientation_code"])
            if value["orientation_code"] == orientation_code:
                if dc_key:
                    raise NameError(
                        '"{}" is a non-unique orientation code '
                        "for this instrument\n"
                        "You must specify das_component"
                        'in each "channel_codes_locations" declaration'
                        "".format(orientation_code)
                    )
                if das_component:
                    if das_component == key:
                        dc_key = key
                else:
                    dc_key = key
        if not dc_key:
            raise NameError(f"instrument {self.reference_code} : " +
                            "No das_component with orientation code " +
                            f"'{orientation_code}' found, " +
                            f"only {das_orientation_codes} found")
        return dc_key

    def __insert_codes(self, dc_key, chan_loc, debug=False):
        """ inserts location and seed codes into the das_component
        """
        if debug:
            print(chan_loc)
            print(dc_key)
            print(self.das_components[dc_key])
        self.das_components[dc_key]["band_code"] = chan_loc[0]
        self.das_components[dc_key]["inst_code"] = chan_loc[1]
        self.das_components[dc_key]["location_code"] = chan_loc[4:6]

    def __update_das_component(self, dc_key, chan_values, debug=False):
        """ update a das_component with net:sta:loc:chan values """
        dc = self.das_components[dc_key]
        if "sample_rate" in chan_values:
            dc["sample_rate"] = chan_values["sample_rate"]
        if "serial_number" in chan_values:
            dc["equipment"].serial_number = chan_values["serial_number"]
        if "location_code" in chan_values:
            dc["location_code"] = chan_values["location_code"]
        if "start_date" in chan_values:
            dc["start_date"] = chan_values["start_date"]
        if "end_date" in chan_values:
            dc["end_date"] = chan_values["end_date"]

        for block_type in ["sensor", "datalogger", "preamplifier"]:
            if block_type in chan_values:
                for key in chan_values[block_type]:
                    dc[block_type][key] = chan_values[block_type][key]
        if "datalogger_config" in chan_values:
            dl_config = chan_values["datalogger_config"]
            if debug:
                print("ADDING datalogger_config ({})".format(dl_config))
            dc["datalogger"]["reference_code"] = (
                dc["datalogger"]["reference_code"] + "_" + dl_config
            )

    def __inject_measurement_instrument_parameters(self, das_component,
                                                   instrument_spec,
                                                   debug=False):
        """
        Read and inject specific values into a measurement instrument
        """
        if debug:
            print(instrument_spec)
        for key, values in instrument_spec.items():
            if "reference_code" in values:
                self.das_components[das_component][key]["reference_code"] =\
                    values["reference_code"]
            if "serial_number" in values:
                self.das_components[das_component][key]["serial_number"] =\
                    values["serial_number"]

    def load_components(self, components_file, referring_file=None):
        """
        Load components into instrument

        components_file = name of components file
        referring_file = file that referred to the components file
                         (for resolving paths)
        """
        components = Instrument_components(components_file, referring_file)

        for key in self.das_components:
            self.fill_channel(key, components)
        self.resource_id = self.facility["reference_name"] +\
            components.revision["date"]

    def fill_channel(self, channel_key, components, debug=False):
        """ Replace channel component strings with the actual components

            components is an OBS_Instrument_Components object
                    (direct from *_instrument_components.yaml)
        """
        channel = self.das_components[channel_key]
        if debug:
            print("Channel=", channel)
        for block_type in ["datalogger", "preamplifier", "sensor"]:
            if block_type == "preamplifier" and block_type not in channel:
                print('component type "{}" absent, ignored'.format(block_type))
                continue  # to ignore empty  preamplifier
            if debug:
                print("Component=", block_type, channel[block_type])
            reference_code = channel[block_type]["reference_code"]
            serial_number = channel[block_type].get("serial_number", None)
            if debug:
                print("components=", components)

            channel[block_type] = components.get_component(
                block_type, reference_code, serial_number
            )
            if debug:
                print("channel[block_type]========", channel[block_type])
            if not channel[block_type]:
                raise NameError(
                    "Component not found: type:{}, "
                    "reference_code:{}, serial_number:{}".format(
                        block_type, reference_code, serial_number
                    )
                )

    def modify_sensors(self, sensor_dict, referring_file=None):
        """ Modify sensors within an instrument
        Inputs:
            sensor_dict: dictionary with key = component, val=[reference_code,
                         serial_number]
        """

        components, path = load_information_file(
            self.components_file + root_symbol +
            "instrument_components/instrument_blocks",
            referring_file,
        )
        sensors_generic = components["sensor"]["generic"]
        sensors_specific = components["sensor"]["specific"]

        for channel, values in sensor_dict.items():
            ref_code = values["reference_code"]
            SN = values["serial_number"]
            self.channels[channel]["sensor"] = sensors_generic[ref_code].copy()
            self.channels[channel]["sensor"]["serial_number"] = SN
            print("Setting {} {} SN to {}".format(channel, ref_code, SN))
            if ref_code in sensors_specific:
                if SN in sensors_specific[ref_code]:
                    for key, value in sensors_specific[ref_code][SN].items():
                        print("Setting {} to {}".format(key, value))
                        self.channels[channel]["sensor"][key] = value

    def fill_responses(self, debug=False):
        for name, channel in self.das_components.items():
            if debug:
                print(yaml.dump(channel))
            channel["sensor"].fill_responses()
            if "preamplifier" in channel:
                channel["preamplifier"].fill_responses()
            channel["datalogger"].fill_responses()
            if debug:
                print(f"channel {name} has : " +
                      f"{len(channel['sensor'].response):d} sensor, " +
                      f"{len(channel['preamplifier'].response):d} preamp, " +
                      f"{len(channel['datalogger'].response):d} logger stages")
            channel["response"] = []
            channel["response"].append(channel["sensor"].response)
            if "preamplifier" in channel:
                channel["response"].append(channel["preamplifier"].response)
            channel["response"].append(channel["datalogger"].response)
