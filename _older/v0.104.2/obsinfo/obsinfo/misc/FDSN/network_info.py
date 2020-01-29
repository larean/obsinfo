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
