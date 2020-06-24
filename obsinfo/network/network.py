"""
Instrumentation and Instrument classes

nomenclature:
    An "Instrument" (measurement instrument) records one physical parameter
    An "Instrumentation" combines one or more measurement instruments
"""
# Standard library modules

# Non-standard modules

# obsinfo modules
from ..obsMetadata.obsmetadata import (ObsMetadata)
from .station import (Station)

"""from ..instrumentation.instrument_component import (Datalogger, Sensor,
                                                    Preamplifier, Equipment,
                                                    InstrumentComponent)


"""
class Network(ObsMetadata):
    """
    One or more Instruments. Part of an obspy/StationXML Station
    """
    def __init__(self, attributes_dict=None):
        """
        Constructor
        """
        
        self.campaign_ref = attributes_dict.get("campaing_ref_bame", None)
        network_info = attributes_dict.get("network-info", None)
        self.fdsn_code = network_info.get("code", None)
        self.fdsn_name = network_info.get("name", None)        
        self.start_date = network_info.get("start_date", None)
        self.end_date = network_info.get("end_date", None)
        self.description = network_info.get("description", None)
        print(self.end_date) 
        
        #self.facility = Facility(attributes_dict.get("facility", None))                
        #self.stations = Stations(attributes_dict.get("stations", None))"""     
          

    def __repr__(self):
        s = f'Instrumentation({type(self.equipment)}, '
        s += f'{len(self.channels)} {type(self.channels[0])}'
        return s

class Facility(object):

    def __init__(self, attributes_dict):
        """
        Constructor
        """
        
        self.reference_name = attributes_dict.get("reference_name")
        self.full_name = attributes_dict.get("reference_name")
        self.email = attributes_dict.get("email")
        self.phone_number = attributes_dict.get("phone_number")
        self.website = attributes_dict.get("website")
        
if __name__ == '__main__':
    thisdict = {
        "campaign_ref": "My campaign",
        "network-info": {
           "code": "H34",
           "name": "My network",
           "start_date": "23/11/1957",
           "end_date": "01/01/2020",
           "description": "a test campaign" 
        }
    }
      
    A = Network(thisdict)
        
    
