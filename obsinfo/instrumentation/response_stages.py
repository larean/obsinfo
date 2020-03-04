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


class Response_Stages():
    """
    Reponse_Stages class

    An ordered list of Stages
    """
    def __init__(self, stages):
        self.stages = stages

        # Add stage_sequence numbers to the stages
        for i in range(len(self.stages)):
            self.stages[i].stage_sequence_number = i+1

    def __repr__(self):
        s = f'Response_Stages([{len(self.stages):d}x{type(self.stages[0])}])'
        return s

    def __add__(self, other):
        """
        Add two Response_Stages objects together

        The first object will have its stages before before the second's
        """
        # Verify that the units are compatible
        assert self.stages[-1].output_units == other.stages[0].input_units,\
            "Output units of 1st don't match input_units of 2nd"
        # Verify that the sample rates are compatible
        if self.output_sample_rate() and other.input_sample_rate():
            assert self.output_sample_rate() == other.input_sample_rate(),\
                "first object's outp samp_rate != 2nd objects' inp samp_rate"
        stages = [s for s in self.stages]
        stages.extend(other.stages)

        return Response_Stages(stages)

    def extend(self, other):
        """
        Extend one ResponseStages with another

        Same as __add__
        """
        return self + other

    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create instance from an info_dict

        info_dict is just a list of Stage()s in this case
        """
        obj = cls([Stage.from_info_dict(s) for s in info_dict])
        return obj

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
        print(sensitivity)
        print(obspy_resp)
        obspy_resp.recalculate_overall_sensitivity(sensitivity.frequency)
        obspy_resp.instrument_sensitivity.input_units = true_input_units

        return obspy_resp

    def output_sample_rate(self):
        """
        Return the output sample rate

        based on any defined sample rates and decimation
        """
        sample_rate = None
        for stage in self.stages:
            if stage.decimation_factor:
                if sample_rate:
                    sample_rate /= stage.decimation_factor
            if stage.output_sample_rate:
                if sample_rate:
                    assert sample_rate == stage.output_sample_rate,\
                        "stage sample rate {:g} != expected {:g}".format(
                            stage.output_sample_rate, sample_rate)
                else:
                    sample_rate = stage.output_sample_rate
        return sample_rate

    def input_sample_rate(self):
        """
        Return the input sample rate

        based on any defined sample rates and decimation
        """
        decimation_factor=1
        for stage in self.stages:
            if stage.decimation_factor:
                decimation_factor *= stage.decimation_factor
            if stage.output_sample_rate:
                return stage.output_sample_rate * decimation_factor
        return None


class Stage():
    """
    Stage class
    """
    def __init__(self, name, description, input_units, output_units, gain,
                 gain_frequency, filter, stage_sequence_number=-1,
                 input_units_description=None, output_units_description=None,
                 output_sample_rate=None, decimation_factor=1.,
                 offset=0, delay=0., correction=0., calibration_date=None):
        self.name = name
        self.description = description
        self.input_units = input_units
        self.output_units = output_units
        self.gain = gain
        self.gain_frequency = gain_frequency
        self.filter = filter
        self.stage_sequence_number = stage_sequence_number
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
        if not self.stage_sequence_number == -1:
            s += f', stage_sequence_number="{self.stage_sequence_number}"'
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

    def to_obspy(self):
        """
        Return equivalent obspy response stage
        """
        # if input_sample_rate:
        #    if not self.output_sample_rate:
        #        self.output_sample_rate = (input_sample_rate
        #                                   / self.decimation_factor)
        #    elif not ((input_sample_rate / self.output_sample_rate)
        #              == self.decimation_factor):
        #        warnings.warn('input_sample_rate/output_sample_rate does not'
        #                      + ' equal decimation_factor')
        if self.output_sample_rate:
            input_sample_rate = (self.output_sample_rate
                                 * self.decimation_factor)
        else:
            input_sample_rate = None
        # else:
        #     warnings.warn('no output_sample_rate specified for stage {:d}'.
        #                   format(stage_sequence_number))

        filt = self.filter
        args = (self.stage_sequence_number, self.gain, self.gain_frequency,
                self.input_units, self.output_units)
        if isinstance(filt, PolesZeros) or isinstance(filt, Analog):
            if not filt.normalization_frequency:
                filt.normalization_frequency = self.gain_frequency
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
                decimation_input_sample_rate=input_sample_rate,
                decimation_factor=self.decimation_factor,
                decimation_offset=self.offset,
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
                decimation_input_sample_rate=input_sample_rate,
                decimation_factor=self.decimation_factor,
                decimation_offset=self.offset,
                decimation_delay=self.delay,
                decimation_correction=self.correction,
                # FIR-specific
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
