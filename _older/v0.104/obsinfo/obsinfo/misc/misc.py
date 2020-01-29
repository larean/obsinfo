""" 
Print complete stations from information in network.yaml file

nomenclature:
    A "measurement instrument" is a means of recording one physical parameter,
        from sensor through dac
    An "instrument" is composed of one or more measurement instruments
    
    version 0.99
    
I need to modify the code so that it treats a $ref as a placeholder for the associated object
"""
# Standard library modules
import math as m
import os.path
import sys

# Non-standard modules
import obspy.core.util.obspy_types as obspy_types
import obspy.core.inventory as inventory
import obspy.core.inventory.util as obspy_util
from obspy.core.utcdatetime import UTCDateTime

################################################################################ 
# Miscellaneous Routines

def calc_norm_factor(zeros,poles,norm_freq,pz_type,debug=False) :
    """
    Calculate the normalization factor for give poles-zeros
    
    The norm factor A0 is calculated such that
                       sequence_product_over_n(s - zero_n)
            A0 * abs(------------------------------------------) === 1
                       sequence_product_over_m(s - pole_m)

    for s_f=i*2pi*f if the transfer function is in radians
            i*f     if the transfer funtion is in Hertz
    """
    
    A0 = 1. + 1j*0.
    if pz_type == 'LAPLACE (HERTZ)':
        s = 1j * norm_freq
    elif pz_type == 'LAPLACE (RADIANS/SECOND)':
        s = 1j * 2 * m.pi * norm_freq
    else:
        print("Don't know how to calculate normalization factor for z-transform poles and zeros!")
    for p in poles:
        A0 = A0 * (s - p)
    for z in zeros:
        A0 = A0 / (s - z)
        
    if debug:
        print('poles=',poles,', zeros=',zeros,'s={:g}, A0={:g}'.format(s,A0))
    
    A0=abs(A0)
    
    return A0
    
##################################################
def round_down_minute(date_time,min_offset):
    """
    Round down to nearest minute that is at least minimum_offset seconds earlier
    """
    dt=date_time-min_offset
    dt.second=0
    dt.microsecond=0
    return dt

##################################################
def round_up_minute(date_time,min_offset):
    """
    Round up to nearest minute that is at least minimum_offset seconds later
    """
    dt=date_time+60+min_offset
    dt.second=0
    dt.microsecond=0
    return dt

##################################################
def make_channel_code(channel_seed_codes,
                        given_band_code,instrument_code,orientation_code,
                        sample_rate,
                        debug=False):
    """
        Make a channel code from sensor, instrument and network information
        
        channel_seed_codes is a dictionary from the instrument_component file
        given_band, instrument, and orientation codes are from the network file
        sample_rate is from the network_file
    """
    band_base=channel_seed_codes['band_base']
    if not len(band_base) == 1:
        raise NameError('Band code is not a single letter: {}'.format(band_code))
    if not instrument_code == channel_seed_codes['instrument']:
        raise NameError('instrument and component instrument_codes do not '\
                        'match: {}!={}'.format(inst_code,
                                        channel_seed_codes['instrument']))
    if not orientation_code in [key for key in channel_seed_codes['orientation']]:
        raise NameError('instrument and component orientation_codes do not '\
                        'match: {}!={}'.format(orientation_code,
                                        channel_seed_codes['orientation']))
    if band_base in 'FCHBMLVURPTQ':
        if sample_rate >=1000:
            band_code='F'
        elif sample_rate >=250:
            band_code='C'
        elif sample_rate >=80:
            band_code='H'
        elif sample_rate >=10:
            band_code='B'
        elif sample_rate > 1 :
            band_code='M'
        elif sample_rate > .3 :
            band_code='L'
        elif sample_rate > .03 :
            band_code='V'
        elif sample_rate > .003 :
            band_code='U'
        elif sample_rate >= .0001 :
            band_code='R'
        elif sample_rate >= .00001 :
            band_code='P'
        elif sample_rate >= .000001 :
            band_code='T'
        else :
            band_code='Q'
    elif band_base in 'GDES':
        if sample_rate >=1000:
            band_code='G'
        elif sample_rate >=250:
            band_code='D'
        elif sample_rate >=80:
            band_code='E'
        elif sample_rate >=10:
            band_code='S'
        else:
            raise ValueError('Short period instrument has sample rate < 10 sps')
    else:
        raise NameError('Unknown band code: {}'.format(band_code))
    if band_code != given_band_code :
        raise NameError('Band code calculated from component and sample rate'\
            ' does not match that given in network file: {} versus {}'.format(
                                    band_code,given_band_code))
    if debug:
        print(band_code)
    channel_code =  band_code+instrument_code+orientation_code
    return channel_code

##################################################
def get_azimuth_dip(channel_seed_codes,orientation_code):
    " Returns azimuth and dip [value,error] pairs "
    if orientation_code in channel_seed_codes['orientation']:
        azimuth=    channel_seed_codes['orientation'][orientation_code]['azimuth.deg']
        azimuth =   [float(x) for x in azimuth]
        dip=        channel_seed_codes['orientation'][orientation_code]['dip.deg']
        dip =       [float(x) for x in dip]
    else:
        raise NameError('orientation code "{}" not found in '\
                'component seed_codes.orientation'.format(orientation_code)) 
    return azimuth,dip