"""
Response class
"""
# Standard library modules
# import warnings

# Non-standard modules
from obspy.core.inventory.response import Response as obspy_Response
from obspy.core.inventory.response import InstrumentSensitivity as obspy_Sensitivity

# Local modules
from .stage import Stage


class Response():
    """
    Reponse class

    Just an ordered list of Stages, plus decimation info
    """
    def __init__(self, stages, input_sample_rate=0, output_sample_rate=0,
                 input_units=None, output_units=None,
                 input_units_description=None, output_units_description=None):
        self.stages = stages
        self.input_sample_rate = input_sample_rate
        self.output_sample_rate = output_sample_rate
        self.input_units = input_units
        self.output_units = output_units
        self.input_units_description = input_units
        self.output_units_description = output_units

        # Add stage_sequence numbers to the stages
        for i in range(len(self.stages)):
            self.stages[i].stage_sequence_number = i+1

        # If there is an input_sample_rate and/or output_sample_rate,
        # add them to the stages and verify
        if self.input_sample_rate:
            in_sr = input_sample_rate
            for stage in self.stages:
                stage.output_sample_rate = in_sr / stage.decimation_factor
                in_sr = stage.output_sample_rate
            if self.output_sample_rate:
                assert self.output_sample_rate == in_sr,\
                    'Incompatible input and output sample rates'
            else:
                self.output_sample_rate = in_sr
        elif self.output_sample_rate:
            out_sr = self.output_sample_rate
            for stage in reversed(self.stages):  # Go backwards
                stage.output_sample_rate = out_sr
                out_sr *= stage.decimation_factor
            self.input_sr = out_sr

    def __repr__(self):
        in_order = True
        s = f'Response([{len(self.stages):d}x{type(self.stages[0])}]'
        if self.input_sample_rate:
            s += f', {self.input_sample_rate:g}'
        else:
            in_order = False
        if self.output_sample_rate:
            s += _add_str('output_sample_rate',
                          f'{self.output_sample_rate:g}',
                          in_order)
        else:
            in_order = False
        if self.input_units:
            s += _add_str('input_units', f'"{self.input_units}"', in_order)
        else:
            in_order = False
        if self.output_units:
            s += _add_str('output_units', f'"{self.output_units}"', in_order)
        else:
            in_order = False
        if self.input_units_description:
            s += _add_str('input_units_description',
                          f'"{self.input_units_description}"', in_order)
        else:
            in_order = False
        if self.output_units_description:
            s += _add_str('output_units_description',
                          f'"{self.output_units_description}"', in_order)
        else:
            in_order = False
        s += ')'
        return s

    def __add__(self, other):
        """
        Add two Response objects together

        The first object will have its stages before before the second's
        """
        # Verify that the input and output units are compatible
        # Verify that the sample rates are compatible
        stages = [s for s in self.stages]
        stages.extend(other.stages)
        
        input_sample_rate = self.input_sample_rate
        if self.output_sample_rate and other.input_sample_rate:
            assert self.output_sample_rate == other.input_sample_rate,\
                "Response objects' sample rates are incompatible"
        if other.output_sample_rate:
            output_sample_rate = other.output_sample_rate
        
        assert self.output_units == other.input_units,\
            "Output units of 1st don't match input_units of 2nd"
        
        return Response(stages, input_sample_rate, output_sample_rate,
                        self.input_units, other.output_units,
                        self.input_units_description,
                        other.output_units_description)

    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create instance from an info_dict
        """
        stages = info_dict.get('stages', [])
        decim_info = info_dict.get('decimation_info', {})
        obj = cls([Stage.from_info_dict(s) for s in stages],
                  decim_info.get('input_sample_rate', 0.),
                  decim_info.get('output_sample_rate', 0.),
                  decim_info.get('input_units', {}).get('name', None),
                  decim_info.get('output_units', {}).get('name', None),
                  decim_info.get('input_units', {}).get('description', None),
                  decim_info.get('output_units', {}).get('description', None)
                  )
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
        gain_prod=1.
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


def _add_str(title, fstring, in_order):
    if in_order:
        return ', ' + fstring
    else:
        return ', ' + title + '=' + fstring
