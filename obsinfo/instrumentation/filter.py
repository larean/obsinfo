"""
Filter class and subclasses
"""
# Standard library modules
# import math as m
import os.path
import pprint

# Non-standard modules
import obspy.core.inventory.response as obspy_response

class Filter():
    """
    Filter superclass
    """
    def __init__(self, type="PolesZeros"):
        """
        Constructor
        """
        self.type=type


class PolesZeros(Filter):
    """
    PolesZeros Filter
    """
    def __init__(self, units='rad/s', poles=[], zeros = [],
                 normalization_frequency=0, normalization_factor=1.):
        self.type = 'PolesZeros'
        self.units = units
        self.poles = poles
        self.zeros = zeros
        self.normalization_frequency = normalization_frequency
        self.normalization_factor = normalization_factor
    
    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create PolesZeros instance from an info_dict
        """
        obj = cls(info_dict.get('units','rad/s'),
                  info_dict.get('poles',[]),
                  info_dict.get('zeros',[]),
                  info_dict.get('normalization_frequency',0.),
                  info_dict.get('normalization_factor',1.))
        return obj


class FIR(Filter):
    """
    FIR Filter
    """
    def __init__(self, symmetry, delay_samples, coefficients,
                 coefficient_divisor):
        self.type = 'FIR'
        self.symmetry = symmetry
        if symmetry not in ['ODD', 'EVEN', 'NONE']:
            warnings.warn(f'Illegal FIR symmetry: "{symmetry}"')
        self.delay_samples = delay_samples
        self.coefficients = coefficients
        self.coefficient_divisor = coefficient_divisor
    
    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create PolesZeros instance from an info_dict
        """
        obj = cls(info_dict.get('symmetry','NONE'),
                  info_dict.get('delay_samples',None),
                  info_dict.get('coefficients',[]),
                  info_dict.get('coefficient_divisor',1.))
        return obj


class Coefficients(Filter):
    """
    Coefficients Filter
    """
    def __init__(self, transfer_function_type, numerator_coefficients,
                 denominator_coefficients):
        if transfer_function_type not in ["ANALOG (RADIANS/SECOND)",
                                          "ANALOG (HERTZ)",
                                          "DIGITAL"]:
            warnings.warn('Illegal transfer function type: "{}"'.format(
                transfer_function_type))
        self.type = 'Coefficients'
        self.transfer_function_type = transfer_function_type
        self.numerator_coefficients = numerator_coefficients
        self.denominator_coefficients = denominator_coefficients
    
    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create PolesZeros instance from an info_dict
        """
        obj = cls(info_dict.get('transfer_function_type','DIGITAL'),
                  info_dict.get('numerator_coefficients',[]),
                  info_dict.get('denominator_coefficients',[]))
        return obj


class ResponseList(Filter):
    """
    ResponseList Filter
    """
    def __init__(self, response_list):
        self.type = 'Coefficients'
        self.response_list = response_list
    
    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create PolesZeros instance from an info_dict
        """
        obj = cls(info_dict.get('response_list',[]))
        return obj


class ANALOG(PolesZeros):
    """
    ANALOG Filter (Flat PolesZeros filter)
    """
    def __init__(self):
        self.type = 'PolesZeros'
        self.units = 'rad/s'
        self.poles = []
        self.zeros = []
        self.normalization_frequency = 0
        self.normalization_factor = 1.
    
    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create AD_CONVERSION instance from an info_dict
        """
        obj = cls()
        return obj


class DIGITAL(Coefficients):
    """
    DIGITAL Filter (Flat Coefficients filter)
    """
    def __init__(self):
        self.type = 'DIGITAL'
        self.transfer_function_type = 'DIGITAL'
        self.numerator_coefficients = [1.0]
        self.denominator_coefficients = []
    
    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create AD_CONVERSION instance from an info_dict
        """
        obj = cls()
        return obj


class AD_CONVERSION(Coefficients):
    """
    AD_CONVERSION Filter (Flat Coefficients filter)
    """
    def __init__(self, input_full_scale, output_full_scale):
        self.type = 'AD_CONVERSION'
        self.transfer_function_type = 'DIGITAL'
        self.numerator_coefficients = [1.0]
        self.denominator_coefficients = []
        self.input_full_scale = input_full_scale
        self.output_full_scale = output_full_scale
    
    @classmethod
    def from_info_dict(cls, info_dict):
        """
        Create AD_CONVERSION instance from an info_dict
        """
        obj = cls(info_dict.get('input_full_scale',None),
                  info_dict.get('output_full_scale',None))
        return obj


