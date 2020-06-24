"""
InstrumentationConfig class

Used to configure an Instrumentation
"""
# Standard library modules

# Non-standard modules

# obsinfo modules
from .instrument_component import (Datalogger, Sensor, Preamplifier,
                                   Equipment, InstrumentComponent)


class InstrumentationConfig(object):
    """
    Instrumentation Configuration
    
    """
    def __init__(self, base_instrumentation, datalogger_config,
                 channel_mods=None, serial_number=None,
                 sensor_config=None, preamplifier_config=None):
        """
        Constructor
        
        :param base_instrumentation: base Instrumentation
        :kind base_instrumentation: ~class `obsinfo.InfoDict`
        :param datalogger_config: datalogger configuration
        :kind datalogger_config: str
        :param channel_mods: Modifications to each channel
        :kind channel_mods: ~class `obsinfo.instrumentation.ChannelMods`
        :param serial_number: instrumentation serial number
        :kind serial_number: str, optional
        :param sensor_config: sensor configuration
        :kind sensor_config: str, optional
        :param preamplifier_config: preamplifier configuration
        :kind preamplifier_config: str, optional
        """
        self.base_instrumentation = base_instrumentation
        self.datalogger_config = datalogger_config
        self.channel_mods = channel_mods
        self.serial_number = serial_number
        self.sensor_config = sensor_config
        self.preamplifier_config = preamplifier_config

    def __repr__(self):
        s = f'InstrumentationConfig({type(self.base_instrumentation)}, '
        s += f'"{self.datalogger_config}"'
        if self.channel_mods:
            ", channel_mods={type(self.channel_mods)}"
        if self.serial_number:
            ', serial_number="{serial_number}"'
        if self.serial_number:
            ', sensor_config="{sensor_config}"'
        if self.serial_number:
            ', preamplifier_config="{preamplifier_config}"'
        return s

    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create InstrumentConfiguration instance from an info_dict
        """
        obj = cls(Instrumentation.from_info_dict(info_dict.get('base',
                                                               None)),
                  info_dict.get('datalogger_config', None),
                  ChannelMods.from_info_dict(info_dict.get('channel_mods', None)),
                  info_dict.get('serial_number', None),
                  info_dict.get('sensor_config', None),
                  info_dict.get('preamplifier_config', None))
        return obj

    def to_Instrumentation(self):
        """
        Output instrumentation based on configurations and modifications
        """
        # First, apply modifications
        if self.channel_mods:
            self.base = self.channel_mods.apply_mods(self.base)

        # Next, configurations
        self.base.config_datalogger(self.datalogger_config)
        self.base.config_sensor(self.sensor_config)
        self.base.config_preamplifier(self.preamplifier_config)

        # Finally, serial numbers
        self.base.set_serial_number(self.datalogger_config)

        return Instrumentation.from_info_dict(self.base)


class ChannelMods(object):
    """
    Instrumentation channel modifications

    values are kept as InfoDict, so that they can be directly applied
    to the base Instrumetation InfoDict
    """
    def __init__(self, base=None, by_orientation=None, by_chan_loc=None,
                 by_das=None):
        """
        :param base: modifications applied to all channels
        :kind data: ~class `obsinfo.InfoDict`
        """
        assert not ((by_orientation and by_das) or (by_orientation and by_chan_loc)
            or (by_das and by_chan_loc)), 'more than one type of chan spec'
        self.base = base
        self.by_orientation = by_orientation
        self.by_das = by_das
        self.by_chan_loc = by_chan_loc        

    def apply_mods(self, inst):
        """
        apply channel modifications to an Instrumentation object
        
        :param inst: object to modify
        :kind inst: ~class `obsinfo.instrumentation.Instrumentation`
        """
        if self.base:
            pass
        if self.by_orientation:
            pass
        elif self.by_das:
            pass
        elif self.by_chan_loc:
            pass

class ChannelConfiguration(object):
    """
    Channel modifications and deployment-specific information

    values are kept as InfoDict, so that they can be directly applied
    to the base Instrumetation InfoDict
    """

class InstrumentComponentConfiguration(object):
    """
    Instrument Component modifications

    values are kept as InfoDict, so that they can be directly applied
    to the base Instrumetation InfoDict
    """
