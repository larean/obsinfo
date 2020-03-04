"""
Instrumentation and Instrument classes

nomenclature:
    An "Instrument" (measurement instrument) records one physical parameter
    An "Instrumentation" combines one or more measurement instruments
"""
# Standard library modules

# Non-standard modules

# obsinfo modules
from .instrument_component import (Datalogger, Sensor, Preamplifier,
                                   Equipment, InstrumentComponent)


class Instrumentation(object):
    """
    One or more Instruments. Part of an obspy/StationXML Station
    """
    def __init__(self, equipment, channels):
        """
        Constructor
        """
        self.equipment = equipment
        self.channels = channels

    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create Instrumentation instance from an info_dict
        """
        info_dict.complete_das_channels()
        info_das = info_dict.get('das_channels', {})
        obj = cls(Equipment.from_info_dict(info_dict.get('equipment', None)),
                  [Instrument.from_info_dict(k, v)
                   for k, v in info_das.items()])
        return obj

    def __repr__(self):
        s = f'Instrumentation({type(self.equipment)}, '
        s += f'{len(self.channels)} {type(self.channels[0])}'
        return s


class Instrument(object):
    """
    Instrument Class.

    Corresponds to StationXML/obspy Channel without location or start/end date
    """
    def __init__(self, das_channel, datalogger, sensor, orientation_code,
                 preamplifier=None):
        self.das_channel = das_channel
        self.equipment_datalogger = datalogger.equipment
        if preamplifier:
            self.equipment_preamplifier = preamplifier.equipment
        else:
            self.equipment_preamplifier = None
        self.equipement_sensor = sensor.equipment
        self.sample_rate = datalogger.sample_rate
        self.delay_correction = datalogger.delay_correction
        self.channel_code = _make_channel_code(self.sample_rate,
                                               sensor.seed_band_base_code,
                                               sensor.seed_instrument_code,
                                               orientation_code)
        self.orientation = sensor.seed_orientations[orientation_code]
        # Stack sensor, preamplifier and datalogger response stages
        self.response_stages = sensor.response_stages
        if preamplifier:
            self.response_stages.extend(preamplifier.response_stages)
        self.response_stages.extend(datalogger.response_stages)

    def __repr__(self):
        s = f'Instrument({self.datalogger}, {self.sensor}, '
        s += f'"{self.orientation_code}"'
        if self.preamplifier:
            s += f', {self.preamplifier}'
        s += ')'
        return s

    @classmethod
    def from_info_dict(cls, das_channel, info_dict):
        """
        Create instance from an info_dict

        :param das_channel: das channel name
        :type das_channel: str
        :param info_dict: information dictionary at das_channels:{das_channel}
                          level
        :type info_dict: dict
        """
        assert 'datalogger' in info_dict, 'No datalogger in instrumentation'
        assert 'sensor' in info_dict, 'No sensor in instrumentation'
        assert 'orientation_code' in info_dict,\
            'No orientation_code in instrumentation'
        if 'preamplifer' in info_dict:
            obj = cls(das_channel,
                      Datalogger.from_info_dict(info_dict['datalogger']),
                      Sensor.from_info_dict(info_dict['sensor']),
                      info_dict['orientation_code'],
                      Preamplifier.from_info_dict(info_dict['preamplifier'])
                      )
        else:
            obj = cls(das_channel,
                      Datalogger.from_info_dict(info_dict['datalogger']),
                      Sensor.from_info_dict(info_dict['sensor']),
                      info_dict['orientation_code']
                      )
        return obj


def _make_channel_code(sample_rate, band_base_code, instrument_code,
                       orientation_code):
    """
    Make a channel code from base_code and sample rate

    :param sample_rate: sample rate (sps)
    :param band_base_code: "B" (broadband) or "S" (short period)
    :param instrument code: instrument code
    :param orientation code: orientation code
    """
    assert len(band_base_code) == 1,\
        f'Band code "{band_base_code}" is not a single letter'
    assert len(instrument_code) == 1,\
        f'Instrument code "{instrument_code}" is not a single letter'
    assert len(orientation_code) == 1,\
        f'Orientation code "{orientation_code}" is not a single letter'
    if band_base_code in "FCHBMLVURPTQ":
        if sample_rate >= 1000:
            band_code = "F"
        elif sample_rate >= 250:
            band_code = "C"
        elif sample_rate >= 80:
            band_code = "H"
        elif sample_rate >= 10:
            band_code = "B"
        elif sample_rate > 1:
            band_code = "M"
        elif sample_rate > 0.3:
            band_code = "L"
        elif sample_rate > 0.03:
            band_code = "V"
        elif sample_rate > 0.003:
            band_code = "U"
        elif sample_rate >= 0.0001:
            band_code = "R"
        elif sample_rate >= 0.00001:
            band_code = "P"
        elif sample_rate >= 0.000001:
            band_code = "T"
        else:
            band_code = "Q"
    elif band_base_code in "GDES":
        if sample_rate >= 1000:
            band_code = "G"
        elif sample_rate >= 250:
            band_code = "D"
        elif sample_rate >= 80:
            band_code = "E"
        elif sample_rate >= 10:
            band_code = "S"
        else:
            raise ValueError("Short period instrument sample rate < 10 sps")
    else:
        raise NameError("Unknown band base code: {}".format(band_base_code))
    return band_code + instrument_code + orientation_code
