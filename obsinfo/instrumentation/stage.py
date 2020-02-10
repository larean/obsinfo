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

# Local modules
from .filter import (Filter, PolesZeros, FIR, Coefficients, ResponseList,
                     Analog, Digital, AD_Conversion)


class Stage():
    """
    Stage class
    """
    def __init__(self, name, description, input_units, output_units, gain,
                 gain_frequency, filter, input_units_description=None,
                 output_units_description=None,
                 output_sample_rate=None, decimation_factor=1.,
                 offset=0, delay=0., correction=0., calibration_date=None):
        self.name = name
        self.description = description
        self.input_units = input_units
        self.output_units = output_units
        self.gain = gain
        self.gain_frequency = gain_frequency
        self.filter = filter
        self.input_units_description = input_units_description
        self.output_units_description = output_units_description
        self.output_sample_rate = output_sample_rate
        self.decimation_factor = decimation_factor
        self.offset = offset
        self.delay = delay
        self.correction = correction
        self.calibration_date = calibration_date

    def __repr__(self):
        s = f'Stage("{self.name}", "{self.description}", '
        s += f'"{self.input_units}", "{self.output_units}", '
        s += f'{self.gain:g}, {self.gain_frequency:g}, '
        s += f'{type(self.filter)}'
        if self.input_units_description:
            s += f', input_units_description="{self.input_units_description}"'
        if self.output_units_description:
            s += f', output_units_description='
            s += f'"{self.output_units_description}"'
        if self.output_sample_rate:
            s += f', output_sample_rate={self.output_sample_rate:g}'
        if not self.decimation_factor == 1.:
            s += f', decimation_factor={self.decimation_factor:g}'
        if not self.delay == 0.:
            s += f', {self.delay:g}'
        if self.calibration_date:
            s += f', delay={self.calibration_date}'
        s += ')'
        return s

    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create instance from an info_dict
        """
        gain_dict = info_dict.get('gain', {})
        obj = cls(info_dict.get('description', ''),
                  info_dict.get('name', ''),
                  info_dict.get('input_units', None).get('name', None),
                  info_dict.get('output_units', None).get('name', None),
                  gain_dict.get('value', 1.0),
                  gain_dict.get('frequency', 0.0),
                  Filter.from_info_dict(info_dict.get('filter', None)),
                  input_units_description=info_dict.get(
                    'input_units', None).get('description', None),
                  output_units_description=info_dict.get(
                    'output_units', None).get('description', None),
                  output_sample_rate=info_dict.get('output_sample_rate', None),
                  decimation_factor=info_dict.get('decimation_factor', 1),
                  delay=info_dict.get('delay', 0),
                  calibration_date=info_dict.get('calibration_date', None)
                  )
        return obj

    def to_obspy(self, stage_sequence_number=-1, input_sample_rate=None):
        """
        Return equivalent obspy response stage
        """
        if input_sample_rate:
            if not self.output_sample_rate:
                self.output_sample_rate = (input_sample_rate
                                           / self.decimation_factor)
            elif not ((input_sample_rate / self.output_sample_rate)
                      == self.decimation_factor):
                warnings.warn('input_sample_rate/output_sample_rate does not'
                              + ' equal decimation_factor')
        if self.output_sample_rate:
            if not input_sample_rate:
                input_sample_rate = (self.output_sample_rate
                                     * self.decimation_factor)
        else:
            warnings.warn('no output_sample_rate specified for stage {:d}'.
                          format(stage_sequence_number))

        filt = self.filter
        args=(stage_sequence_number, self.gain, self.gain_frequency,
              self.input_units, self.output_units)
        if isinstance(filt, PolesZeros) or isinstance(filt, Analog):
            obj = PolesZerosResponseStage(
                *args,
                name=self.name,
                input_units_description=self.input_units_description,
                output_units_description=self.output_units_description,
                description=self.description,
                decimation_input_sample_rate=input_sample_rate,
                decimation_factor=self.decimation_factor,
                decimation_offset=self.offset,
                decimation_delay=self.delay,
                decimation_correction=self.correction,
                # PolesZeros-specific
                pz_transfer_function_type=filt.transfer_function.type,
                normalization_frequency=filt.normalization_frequency,
                zeros=filt.zeros,
                poles=filt.poles,
                normalization_factor=filt.normalization_factor)
        elif isinstance(filt, FIR):
            obj = FIRResponseStage(
                *args,
                name=self.name,
                input_units_description=self.input_units_description,
                output_units_description=self.output_units_description,
                description=self.description,
                decimation_input_sample_rate=input_sample_rate,
                decimation_factor=self.decimation_factor,
                decimation_offset=self.offset,
                decimation_delay=self.delay,
                decimation_correction=self.correction,
                # FIR-specific
                symmetry=filt.symmetry,
                coefficients=[c / filt.coefficient_divisor
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
                decimation_input_sample_rate=input_sample_rate,
                decimation_factor=self.decimation_factor,
                decimation_offset=self.offset,
                decimation_delay=self.delay,
                decimation_correction=self.correction,
                # FIR-specific
                # CF-specific
                cf_transfer_function_type=filt.transfer_function_type,
                numerator=filt.numerator,
                denominator=filt.denominator)
        elif isinstance(filt, ResponseList):
            obj = ResponseListResponseStage(
                *args,
                name=self.name,
                input_units_description=self.input_units_description,
                output_units_description=self.output_units_description,
                description=self.description,
                decimation_input_sample_rate=input_sample_rate,
                decimation_factor=self.decimation_factor,
                decimation_offset=self.offset,
                decimation_delay=self.delay,
                decimation_correction=self.correction,
                # ResponeList-specific
                response_list_elements=filt.response_list)
        else:
            warnings.warn(f'Unhandled response stage type: "{filt.type}"')
        return obj
