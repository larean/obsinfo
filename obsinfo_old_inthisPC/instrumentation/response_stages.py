"""
Response Stage class
"""
# Standard library modules
import warnings

# Non-standard modules
from obspy.core.inventory.response import (PolesZerosResponseStage,
                                           FIRResponseStage,
                                           CoefficientsTypeResponseStage,
                                           ResponseListResponseStage)
from obspy.core.inventory.response import Response as obspy_Response
from obspy.core.inventory.response import InstrumentSensitivity\
                                   as obspy_Sensitivity
import obspy.core.util.obspy_types as obspy_types

# Local modules
from .filter import (Filter, PolesZeros, FIR, Coefficients, ResponseList,
                     Analog, Digital, AD_Conversion)


class ResponseStages():
    """
    ReponseStages class

    An ordered list of Stages
    """
    def __init__(self, info_dict, delay_correction={'apply': False, 'value': 0}):
        
        self.stages = [Stage(s, delay_correction) for s in info_dict]
        if delay_correction['apply']: #Apply correction only to last stage making it a GLOBAL correction, all others are zero
            self.stages[len(self.stages)-1] == delay_correction['value']
        self._assure_continuity()

    def __repr__(self):
        s = f'Response_Stages([{len(self.stages):d}x{type(self.stages[0])}])'
        return s

    def _assure_continuity(self):
        """
        Number stages sequentially and verify/set units and sample rates
        """
        # Order the stage_sequence_numbers
        for i in range(len(self.stages)):
            self.stages[i].stage_sequence_number = i+1

        stage = self.stages[0]

        for next_stage in self.stages[1:]:
            # Verify continuity of units
            assert stage.output_units == next_stage.input_units,\
                "Stage {:d} and {:d} units don't match".format(
                    stage.stage_sequence_number,
                    next_stage.stage_sequence_number)
            # Verify continuity of sample rate
            if stage.output_sample_rate:
                assert next_stage.decimation_factor,\
                    'No decimation_rate for stage {:d}'.format(
                        next_stage.stage_sequence_number)
                next_input_rate = (stage.output_sample_rate
                             / next_stage.decimation_factor)
                if next_stage.output_sample_rate:
                    assert next_stage.output_sample_rate == next_rate,\
                        'stage {:d} sample rate ({:g}) != expected ({:g})'.\
                            format(next_stage.stage_sequence_number,
                                   next_stage.output_sample_rate,
                                   next_rate)
                else:
                    next_stage.output_sample_rate = next_input_rate
            stage = next_stage

    
    def to_obspy(self):
        """
        Return equivalent obspy response class
        """
        obj = obspy_Response(response_stages=[s.to_obspy()
                                              for s in self.stages])
        obj = self._add_sensitivity(obj)
        
        return obj

    def _add_sensitivity(self, obspy_resp):
        """
        Adds sensitivity to an obspy Response object

        Based on ..misc.obspy_routines.response_with_sensitivity
        """

        input_units = self.stages[0].input_units
        true_input_units = self.stages[0].input_units
        if "PA" in true_input_units.upper():
            # MAKE OBSPY THINK ITS M/S TO CORRECTLY CALCULATE SENSITIVITY
            input_units = "M/S"
        gain_prod = 1.
        for stage in self.stages:
            gain_prod *= stage.gain
            
        sensitivity = obspy_Sensitivity(
            gain_prod,
            self.stages[0].gain_frequency,
            input_units=input_units,
            output_units=self.stages[-1].output_units,
            input_units_description=self.stages[0].input_units_description,
            output_units_description=self.stages[-1].output_units_description
            )
        
        obspy_resp.instrument_sensitivity = sensitivity
        obspy_resp.recalculate_overall_sensitivity(sensitivity.frequency)
        obspy_resp.instrument_sensitivity.input_units = true_input_units

        return obspy_resp


class Stage():
    """
    Stage class
    """
    def __init__(self, info_dict, delay_correc):
        self.name = info_dict.get('name', '')
        self.description = info_dict.get('description', '')
        self.input_units = info_dict.get('input_units', None).get('name', None)
        self.output_units = info_dict.get('output_units', None).get('name', None)
        gain_dict = info_dict.get('gain', {})
        self.gain = gain_dict.get('value', 1.0)             
        self.gain_frequency = gain_dict.get('frequency', 0.0)
        self.filter = Filter.dynamic_class_constructor(info_dict.get('filter', None), apply_correc)
        self.stage_sequence_number = -1
        self.input_units_description = input_units_description=info_dict.get(
                    'input_units', None).get('description', None)
        self.output_units_description = output_units_description=info_dict.get(
                    'output_units', None).get('description', None)
        self.input_sample_rate = info_dict.get('input_sample_rate', None)
        self.delay = info_dict.get('delay', None)
        self.decimation_factor = info_dict.get('decimation_factor', 1)
        
        if self.decimation_factor < self.filter.offset:
            warnings.warn(f'Offset too large for decimation factor: "{self.filter.offset}"')
        else:    
            self.calculate_delay(self.delay, self.filter.offset, delay_correc, self.input_sample_rate)
        
        self.calibration_date = info_dict.get('calibration_date', None)
                        
                  
    @property
    def output_sample_rate(self):
        if self.input_sample_rate and self.decimation_factor:
            return self.input_sample_rate / self.decimation_factor
        else:
            return None

    def calculate_delay(self, delay, offset, correction, input_sample_rate):
        """
        Calculates delay as a function of object for digital filters if delay not specified
        Otherwise, uses delay as passed in the arguments
        Also applies correction in the following way:
            - correction is a dict with two keys, "apply" and "value".
            - If apply == False, correction is not applied and delay values stay the same
            - If apply == True, correction is applied but only to the last stage, and this is
              done elsewhere (in Response_stages). All other delays are set to zero, so 
              "correction" is a GLOBAL correction as opposed to StationXML, where stage-level
              corrections are allowed.
        """
        
        if delay == None:
            self.delay = offset / input_sample_rate if offset != None else 0
        else:
            self.delay = delay
            
        if correction['apply']:
            self.delay = 0 

    def __repr__(self):
        s = f'Stage("{self.name}", "{self.description}", '
        s += f'"{self.input_units}", "{self.output_units}", '
        s += f'{self.gain:g}, {self.gain_frequency:g}, '
        s += f'{type(self.filter)}'
        if not self.stage_sequence_number == -1:
            s += f', stage_sequence_number="{self.stage_sequence_number}"'
        if self.input_units_description:
            s += f', input_units_description="{self.input_units_description}"'
        if self.output_units_description:
            s += f', output_units_description='
            s += f'"{self.output_units_description}"'
        if self.input_sample_rate:
            s += f', input_sample_rate={self.input_sample_rate:g}'
        if not self.decimation_factor == 1.:
            s += f', decimation_factor={self.decimation_factor:g}'
        if not self.delay == 0.:
            s += f', {self.delay:g}'
        if self.calibration_date:
            s += f', delay={self.calibration_date}'
        s += ')'
        return s


    def to_obspy(self):
        """
        Return equivalent obspy response stage
        """

        filt = self.filter
        args = (self.stage_sequence_number, self.gain, self.gain_frequency,
                self.input_units, self.output_units)
        if (isinstance(filt, PolesZeros) 
                or isinstance(filt, Analog)):
            if not filt.normalization_frequency:
                filt.normalization_frequency = self.gain_frequency
            obj = PolesZerosResponseStage(
                *args,
                name=self.name,
                input_units_description=self.input_units_description,
                output_units_description=self.output_units_description,
                description=self.description,
                decimation_input_sample_rate=self.input_sample_rate,
                decimation_factor=self.decimation_factor,
                decimation_offset=filt.offset,
                decimation_delay=self.delay,
                decimation_correction=self.correction,
                #OJO: check if correction and delay should be modified
                # PolesZeros-specific
                pz_transfer_function_type=filt.transfer_function_type,
                normalization_frequency=filt.normalization_frequency,
                zeros=[obspy_types.ComplexWithUncertainties(
                    t, lower_uncertainty=0.0, upper_uncertainty=0.0)\
                    for t in filt.zeros],
                poles=[obspy_types.ComplexWithUncertainties(
                    t, lower_uncertainty=0.0, upper_uncertainty=0.0)\
                    for t in filt.poles],
                normalization_factor=filt.calc_normalization_factor())
        elif isinstance(filt, FIR):
            obj = FIRResponseStage(
                *args,
                name=self.name,
                input_units_description=self.input_units_description,
                output_units_description=self.output_units_description,
                description=self.description,
                decimation_input_sample_rate=self.input_sample_rate,
                decimation_factor=self.decimation_factor,
                decimation_offset=filt.offset,
                decimation_delay=self.delay,
                decimation_correction=self.correction,
                # FIR-specific
                symmetry=filt.symmetry,
                coefficients=[obspy_types.FloatWithUncertaintiesAndUnit(
                    c / filt.coefficient_divisor)
                              for c in filt.coefficients])
        elif (isinstance(filt, Coefficients)
                or isinstance(filt, Digital)
                or isinstance(filt, AD_Conversion)):
            obj = CoefficientsTypeResponseStage(
                *args,
                name=self.name,
                input_units_description=self.input_units_description,
                output_units_description=self.output_units_description,
                description=self.description,
                decimation_input_sample_rate=self.input_sample_rate,
                decimation_factor=self.decimation_factor,
                decimation_offset=filt.offset,
                decimation_delay=self.delay,
                decimation_correction=self.correction,
                # CF-specific
                cf_transfer_function_type=filt.transfer_function_type,
                numerator=[obspy_types.FloatWithUncertaintiesAndUnit(
                    n, lower_uncertainty=0.0, upper_uncertainty=0.0)\
                    for n in filt.numerator_coefficients],
                denominator=[obspy_types.FloatWithUncertaintiesAndUnit(
                    n, lower_uncertainty=0.0, upper_uncertainty=0.0)\
                    for n in filt.denominator_coefficients])
        elif isinstance(filt, ResponseList):
            obj = ResponseListResponseStage(
                *args,
                name=self.name,
                input_units_description=self.input_units_description,
                output_units_description=self.output_units_description,
                description=self.description,
                decimation_input_sample_rate=self.input_sample_rate,
                decimation_factor=self.decimation_factor,
                decimation_offset=filt.offset,
                decimation_delay=self.delay,
                decimation_correction=self.correction,
                # ResponeList-specific
                response_list_elements=filt.response_list)
        else:
            warnings.warn(f'Unhandled response stage type: "{filt.type}"')
        
        return obj
