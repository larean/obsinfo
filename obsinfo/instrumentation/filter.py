"""
Filter class and subclasses
"""
# Standard library modules
import math as m
import warnings

# Non-standard modules
# import obspy.core.inventory.response as obspy_response


class Filter(object):
    """
    Filter superclass
    """
    def __init__(self, type="PolesZeros"):
        """
        Constructor
        """
        self.type = type

    @staticmethod
    def dynamic_class_constructor(info_dict):
        """
        Creates an appropriate Filter subclass from an info_dict
        """
        if "type" not in info_dict:
            warnings.warn('No "type" specified in info_dict')
            return None
        else:
            filter_type = info_dict['type']
            if filter_type == 'PolesZeros':
                obj = PolesZeros.dynamic_class_constructor(filter_type, info_dict)
            elif filter_type == 'FIR':
                obj = FIR.dynamic_class_constructor(filter_type, info_dict)
            elif filter_type == 'Coefficients':
                obj = Coefficients.dynamic_class_constructor(filter_type, info_dict)
            elif filter_type == 'ResponseList':
                obj = ResponseList.dynamic_class_constructor(filter_type, info_dict)
            elif filter_type == 'AD_CONVERSION':
                obj = AD_Conversion.dynamic_class_constructor(filter_type, info_dict)
            elif filter_type == 'ANALOG':
                obj = Analog.dynamic_class_constructor(filter_type, info_dict)
            elif filter_type == 'DIGITAL':
                obj = Digital.dynamic_class_constructor(filter_type, info_dict)
            else:
                warnings.warn(f'Unknown Filter type: "{info_dict["type"]}"')
        return obj
    
    def dictobj(self):
        return self.__dict__


class PolesZeros(Filter):
    """
    PolesZeros Filter
    """
    def __init__(self, filter_type, units, transfer_function_type='LAPLACE (RADIANS/SECOND)', 
                 poles=[], zeros=[],
                 normalization_frequency=1., normalization_factor=None):
        """
        poles and zeros should be lists of complex numbers
        """
        if transfer_function_type == 'LAPLACE (RADIANS/SECOND)':
            self.units = "rads/s" if not units else units
        elif transfer_function_type == 'LAPLACE (HERTZ)':
            self.units = "Hz" if not units else units
        elif transfer_function_type == 'DIGITAL (Z-TRANSFORM)':
            self.units = None if not units else units
        else:
            warnings.warn(f'Illegal transfer_function_type in PolesZeros: "{transfer_function_type}"')
            
        self.transfer_function_type = transfer_function_type
        self.poles = poles
        self.zeros = zeros
        self.normalization_frequency = normalization_frequency
        if normalization_frequency and normalization_factor:
            self.normalization_factor = normalization_factor
        else:            
            self.normalization_factor = self.calc_normalization_factor()

        super().__init__(filter_type)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, info_dict):
        """
        Create PolesZeros instance from an info_dict
        """
        obj = cls(filter_type,
                  info_dict.get(info_dict.get('units', None)),
                                info_dict.get('transfer_function_type',
                                    'LAPLACE (RADIANS/SECOND)'),
                                [(float(x[0]) + 1j*float(x[1]))\
                                    for x in info_dict.get('poles', [])],
                                [(float(x[0]) + 1j*float(x[1]))
                                    for x in info_dict.get('zeros', [])],
                                info_dict.get('normalization_frequency', 1.),
                                info_dict.get('normalization_factor', None))
        return obj

    def __repr__(self):
        """
        String representation of object
        """
        s = f'PolesZeros("{self.units}", {self.poles}, {self.zeros}, '
        s += f'{self.normalization_frequency:g}, '
        s += f'{self.normalization_factor:g})'
        return s

    def calc_normalization_factor(self, debug=False):
        """
        Calculate the normalization factor for give poles-zeros

        The norm factor A0 is calculated such that
                           sequence_product_over_n(s - zero_n)
                A0 * abs(------------------------------------------) === 1
                           sequence_product_over_m(s - pole_m)
        for s_f=i*2pi*f if the transfer function is in radians
                i*f     if the transfer function is in Hertz
        """
        if not self.normalization_frequency:
            return None #Assert if freq = None and send error msg

        A0 = 1.0 + (1j * 0.0)
        if self.transfer_function_type == "LAPLACE (HERTZ)":
            s = 1j * self.normalization_frequency
        elif self.transfer_function_type == "LAPLACE (RADIANS/SECOND)":
            s = 1j * 2 * m.pi * self.normalization_frequency
        else:
            print("Don't know how to calculate normalization factor "
                  "for z-transform poles and zeros!") #Warning msg
            return None
        for p in self.poles:
            A0 *= (s - p)
        for z in self.zeros:
            A0 /= (s - z)

        if debug:
            print("poles={}, zeros={}, s={:g}, A0={:g}".format(
                self.poles, self.zeros, s, A0))

        A0 = abs(A0)
        return A0


class FIR(Filter):
    """
    FIR Filter
    """
    def __init__(self, filter_type, symmetry, delay, coefficients,
                 coefficient_divisor):
        
        self.symmetry = symmetry
        if symmetry not in ['ODD', 'EVEN', 'NONE']:
            warnings.warn(f'Illegal FIR symmetry: "{symmetry}"')
        self.delay = delay
        self.coefficients = coefficients
        self.coefficient_divisor = coefficient_divisor
        super().__init__(filter_type)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, info_dict):
        """
        Create FIR instance from an info_dict
        """
        obj = cls(filter_type,
                  info_dict.get('symmetry', 'NONE'),
                  info_dict.get('delay', 0),
                  info_dict.get('coefficients', []),
                  info_dict.get('coefficient_divisor', 1.))
        return obj

    def __repr__(self):
        """
        String representation of object
        """
        s = f'FIR("{self.symmetry}", {self.delay:g}, '
        s += f'{self.coefficients}, {self.coefficient_divisor})'
        return s


class Coefficients(Filter):
    """
    Coefficients Filter
    """
    def __init__(self, filter_type, transfer_function_type, numerator_coefficients,
                 denominator_coefficients):
        if transfer_function_type not in ["ANALOG (RADIANS/SECOND)",
                                          "ANALOG (HERTZ)",
                                          "DIGITAL"]:
            warnings.warn('Illegal transfer function type: "{}"'.format(
                transfer_function_type))

        self.transfer_function_type = transfer_function_type
        self.numerator_coefficients = numerator_coefficients
        self.denominator_coefficients = denominator_coefficients
        super().__init__(filter_type)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, info_dict):
        """
        Create Coefficients instance from an info_dict
        """
        obj = cls(filter_type, info_dict.get('transfer_function_type', 'DIGITAL'),
                  info_dict.get('numerator_coefficients', []),
                  info_dict.get('denominator_coefficients', []))
        return obj

    def __repr__(self):
        s = f'Coefficients("{self.transfer_function_type}", '
        s += f'{self.numerator_coefficients}, '
        s += f'{self.denominator_coefficients})'
        return s


class ResponseList(Filter):
    """
    ResponseList Filter
    """
    def __init__(self, filter_type, response_list):
        self.response_list = response_list
    
        super().__init__(filter_type)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, info_dict):
        """
        Create Response List instance from an info_dict
        """
        obj = cls(filter_type, info_dict.get('elements', []))
        return obj

    def __repr__(self):
        return f'ResponseList("{self.response_list}")'


class Analog(PolesZeros):
    """
    Analog Filter (Flat PolesZeros filter)
    """
    def __init__(self, filter_type): 
        self.units = "rad/s"
        self.poles = []
        self.zeros = []
        self.normalization_frequency = 0.
        self.normalization_factor = None
        super().__init__(filter_type, self.units, "LAPLACE (RADIANS/SECOND)", self.poles, self.zeros, self.normalization_frequency, self.normalization_factor)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, info_dict):
        """
        Create Analog instance from an info_dict
        """
        obj = cls(filter_type)
        return obj

    def __repr__(self):
        return 'Analog()'


class Digital(Coefficients):
    """
    Digital Filter (Flat Coefficients filter)
    """
    def __init__(self, filter_type):
        self.transfer_function_type = 'DIGITAL'
        self.numerator_coefficients = [1.0]
        self.denominator_coefficients = []
        super().__init__(filter_type, "DIGITAL", self.numerator_coefficients, self.denominator_coefficients)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, info_dict):
        """
        Create Digital instance from an info_dict
        """
        obj = cls(filter_type)
        return obj

    def __repr__(self):
        return 'Digital()'


class AD_Conversion(Coefficients):
    """
    AD_Conversion Filter (Flat Coefficients filter)
    """
    def __init__(self, filter_type, input_full_scale, output_full_scale):
        self.transfer_function_type = 'DIGITAL'
        self.numerator_coefficients = [1.0]
        self.denominator_coefficients = []
        self.input_full_scale = input_full_scale
        self.output_full_scale = output_full_scale
        super().__init__(filter_type, "DIGITAL", None, None)

    @classmethod
    def dynamic_class_constructor(cls, filter_type, info_dict):
        """
        Create AD_Conversion instance from an info_dict
        """
        obj = cls(filter_type, info_dict.get('input_full_scale', None),
                  info_dict.get('output_full_scale', None))
        return obj

    def __repr__(self):
        s = f'AD_Conversion({self.input_full_scale:g}, '
        s += f'{self.output_full_scale})'
        return s
