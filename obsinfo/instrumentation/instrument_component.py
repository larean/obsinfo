"""
InstrumentComponent class and subclasses.

No StationXML equivalent.
"""
# Standard library modules
# import math as m
import warnings

# Non-standard modules
from obspy.core.inventory.util import Equipment as obspy_Equipment
from obspy.core.util.obspy_types import FloatWithUncertaintiesAndUnit as\
    obspy_FloatWithUncertaintiesAndUnit

from .response_stages import Response_Stages


class InstrumentComponent(object):
    """
    InstrumentComponent superclass.  No obspy equivalent
    """
    def __init__(self, equipment, response_stages=[],
                 config_description=''):
        """
        Constructor
        """
        self.equipement = equipment
        if config_description:
            self.equipment.description += ('[config: ' + config_description
                                           + ']')
        self.response_stages = response_stages

    @staticmethod
    def from_info_dict(info_dict):
        """
        Creates an appropriate Instrumnet_component subclass from an info_dict
        """
        if 'datalogger' in info_dict:
            obj = Datalogger.from_info_dict(info_dict['datalogger'])
        elif 'sample_rate' in info_dict:
            obj = Sensor.from_info_dict(info_dict)
        elif 'sensor' in info_dict:
            obj = Sensor.from_info_dict(info_dict['sensor'])
        elif 'seed_codes' in info_dict:
            obj = Sensor.from_info_dict(info_dict)
        elif 'preamplifier' in info_dict:
            obj = Preamplifier.from_info_dict(info_dict['preamplifier'])
        elif 'equipment' in info_dict:
            obj = Preamplifier.from_info_dict(info_dict)
        else:
            warnings.warn('Unknown InstrumentComponent: '
                          f'"{info_dict}"')
        return obj


class Datalogger(InstrumentComponent):
    """
    Datalogger Instrument Component. No obspy equivalent
    """
    def __init__(self, equipment, sample_rate, response_stages=[],
                 config_description='', delay_correction=0):
        self.equipment = equipment
        if config_description:
            self._config_description = config_description
            self.equipment.description += ('[config: ' + config_description
                                           + ']')
        self.sample_rate = sample_rate
        self.response_stages = response_stages
        self.delay_correction = delay_correction

    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create Datalogger instance from an info_dict
        """
        if not info_dict:
            return None
        equipment = info_dict.get('equipment', None)
        response_stages = info_dict.get('response_stages', None)
        obj = cls(Equipment.from_info_dict(equipment),
                  info_dict.get('sample_rate', None),
                  Response_Stages.from_info_dict(response_stages),
                  info_dict.get('config_description', ''),
                  info_dict.get('delay_correction', 0))
        # print(obj)
        return obj

    def __repr__(self):
        s = f'Datalogger({type(self.equipment)}, {self.sample_rate:g}'
        if self.response_stages:
            s += f', {len(self.response_stages):d} x Stage'
        if self._config_description:
            s += f', config_description="{self._config_description}"'
        if self.delay_correction:
            s += f', delay_correction={self.delay_correction:g}'
        s += ')'
        return s


class Sensor(InstrumentComponent):
    """
    Sensor Instrument Component. No obspy equivalent
    """
    def __init__(self, equipment, seed_band_base_code, seed_instrument_code,
                 seed_orientations, response_stages=[],
                 config_description=''):
        """
        Constructor

        :param equipment: Equipment information
        :type equipment: ~class `obsinfo.instrumnetation.Equipment`
        :param seed_band_base_code: SEED base code ("B" or "S") indicating
                                    instrument band.  Must be modified by
                                    obsinfo to correspond to output sample
                                    rate
        :type seed_band_base_code: str (len 1)
        :param seed_instrument code: SEED instrument code
        :type seed_instrument_code: str (len 1)
        :param seed_orientations: SEED orientation codes and corresponding
                                      azimuths and dips
        :type seed_orientation: dict

        """
        self.equipment = equipment
        if config_description:
            self.equipment.description += ('[config: ' + config_description
                                           + ']')
        self.seed_band_base_code = seed_band_base_code
        self.seed_instrument_code = seed_instrument_code
        self.seed_orientations = seed_orientations  # dictionary
        self.response_stages = response_stages

    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create Sensor instance from an info_dict
        """
        if not info_dict:
            return None
        seed_dict = info_dict.get('seed_codes', {})
        orient_dict = seed_dict.get('orientation', {})
        orients = {key: Orientation.from_info_dict(value)
                   for (key, value) in orient_dict.items()}
        response_stages = info_dict.get('response_stages', None)
        obj = cls(Equipment.from_info_dict(info_dict.get('equipment', None)),
                  seed_dict.get('band_base', None),
                  seed_dict.get('instrument', None),
                  orients,
                  Response_Stages.from_info_dict(response_stages),
                  info_dict.get('config_description', '')
                  )
        return obj

    def __repr__(self):
        s = 'Datalogger({}, "{}", "{}", {}x{}'.format(
            type(self.equipment), self.seed_band_base_code,
            self.seed_instrument_code, len(self.seed_orientations),
            type(self.seed_orientations))
        if self.response_stages:
            s += f', {len(self.response_stages):d} x list'
        if self.config_description:
            s += f', config_description={self.config_description}'
        s += ')'
        return s


class Preamplifier(InstrumentComponent):
    """
    Preamplifier Instrument Component. No obspy equivalent
    """
    def from_info_dict(cls, info_dict):
        """
        Create Sensor instance from an info_dict
        """
        if not info_dict:
            return None
        response_stages = info_dict.get('response_stages', None)
        obj = cls(Equipment.from_info_dict(info_dict.get('equipment', None)),
                  Response_Stages.from_info_dict(response_stages),
                  info_dict.get('config_description', '')
                  )
        return obj

    def __repr__(self):
        s = f'Preamplifier({type(self.equipment)}'
        if self.response_stages:
            s += f', {len(self.response_stages):d}xlist'
        if self.config_description:
            s += f', config_description={self.config_description}'
        s += ')'
        return s


class Equipment(obspy_Equipment):
    """
    Equipment class.

    Equivalent to obspy.core.inventory.util.Equipment
    """
    def __init__(self, type, description, manufacturer, model,
                 vendor=None, serial_number=None, installation_date=None,
                 removal_date=None, calibration_dates=None):
        self.type = type
        self.description = description
        self.manufacturer = manufacturer
        self.model = model
        self.vendor = vendor
        self.serial_number = serial_number
        self.installation_date = installation_date
        self.removal_date = removal_date
        self.calibration_dates = calibration_dates or []
        self.resource_id = None

    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create Equipment instance from an info_dict
        """
        obj = cls(info_dict.get('type', None),
                  info_dict.get('description', None),
                  info_dict.get('manufacturer', None),
                  info_dict.get('model', None),
                  info_dict.get('vendor', None),
                  info_dict.get('serial_number', None),
                  calibration_dates=info_dict.get('calibration_dates', None)
                  )
        return obj

    def to_obspy(self):
        return self


class Orientation(object):
    """
    Class for sensor orientations
    """
    def __init__(self, azimuth, azimuth_uncertainty, dip, dip_uncertainty):
        """
        Constructor

        :param azimuth: azimuth (clockwise from north, degrees)
        :param azimuth_uncertainty: degrees
        :param dip: dip (degrees, -90 to 90: positive=down, negative=up)
        :param dip_uncertainty: degrees
        """
        self.azimuth = obspy_FloatWithUncertaintiesAndUnit(
            azimuth, lower_uncertainty=azimuth_uncertainty,
            upper_uncertainty=azimuth_uncertainty, unit='degrees')
        self.dip = obspy_FloatWithUncertaintiesAndUnit(
            dip, lower_uncertainty=dip_uncertainty,
            upper_uncertainty=dip_uncertainty, unit='degrees')

    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create Orientation instance from an info_dict
        """
        azimuth, azi_uncert = info_dict.get('azimuth.deg', [None, None])
        dip, dip_uncert = info_dict.get('dip.deg', [None, None])
        obj = cls(azimuth, azi_uncert, dip, dip_uncert)
        return obj
