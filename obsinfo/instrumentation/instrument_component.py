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

from .response_stages import ResponseStages


class InstrumentComponent(object):
    """
    InstrumentComponent superclass.  No obspy equivalent
    """
    def __init__(self, equipment, response_stages=[],
                 config_description=''):
        """
        Constructor
        """
        self.equipment = equipment
        if config_description:
            self.equipment.description += ('[config: ' + config_description
                                           + ']')
        self.response_stages = response_stages
            
        
    def reconfigure_component(self, key, info_dict, 
                                           instrumentation_selected_config=None, instrumentation_selected_sn=None, 
                                           default=None):
        """
        Completes the component layout.  Layout = configuration or serial number
        There are two types of layout, configuration  and serial numbers.
        In the instrumentation class both can be defined. It may be used to OVERRIDE values of attributes by default or to SELECT
        an existing layout at the component level (by specifying a layout selector). The component class MAY already have a default layout selector
        
        Thus we first check if there is an instrumentation level layout which changes the component level layout. This has absolute priority.
        Afterwards, if there are overrides, they will be processed in the following priority order:
            1) instrument_selected_configuration
            2) instrumentation_selected_serial_number 
            3) component_selected_configuration
            4) component_selected_serial_numbers

        """
        das_value = info_dict.get(key, default)

        instrumentation_selected_config_value = instrumentation_selected_config.get(key, default)
        instrumentation_selected_sn_value = instrumentation_selected_sn.get(key, default)
        #Checks if there is an overriding configuration selector at instrumentation level. If yes, use it to select config at component level
        #If not, use component level selector. If non-existent, don't use layouts.
        #First for configuration
        overriding_config_selector = instrumentation_selected_config.get('configuration_selector', None)
        component_configuration_selector = overriding_config_selector if overriding_config_selector else info_dict.get(
                                                                                       'configuration_selector', None)
        #Same as above, for serial number   
        overriding_sn_selector = instrumentation_selected_config.get('serial_number_selector', None)
        component_sn_selector = overriding_sn_selector if overriding_sn_selector else info_dict.get(
                                                                                        'serial_number_selector', None)
        #Here we select the adequate config value according to both the selector and the key
        if component_config_selector:
            component_all_configs = info_dict.get('configuration_definitions', None)
            component_selected_config = component_all_configs.get(component_config_selector, None)
            component_selected_config_value = component_selected_config(key, default)
        #Here we select the adequate SN value according to both the selector and the key
        if component_sn_selector:
            component_all_sns = info_dict.get('serial_numbers_definitions', None)
            component_selected_sn = component_all_sns.get(component_sn_selector, None)
            component_selected_sn_value = component_selected_sn(key, default)
        
        #Have selected adequate component layout but still need to implement priorities
        #Implement priority 1
        if instrumentation_selected_config_value:
            return instrumentation_selected_config_value  
        #Implement priority 2
        elif instrumentation_selected_sn_value:
            return instrumentation_selected_sn_value
        #Implement priority 3
        elif component_selected_config_value:
            return component_selected_config_value  
        #Implement priority 4
        elif component_selected_sn_value:
            return component_selected_sn_value
        else:
            return info_dict.get(key, default)
        #Implement priority 5
        
        
    def select_actual_component(self, nfo_dict, selected_config, selected_sn):
        pass
        
    @staticmethod
    def dynamic_class_constructor(component_type, info_dict, selected_config, selected_sn):
        """
        Creates an appropriate Instrumnet_component subclass from an info_dict
        """
        if component_type == 'datalogger':
            obj = Datalogger.dynamic_class_constructor(info_dict['datalogger'], selected_config, selected_sn)
        elif 'sample_rate' in info_dict:
            obj = Sensor.dynamic_class_constructor(info_dict, selected_config, selected_sn)
        elif component_type == 'sensor':
            obj = Sensor.dynamic_class_constructor(info_dict['sensor'], selected_config, selected_sn)
        elif 'seed_codes' in info_dict:
            obj = Sensor.dynamic_class_constructor(info_dict, selected_config, selected_sn)
        elif component_type == 'preamplifier':
            obj = Preamplifier.dynamic_class_constructor(info_dict['preamplifier'], selected_config, selected_sn)
        elif 'equipment' in info_dict:
            obj = Preamplifier.dynamic_class_constructor(info_dict, selected_config, selected_sn)
        else:
            warnings.warn('Unknown InstrumentComponent ')
        return obj


class Datalogger(InstrumentComponent):
    """
    Datalogger Instrument Component. No obspy equivalent
    """
    def __init__(self, equipment, sample_rate, response_stages=[],
                 config_description='', delay_correction=0):
        
        self.sample_rate = sample_rate
        self.delay_correction = delay_correction
        super().__init__(equipment, response_stages, config_description)

    @classmethod
    def dynamic_class_constructor(cls, info_dict, selected_config, selected_sn):
        """
        Create Datalogger instance from an info_dict
        """
        if not info_dict:
            return None
        
        select_actual_component(info_dict, selected_config, selected_sn)
        equipment = reconfigure_component('equipment', info_dict, selected_config, selected_sn, None)
        response_stages = reconfigure_component('response_stages', info_dict, selected_config, selected_sn, None)
        sample_rate = reconfigure_component('sample_rate', info_dict, selected_config, selected_sn, None)
        config_description = reconfigure_component('config_description', info_dict, selected_config, selected_sn, '')
        delay_correction = reconfigure_component('delay_correction', info_dict, selected_config, selected_sn, 0)
        
        response_stages = ResponseStages(response_stages)
        
        obj = cls(Equipment.dynamic_class_constructor(equipment),
                  sample_rate,
                  ResponseStages(response_stages),
                  config_descritption,
                  delay_correction)
                  
        return obj

    def __repr__(self):
        s = f'Datalogger({type(self.equipment)}, {self.sample_rate:g}'
        if self.response_stages:
            s += f', {s.description for s in self.response_stages.stages} x Stage'
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
                 config_description='',
                 selected_instrumentation_config=None, selected_instrumentation_sn=None):
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
        :type seed_orientations: dict

        """
        self.equipment = equipment
        if config_description:
            self.equipment.description += ('[config: ' + config_description
                                           + ']')
        self.seed_band_base_code = seed_band_base_code
        self.seed_instrument_code = seed_instrument_code
        self.seed_orientations = seed_orientations  # dictionary
        self.response_stages = response_stages
        super().__init__(selected_config, selected_sn)


    @classmethod
    def dynamic_class_constructor(cls, info_dict, selected_config=None, selected_sn=None):
        """
        Create Sensor instance from an info_dict
        """
        if not info_dict:
            return None
        seed_dict = info_dict.get('seed_codes', {})
        orient_dict = seed_dict.get('orientation', {})
        orients = {key: Orientation(value)
                   for (key, value) in orient_dict.items()}
        response_stages = info_dict.get('response_stages', None)
        obj = cls(Equipment.dynamic_class_constructor(info_dict.get('equipment', None)),
                  seed_dict.get('band_base', None),
                  seed_dict.get('instrument', None),
                  orients,
                  ResponseStages(response_stages),
                  info_dict.get('config_description', ''),
                  selected_config, selected_sn
                  )
        return obj

    def __repr__(self):
        s = 'Sensor({}, "{}", "{}", {}x{}'.format(
            type(self.equipment), self.seed_band_base_code,
            self.seed_instrument_code, len(self.seed_orientations),
            type(self.seed_orientations))
        if self.response_stages:
            s += f', {self.response_stages} x list'
        #if self.config_description:
        #    s += f', config_description={self.config_description}'
        s += ')'
        return s


class Preamplifier(InstrumentComponent):
    """
    Preamplifier Instrument Component. No obspy equivalent
    """
    
    def __init__(self, equipment,  response_stages=[],
                 config_description='',
                 selected_instrumentation_config=None, selected_instrumentation_sn=None):
        """
        Constructor

        :param equipment: Equipment information
        :type equipment: ~class `obsinfo.instrumnetation.Equipment`

        """
        self.equipment = equipment
        if config_description:
            self.equipment.description += ('[config: ' + config_description
                                           + ']')
        self.response_stages = response_stages
        super().__init__(selected_config, selected_sn)

        
    def dynamic_class_constructor(cls, info_dict=None, selected_config=None, selected_sn=None):
        """
        Create Sensor instance from an info_dict
        """
        if not info_dict:
            return None
        response_stages = info_dict.get('response_stages', None)
        obj = cls(Equipment.dynamic_class_constructor(info_dict.get('equipment', None)),
                  ResponseStages(response_stages),
                  info_dict.get('config_description', ''),
                  selected_config, selected_sn
                  )
        return obj

    def __repr__(self):
        s = f'Preamplifier({type(self.equipment)}'
        if self.response_stages:
            s += f', {self.response_stages} x list'
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
                 removal_date=None, calibration_dates=None,
                 selected_config=None, selected_sn=None):
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
        super().__init__(selected_config, selected_sn)

    @classmethod
    def dynamic_class_constructor(cls, info_dict, selected_config=None, selected_sn=None):
        """
        Create Equipment instance from an info_dict
        """
        obj = cls(info_dict.get('type', None),
                  info_dict.get('description', None),
                  info_dict.get('manufacturer', None),
                  info_dict.get('model', None),
                  info_dict.get('vendor', None),
                  info_dict.get('serial_number', None),
                  info_dict.get('calibration_dates', None), 
                  selected_config, selected_sn
                  )
        return obj

    def to_obspy(self):
        return self


class Orientation(object):
    """
    Class for sensor orientations
    """
    def __init__(self, info_dict):
        """
        Constructor

        :param azimuth: azimuth (clockwise from north, degrees)
        :param azimuth_uncertainty: degrees
        :param dip: dip (degrees, -90 to 90: positive=down, negative=up)
        :param dip_uncertainty: degrees
        """
        azimuth, azi_uncert = info_dict.get('azimuth.deg', [None, None])
        dip, dip_uncert = info_dict.get('dip.deg', [None, None])
        self.azimuth = obspy_FloatWithUncertaintiesAndUnit(
            azimuth, lower_uncertainty=azimuth_uncertainty,
            upper_uncertainty=azimuth_uncertainty, unit='degrees')
        self.dip = obspy_FloatWithUncertaintiesAndUnit(
            dip, lower_uncertainty=dip_uncertainty,
            upper_uncertainty=dip_uncertainty, unit='degrees')

    @classmethod
    def dynamic_class_constructor(cls, info_dict):
        """
        Create Orientation instance from an info_dict
        """
        azimuth, azi_uncert = info_dict.get('azimuth.deg', [None, None])
        dip, dip_uncert = info_dict.get('dip.deg', [None, None])  
        obj = cls(azimuth, azi_uncert, dip, dip_uncert)
        return obj
