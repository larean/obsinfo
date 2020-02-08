"""
Response Stage class
"""
# Standard library modules
import pprint

# Non-standard modules
import obspy.core.inventory.response as obspy_response

from .filter import Filter

class Stage():
    """
    Stage class
    """
    def __init__(self, name, description, input_units, output_units, gain,
                 gain_frequency, filter, output_sample_rate,
                 decimation_factor=1.,  delay=0., calibration_date=None):
        """
        Constructor
        """
        self.name = name
        self.description = description
        self.input_units = input_units
        self.output_units = output_units
        self.gain = gain
        self.gain_frequency = gain_frequency
        self.filter = filter
        self.output_sample_rate = output_sample_rate
        self.decimation_factor = decimation_factor
        self.delay = delay
        self.calibration_date = calibration_date
        
    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create instance from an info_dict
        """
        gain_dict=info_dict.get('gain',{})
        obj = cls(info_dict.get('description',''),
                  info_dict.get('name',''),
                  info_dict.get('input_units',None),
                  info_dict.get('output_units',None),
                  gain_dict.get('value',1.0),
                  gain_dict.get('frequency',0.0),
                  Filter(info_dict.get('filter',None)),
                  info_dict.get('output_sample_rate',None),
                  info_dict.get('decimation_factor',1),
                  info_dict.get('delay',0),
                  info_dict.get('calibration_date',None)
                  )


    def to_obspy(self,stage_sequence_number=-1, input_sample_rate=None):
        """
        Return equivalent obspy response stage
        """
        if input_sample_rate:
            if not self.output_sample_rate:
                self.output_sample_rate = input_sample_rate
                                          / self.decimation_factor
            if not (input_sample_rate / self.output_sample_rate)
                   == self.decimation_factor:
                warnings.warn('input_sample_rate/output_sample_rate does not'
                              + ' equal decimation_factor')
        if self.output_sample_rate:
            if not input_sample_rate:
                input_sample_rate = (self.output_sample_rate
                                     * self.decimation_factor)
        else:
            warning.warn('no output_sample_rate specified for stage {:d}'.
                format(stage_sequence_number))

        filt=self.filter
        if isinstance(filt,'PolesZeros'):
            obj = PolesZerosResponseStage(
                stage_sequence_number,
                self.gain,
                self.gain_frequency,
                self.input_units,
                self.output_units,
                name=self.name,
                description=self.description,
                # PZ-specific
                pz_transfer_function_type=filt.transfer_function.type,
                normalization_frequency=filt.normalization_frequency,
                zeros=filt.zeros,
                poles=filt.poles,
                normalization_factor=filt.normalization_factor)
        elif isinstance(filt,'FIR'):
            obj = FIRResponseStage(
                stage_sequence_number,
                self.gain,
                self.gain_frequency,
                self.input_units,
                self.output_units,
                decimation_input_sample_rate=input_sample_rate,
                decimation_factor=self.decimation_factor,
                decimation_delay=self.delay,
                name=self.name,
                description=self.description,
                # FIR-specific
                symmetry=filt.symmetry,
                coefficients=filt.coefficients / filt.coefficients_divisor)
        elif isinstance(filt,'Cofficients'):
            obj = CoefficientsTypeResponseStage(
                stage_sequence_number,
                self.gain,
                self.gain_frequency,
                self.input_units,
                self.output_units,
                decimation_input_sample_rate=input_sample_rate,
                decimation_factor=self.decimation_factor,
                decimation_delay=self.delay,
                name=self.name,
                description=self.description,
                # CF-specific
                cf_transfer_function_type=filt.transfer_function_type,
                numerator=filt.numerator,
                denominator=filt.denominator)
        elif isinstance(filt,'ResponseList'):
            obj = ResponseListResponseStage(
                stage_sequence_number,
                self.gain,
                self.gain_frequency,
                self.input_units,
                self.output_units,
                decimation_input_sample_rate=input_sample_rate,
                decimation_factor=self.decimation_factor,
                decimation_delay=self.delay,
                name=self.name,
                description=self.description,
                # ResponeList-specific
                response_list_elements=filt.response_list)
        else:
            warning.warn(f'Unhandled response stage type: "{filt.type}"')        