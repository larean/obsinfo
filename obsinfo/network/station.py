"""
Station class
"""
# Standard library modules

# Non-standard modules

# obsinfo modules
from ..instrumentation import (Instrumentation)


class Station(object):
    """
    Station. Equivalent to obspy/StationXML Station
    """
    def __init__(self, site, start_date, end_date, location_code,
                 locations, instruments, processing=None,
                 restricted_status='unknown'):
        """
        Constructor
        
        :param site: site description
        :kind site: str
        :param start_date: station start date
        :kind start_date: str
        :param end_date: station start date
        :kind end_date: str
        :param location_code: station location code (2 digits)
        :kind location_code: str
        :param locations: locations (names and positions)
        :kind locations: ~class `obsinfo.network.Locations`
        :param instruments: list of Instrumentation
        :kind instruments: list
        :param processing: processing steps
        :kind processing: dict (maybe should have class?)
        :param restricted_status: "open", "closed", "partial", or "unknown"
        :kind restricted_status: str
        
        """
        self.site = site
        self.start_date = start_date
        self.end_date = end_date
        self.location_code = location_code
        self.locations = locations
        self.instruments = instrument_list
        self.processing = processing
        self.restricted_status = restricted_status

    def __repr__(self):
        s = f'Station({self.site}, {self.start_date}, {self.end_date}, '
        s += f'{self.location_code}, {len(self.locations)} {type(Location}s, '
        s += f'{len(self.instruments)} {type(Instrumentation}s'
        if self.processing:
            s += f', {len(self.processing)} processing-steps'
        if not self.restricted_stations == "unknown":
            s += f', {self.restricted_status}'
        s += ')'
        return s

    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create Station instance from an info_dict
        """
        info_dict.complete_das_channels()
        info_das = info_dict.get('das_channels', {})
        obj = cls(info_dict['site'],
                  info_dict['start_date'],
                  info_dict['end_date'],
                  info_dict['location_code'],
                  Locations.from_info_dict(info_dict['locations']),
                  [Instruments.from_info_dict(i)
                    for i in info_dict['instruments']],
                  Processing.from_info_dict(info_dict.get('processing',None)),
                  info_dict.get('restricted_status', None)
                  )
                  [Instrument.from_info_dict(k, v)
                   for k, v in info_das.items()])
        return obj

    def to_obspy(self):


class Locations(object):
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
        self.responses_ordered = sensor.responses_ordered
        if preamplifier:
            self.responses_ordered.extend(preamplifier.responses_ordered)
        self.responses_ordered.extend(datalogger.responses_ordered)

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
