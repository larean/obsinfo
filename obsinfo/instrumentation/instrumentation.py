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

# obsinfo modules
from ..misc.info_files import (dict_update, load_information_file, root_symbol,
                               info_dict_configure)
from ..misc import FDSN
from .instrument_components import Instrument_components


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
            temp["instrumentation"]["ref_file"]["$ref"]
        self.instruments = temp["instrumentation"]["instruments"]

    def __repr__(self):
        return "<OBS_Instrumentation: facility={}>".format(
            self.facility["reference_name"])

    def _count_components(self, counting_dict, instrument,
                          components, debug=False):
        """
        Adds instrument components to a counting dictionary

        Looks through instrument's 'base_channel' and 'das_channels' fields

        :param counting_dict: dictionary with subfields "exists" and "n_cites"
        :param instrument: instrument ref dictionary
        :param components: Instrument_components object
        """
        counting_dict = self._count_components_onechan(
            counting_dict, instrument["base_channel"], components)
        for das_channel in instrument["das_channels"].values():
            counting_dict = self._count_components_onechan(counting_dict,
                                                           das_channel,
                                                           components)
        return counting_dict

    def _count_components_onechan(self, counting_dict, channel, components):
        """
        Adds channel components to a counting dictionary

        :param counting_dict: dictionary with subfields "exists" and "n_cites"
        :param channel: instrument channel ref dictionary
        :param components: Instrument_components object
        """
        # print(yaml.dump(channel))
        for key, values in channel.items():
            if "ref_code" in values:
                ref_code = values["ref_code"]
                if ref_code in counting_dict:
                    counting_dict[ref_code]["n_cites"] += 1
                else:
                    counting_dict[ref_code] = dict(n_cites=1, exists=None,
                                                   component_type=key,
                                                   config_list=False)
                    # print("components=", components)
                    component = components.get_component(key.split('_')[0],
                                                         ref_code)
                    if component:
                        counting_dict[ref_code]["exists"] = True
#                         if type(component) == list:
#                             counting_dict[ref_code]["config_list"] = [
#                                 x[len(ref_code) + 1] for x in component
#                             ]
                    else:
                        counting_dict[ref_code]["exists"] = False
        return counting_dict

    def print_elements(self):
        """
        Print all instruments (descriptions and  serial numbers)
        """
        for key, element in sorted(self.instruments.items()):
            description = None
            # print(element)
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
            configs = []
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
                                       indent=8), end='')
            if SNs:
                print('  ' + yaml.dump({"specified SNs": sorted(set(SNs))},
                                       indent=8), end='')
#             if "specific" in self.instruments:
#                 if key in self.instruments["specific"]:
#                     SNs = sorted(self.instruments["specific"][key])
#             print(f'{key}: description="{description}", specified_SNs={SNs}')

    def check_dependencies(self, print_names=False):
        """
        Verify that the components file exists and contains requested components

        Prints error message if anything fails
        returns:
        :returns file_exists: true if file exists, false otherwise
        :returns components_exist: true if all components exist, else false
        :returns n_components: number of components checked (including repeats)
        """
        comp_file = os.path.join(self.basepath, self.components_file)
        if not os.path.isfile(comp_file):
            print(f'Intrument_components file not found: "{comp_file}"')
            return False, False, None
        components = Instrument_components(comp_file)
        # print("check_dependencies:components=", components)
        counting_dict = dict()

        # Loop through instruments, counting instrument components
        for key, instrument in self.instruments.items():
            counting_dict = self._count_components(counting_dict,
                                                   instrument, components,
                                                   print_names)
            # print(key)
            # print(instrument)
            # print(yaml.dump(counting_dict))
        total_components, total_found, total_cites = 0, 0, 0

        # Loop through and print instrument components
        for ref_code, value in sorted(counting_dict.items()):
            total_components += 1
            n_cites = value["n_cites"]
            total_cites += n_cites
            if n_cites == 1:
                cite_str = " 1 cite "
            else:
                cite_str = f"{n_cites:2d} cites"
            if value["exists"]:
                total_found += 1
                if print_names:
                    print(f"        FOUND ({cite_str}): {ref_code}")
            else:
                print(f"    NOT FOUND ({cite_str}): {ref_code}")
        config_header_written = False
        for ref_code, value in sorted(counting_dict.items()):
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
    """
    One instrument from an instrumentation.yaml file
    """
    
    def __init__(self, ref_file, inst_dict, basepath, format_version,
                 revision, facility, referring_file=None,
                 ref_code=None,serial_number=None):
        """
        Create an instrument from components

        :param inst_dict: Dictionary containing full instrument description
        :param ref_file: Name of instrument_components.yaml file
        """

        # SET ATTRIBUTES
        self.basepath = basepath
        self.format_version = format_version
        self.revision = revision
        self.facility = facility
        self.components_file = ref_file
        self.config_description = None

        # SET INSTRUMENT
        self.equipment = FDSN.equipment_type(inst_dict["equipment"])
        self.ref_code = ref_code or self.equipment.model
        if serial_number:
            # self.serial_number = serial_number
            self.equipment.serial_number = serial_number
        # else:
        #     self.serial_number = self.equipment.serial_number
        for das_channel in inst_dict["das_channels"].values():
            das_channel = dict_update(inst_dict["base_channel"],das_channel)
        # self.base_channel = inst_dict["base_channel"]
        self.das_channels = inst_dict["das_channels"]
        if 'config_description' in inst_dict:
            self.equipment.description = self.equipment.description +\
                f" [config: {inst_dict['config_description']}]"


    @classmethod
    def from_ref(cls, ref_file, inst_spec_dict, referring_file=None):
        """
        Read instrument from an instrumentation.yaml file

        inst_spect_dict["ref_code"] must be a valid code in the
        instrumentation.yaml file
    
        :param ref_file: Name of instrumentation.yaml file
        :param inst_spec_dict: A dictionary containing "ref_code" field and
                               optional fields:
                                "config" (str)
                                "serial_number" (str)
                                "chan_mods" (obj with subfields
                                    "base"
                                    "by_orientation"
                                    "by_das"
                                The chan_mods field allows you to modify any
                                value in the instrument's base_channel and
                                das_channel fields
        """        
        instrumentation = Instrumentation(ref_file, referring_file)
        
        # SET ATTRIBUTES
        basepath = instrumentation.basepath
        format_version = instrumentation.format_version
        revision = instrumentation.revision
        facility = instrumentation.facility
        components_file = instrumentation.components_file

        # SET INSTRUMENT
        ref_code = inst_spec_dict["ref_code"]
        serial_number = inst_spec_dict.get("serial_number", None)
        inst_dict = _get_instrument_dict(instrumentation, ref_code)
#         print(60*'=')
#         pprint.pprint(inst_dict)
#         print(60*'=')
#         print(serial_number, inst_spec_dict.get('config',None))
        # SET SPECIFIC CONFIGURATIONS (IF ANY)
        inst_dict=info_dict_configure(inst_dict,
                                      inst_spec_dict.get('config',None),
                                      serial_number)
        # SET CHANNEL_MODS
        if "chan_mods" in inst_spec_dict:
            inst_dict=_apply_chan_modes(inst_dict,inst_spect_dict["chan_mods"])
#         pprint.pprint(inst_dict)
#         print(60*'=')
        return cls(components_file, inst_dict, basepath, format_version,
                   revision, facility, os.path.join(basepath,ref_file), 
                   ref_code=ref_code, serial_number=serial_number)

    def _apply_chan_mods(inst_dict,chan_mods):
        """
        Apply channel modifications to an Instrument dictionary
        
        chan_mods is a dictionary with the following possible keys:
            "base": dictionary of modifications to apply to instrument's
                    "base_channel" field
            "by_orientation": dictionary of modifications to apply to
                              instrument "das_channels" based on orientation
                              code
            "by_das": dictionary of modifications to apply to instrument
                      "das_channels" based on das_code
        All of these modifications are applied using info_files.dict_update()
        
        :param inst_dict: Instrument dictionary
        :param chan_mods: channel modificiations
        :type chan_mods, inst_dict: dict
        """
        if "by_orientation" in chan_mods and "by_das" in chan_mods:
            raise NameError("Cannot specify both 'by_das' and 'by_orientation' in 'chan_mods'")
        if "base" in chan_mods:
            if "base_channel" in inst_dict:
                inst_dict["base_channel"] = \
                    dict_update(inst_dict["base_channel"], chan_mods["base"])
            else:
                inst_dict["base_channel"] = chan_mods["base"]
        if "by_orientation" in chan_mods:
            for key, val in chan_mods["by_orientation"].items():
                das_key = get_das_key(key)
                inst_dict = _update_das_channel(inst_dict,key,val)
        if "by_das" in chan_mods:
            for key, val in chan_mods["by_das"].items():
                inst_dict = _update_das_channel(inst_dict,key,val)
        return inst_dict

    def _update_das_channel(self,inst_dict,das_key,val):
        if das_key in inst_dict["das_channels"]:
            inst_dict["das_channels"][das_key] = \
                dict_update(inst_dict["base_channel"], chan_mods["base"])
        else:
            inst_dict["das_channels"][das_key] = chan_mods["base"]
        return inst_dict

    def __repr__(self):
        return f"<{__name__}: ref_code={self.ref_code}, " +\
               f"serial_number={self.equipment.serial_number}, " +\
               f"{len(self.das_channels):d} channels >"

#     def __find_dc_key(self, orientation_code, das_channel=None, debug=False):
#         """
#         Find the das_channel corresponding to the given orientation code
# 
#         Also validates that the orientation code is possible and unique,
#         using das_channel if necessary
#         
#         :param orientation_code: orientation_code
#         :param das_channel: das channel name
#         :type orientation_code, das_channel: str
#         :returns dc_key: das channel name
#         """
#         if das_channel:
#             return das_channel
#         dc_key = None
#         das_orientation_codes = []
#         for key, value in self.das_channels.items():
#             das_orientation_codes.append(value["orientation_code"])
#             if value["orientation_code"] == orientation_code:
#                 if dc_key:
#                     raise NameError(f'"{orientation_code}" is a non-unique '
#                                     "orientation code for this instrument\n"
#                                     "You must use _by_das")
#                 if das_channel:
#                     if das_channel == key:
#                         dc_key = key
#                 else:
#                     dc_key = key
#         if not dc_key:
#             raise NameError(f"instrument {self.reference_code} : " +
#                             "No das_channel with orientation code " +
#                             f"'{orientation_code}' found, " +
#                             f"only {das_orientation_codes} found")
#         return dc_key


    def load_components(self, components_file, referring_file=None):
        """
        Load components into instrument

        :param components_file: name of components file
        :param referring_file: file that referred to the components file
                               (for resolving paths)
        """
        components = Instrument_components(components_file, referring_file)

        # print(self)
        for key, channel in self.das_channels.items():
#             # Inject base channel into das_channel
#             print(key)
#             print(channel)
#             channel = dict_update(channel, self.base_channel)
#             print(channel)
            self.fill_channel(key, components)
        self.resource_id = self.facility["ref_name"] +\
                           components.revision["date"]

    def fill_channel(self, channel_key, components):
        """
        Replace channel component strings with the actual components

        :param components:
        :type components: class Instrument_components
        """
        channel = self.das_channels[channel_key]
        # print("Channel=", channel)
        for block_type in ["datalogger", "preamplifier", "sensor"]:
            if block_type not in channel:
                if block_type == "preamplifier":
                    print(f'component type "{block_type}" absent, ignored')
                    continue  # to ignore empty  preamplifier
                raise NameError(f'component type "{block_type}" missing!')
            # print("Component=", block_type, channel[block_type])
            ref_code = channel[block_type]["ref_code"]
            serial_number = channel[block_type].get("serial_number", None)
            config = channel[block_type].get("config", None)
            # print("components=", components)

            channel[block_type] = components.get_component(block_type,
                ref_code, config, serial_number)
            # print("channel[block_type]========", channel[block_type])
            if not channel[block_type]:
                raise NameError(
                    f"Component not found: type:{block_type}, "
                    f"ref_code:{ref_code}, "
                    f"serial_number:{serial_number}, "
                    f"config:{config}")

    def modify_sensors(self, sensor_dict, referring_file=None):
        """ 
        Modify sensors within an instrument
        
        :param sensor_dict: dictionary with key = component, val=[ref_code,
                         serial_number]
        :type sensor_dict: dict
        """

        components, path = load_information_file(
            self.components_file + root_symbol +
            "instrument_components/instrument_blocks",
            referring_file,
        )
        sensors = components["sensor"]
        for channel, values in sensor_dict.items():
            self._modify_sensor(sensors[values["ref_code"]], channel, values)

    def _modify_sensor(self, sensor, channel, values):
        """
        Modify sensor within an instrument
        
        :param sensor: dictionary of sensors from instrumnet_components file
        :param channel: channel name?
        :param values: channel values?
        """
        sensor = sensor.copy()
        SN = values["serial_number"]
        sensor["serial_number"] = SN
        sensor=info_dict_configure(sensor, values.get("config", None), SN)
        self.channels[channel]["sensor"] = sensor

    def fill_responses(self, debug=False):
        """
        Fill in object's instrument responses
        """
        for name, channel in self.das_channels.items():
            # print(yaml.dump(channel))
            channel["sensor"].fill_responses()
            if "preamplifier" in channel:
                channel["preamplifier"].fill_responses()
            channel["datalogger"].fill_responses()
#             print(f"channel {name} has : " +
#                   f"{len(channel['sensor'].response):d} sensor, " +
#                   f"{len(channel['preamplifier'].response):d} preamp, " +
#                   f"{len(channel['datalogger'].response):d} logger stages")
            channel["response"] = []
            channel["response"].append(channel["sensor"].response)
            if "preamplifier" in channel:
                channel["response"].append(channel["preamplifier"].response)
            channel["response"].append(channel["datalogger"].response)
            
            
def _get_instrument_dict(instrumentation, ref_code):
    """
    Returns dictionary value corresponding to key = ref_code
    
    :param instrumentation: dictionary of instruments
    :param ref_code: instrument key
    :type ref_code: str
    """
    if ref_code not in instrumentation.instruments:
        raise NameError(f'"{self.ref_code}" not in instrumentation')
    return instrumentation.instruments[ref_code]
