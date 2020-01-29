import json
import pprint
import os.path
import sys

# Non-standard modules
import yaml
import obspy.core.util.obspy_types as obspy_types
import obspy.core.inventory as inventory
import obspy.core.inventory.util as obspy_util
from obspy.core.utcdatetime import UTCDateTime

################################################################################       
class network_info:
    """ Basic information about an FDSN network """
    def __init__(self,info):
        """ Initialize using obs-info network.yaml "network_info" field"""
        self.code=       info['code']
        self.start_date= UTCDateTime(info['start_date'])
        self.end_date=   UTCDateTime(info['end_date'])
        self.description=info['description']
        self.comments=   info['comments']  # Should be a list
################################################################################       
class equipment_type:
    """ Duplicates StationXML EquipmentType """
    def __init__(self,equipment_dict,debug=False):
        """ Initialize from YAML OBS-info equipment dictionary"""
        self.type=None
        self.description=None
        self.manufacturer=None
        self.model=None
        self.serial_number=None
        self.vendor=None
        self.installation_date=None
        self.removal_date=None
        self.calibration_date=None
        if debug:
            print(equipment_dict)
        for key in equipment_dict:
            if not hasattr(self,key):
                raise NameError('No attribute "{}" in FDSN_EquipmentType'.key)
            else:
                setattr(self,key,equipment_dict[key])
    def merge(self,new):
        """ Merge two EquipmentType objects
    
            Takes values from "new" where they exist
            new should be a 
        """
        if not type(new) == equipment_type:
            print('Tried to merge with a non FDSN_EquipmentType')
            return
        for key in vars(new):
            if getattr(new,key):
                setattr(self,key,getattr(new,key))

