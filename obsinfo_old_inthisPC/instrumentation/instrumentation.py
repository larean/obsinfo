"""
Instrumentation and Instrument classes

nomenclature:
    An "Instrument" (measurement instrument) records one physical parameter
    A "Channel" is an Instrument + an orientation code and possibly
        starttime, endtime and location code
    An "Instrumentation" combines one or more measurement Channels
"""
# Standard library modules

# Non-standard modules

# obsinfo modules
from .instrument_component import (Datalogger, Sensor, Preamplifier,
                                   Equipment)
from ..info_dict import InfoDict


class Instrumentation(object):
    """
    One or more Instruments. Part of an obspy/StationXML Station
    """
    def __init__(self, info_dict):
        """
        Constructor
        info_dict may contain a configuration_selection or serial_number for the instrumentation and the corresponding configs or SN 
        for the components: datalogger, preamplifier and sensor

        :param equipment: equipment description
        :type equipment: ~class `Equipment`
        :param channels: list of channels
        :type channels: list of ~class `Channel`
        """
        config_dict = info_dict.get('configuration_definitions', None)
        sn_dict = info_dict.get('serial_number_definitions', None)
        config_selector = info_dict.get('configuration_selection', None)
        sn_selector = info_dict.get('serial_number_selection', None)
        
        if config_selector:
            selected_config = config_dict.get(config_selector)
        if sn_selector:
            selected_sn = config_dict.get(sn_selector)
            
        self.equipment = Equipment(info_dict.get('equipment', None))
        das_channels = info_dict.get('das_channels', {})
        channel_template = info_dict.get('channel_template', {})
        #v here is the info_dict of each das_channel
        self.channels = [Channel(k, v, channel_template, selected_config, selected_sn)
                   for k, v in das_channels.items()]
        
    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create Instrumentation instance from an info_dict
        """
        info_dict = InfoDict(info_dict)
        info_dict.complete_das_channels()
        info_das = info_dict.get('das_channels', {})
        obj = cls(Equipment.from_info_dict(info_dict.get('equipment', None)),
                  [Channel.from_info_dict(v, k)
                   for k, v in info_das.items()])
        return obj

    def __repr__(self):
        s = f'Instrumentation({type(self.equipment)}, '
        s += f'{len(self.channels)} {type(self.channels[0])}'
        return s


class Channel(object):
    """
    Channel Class.

    Corresponds to StationXML/obspy Channel, plus das_channel code
    """
    def __init__(self, channel_label, info_dict, channel_template=None, selected_config=None, selected_sn=None):
        """
        :param instrument: instrument description
        :type instrument: ~class `Instrument`
        :param das_channel: the DAS channel the instrument is on
        :type das_channel: str
        :param orientation_code: orientation code of this channel/instrument
        :type orientation_code: str
        :param location_code: channel location code (if different from network)
        :type location_code: str, opt
        :param startdate: channel startdate (if different from network)
        :type startdate: str, opt
        :param enddate: channel enddate (if different from network)
        :type enddate: str, opt
        """
        #Complete das channel fields with base fields
        self.das_channel = self.complete_das_channel(info_dict, channel_template)
        
        self.instrument = Instrument(info_dict, selected_config, selected_sn)
        self.orientation_code = info_dict.get('orientation_code', None)
        #self.orientation = instrument.seed_orientations[orientation_code] #OJO. Not good. Seed orientations are not there
        self.location_code = reconfigure_channel('location_code', selected_config, selected_sn, None)
        self.startdate = reconfigure_channel('startdate', selected_config, selected_sn, None)
        self.enddate = reconfigure_channel('enddate', selected_config, selected_sn, None)

    def complete_das_channel(self, das_channel, channel_template):
        """
        Take all the fields defined for each das channel and complement them with the channel_template fields
        If das_channel key exists, leave the value. If not, add channel_template key/value
        """
        #If there are no modifications, use default
        if not das_channel:
            return channel_template
        
        for k, v in channel_template.items():
            if k not in das_channel:    
               das_channel[k] = v
        
        return das_channel
    
    def reconfigure_channel(self, key, info_dict, selected_config=None, selected_sn=None, default=None):
        """
        Reconfigure possible values of channel fields. Configuration takes precedence over serial number
        """
        #Implement priority 1    
        if selected_config:
            return instrumentation_selected_config.get(key, default)  
        #Implement priority 2
        elif selected_sn:
            return instrumentation_selected_sn.get(key, default)
        else:
            return info_dict.get(key, default)

    @classmethod
    def from_info_dict(cls, info_dict, das_channel=None):
        """
        Create instance from an info_dict

        :param info_dict: information dictionary at
                          instrument:das_channels level
        :type info_dict: dict
        """

        obj = cls(Instrument.from_info_dict(
                    {'datalogger': info_dict['datalogger'],
                     'sensor': info_dict['sensor'],
                     'preamplifier': info_dict.get('preamplifier', None)}),
                  das_channel,
                  info_dict.get('orientation_code', None),
                  info_dict.get('location_code', None),
                  info_dict.get('startdate', None),
                  info_dict.get('enddate', None))
        return obj

    def __repr__(self):
        s = f'Channel({type(self.instrument)}, "{self.das_channel}", '
        s += f'"{self.orientation_code}"'
        if self.location:
            s += f', {self.location}'
            write_keys = False
        else:
            write_keys = True
        if self.startdate:
            if write_keys:
                s += f', startdate={self.startdate}'
            else:
                s += f', {self.startdate}'
        else:
            write_keys = True
        if self.enddate:
            if write_keys:
                s += f', enddate={self.enddate}'
            else:
                s += f', {self.enddate}'
        else:
            write_keys = True
        s += ')'
        return s

    @property
    def channel_code(self, sample_rate):
        """
        Return channel code for a given sample rate

        :param sample_rate: instrumentation sampling rate (sps)
        :kind sample_rate: float
        """
        inst_code = self.instrument.seed_instrument_code
        assert len(inst_code) == 1,\
            f'Instrument code "{inst_code}" is not a single letter'
        assert len(self.orientation_code) == 1,\
            'Orientation code "{}" is not a single letter'.format(
                self.orientation_code)
        return (self._band_code(sample_rate)
                + inst_code
                + self.orientation_code)

    def _band_code(self, sample_rate):
        """
        Return the channel band code

        :param sample_rate: sample rate (sps)
        """
        bbc = self.instrument.seed_band_base_code
        assert len(bbc) == 1,\
            f'Band base code "{bbc}" is not a single letter'
        if bbc in "FCHBMLVURPTQ":
            if sample_rate >= 1000:
                return "F"
            elif sample_rate >= 250:
                return "C"
            elif sample_rate >= 80:
                return "H"
            elif sample_rate >= 10:
                return "B"
            elif sample_rate > 1:
                return "M"
            elif sample_rate > 0.3:
                return "L"
            elif sample_rate > 0.03:
                return "V"
            elif sample_rate > 0.003:
                return "U"
            elif sample_rate >= 0.0001:
                return "R"
            elif sample_rate >= 0.00001:
                return "P"
            elif sample_rate >= 0.000001:
                return "T"
            else:
                return "Q"
        elif bbc in "GDES":
            if sample_rate >= 1000:
                return "G"
            elif sample_rate >= 250:
                return "D"
            elif sample_rate >= 80:
                return "E"
            elif sample_rate >= 10:
                return "S"
            else:
                raise ValueError("Short period sensor sample rate < 10 sps")
        else:
            raise NameError(f'Unknown band base code: "{bbc}"')


class Instrument(Channel):
    """
    Instrument Class.
    """
    def __init__(self, info_dict, selected_config=None, selected_sn=None):
        """
        :param datalogger: datalogger information
        :type datalogger: ~class `Datalogger`
        :param sensor: sensor information
        :type sensor: ~class `Sensor`
        :param preamplifier: preamplifier information
        :type preamplifier: ~class `Preamplifier`, opt
        """
        assert 'datalogger' in info_dict, 'No datalogger specified'
        assert 'sensor' in info_dict, 'No sensor specified'
        
        datalogger_dict = self.reconfigure_channel('datalogger', info_dict, selected_config, selected_sn, None)
        sensor_dict = self.reconfigure_channel('sensor', info_dict, selected_config, selected_sn, None)
        preamplifier_dict = self.reconfigure_channel('preamplifier', info_dict, selected_config, selected_sn, None)
        # Set equipment parameters
        self.datalogger = InstrumentComponent.dynamic_class_constructor('datalogger', datalogger_dict, selected_config, selected_sn)
        self.sensor = InstrumentComponent.dynamic_class_constructor('sensor', sensor_dict, selected_config, selected_sn)
        self.preamplifier = InstrumentComponent.dynamic_class_constructor('preamplifier', preamplifier_dict, 
                                                                          selected_config, selected_sn) if preamplifier_dict else None 
    
    def __repr__(self):
        s = f'Instrument({self.datalogger}, {self.sensor}'
        if self.preamplifier:
            s += f', {self.preamplifier}'
        s += ')'
        return s
    
    @property
    def equipment_datalogger(self):
        return self.datalogger.equipment
    @property
    def equipment_sensor(self):
        return self.sensor.equipment
    @property
    def equipment_sensor(self):
        return self.preamplifier.equipment
    @property
    def response_stages(self):    
    # Stack response stages
        response_stages = self.sensor.response_stages
        if self.preamplifier:
            response_stages += self.preamplifier.response_stages
        return response_stages + self.datalogger.response_stages
    @property
    def sample_rate(self):    
        return self.datalogger.sample_rate
    @property
    def delay_correction(self):  
        return self.datalogger.delay_correction  
    @property
    def seed_band_base_code(self):    
        return self.sensor.seed_band_base_code
    @property
    def seed_instrument_code(self): 
        return self.sensor.seed_instrument_code   
    @property
    def seed_orientation(self):    
        return self.sensor.seed_orientation

    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create instance from an info_dict

        :param info_dict: information dictionary containing datalogger,
                          sensor, and optionally preamplifier keys
        :type info_dict: InfoDict
        """
       
        assert 'datalogger' in info_dict, 'No datalogger specified'
        assert 'sensor' in info_dict, 'No sensor specified'
        
        
        obj = cls(Datalogger.from_info_dict(info_dict['datalogger']),
                  Sensor.from_info_dict(info_dict['sensor']),
                  Preamplifier.from_info_dict(info_dict.get('preamplifier',
                                                            None)))
        return obj
