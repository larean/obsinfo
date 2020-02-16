"""
Print complete stations from information in network.yaml file

nomenclature:
    A "measurement instrument" is a means of recording one physical parameter,
        from sensor through dac
    An "instrument" is composed of one or more measurement instruments

I need to modify the code so that it treats a $ref as a placeholder for the
associated object
"""
# Standard library modules
import os.path
import sys

# Non-standard modules
import yaml
import obspy.core.util.obspy_types as obspy_types
import obspy.core.inventory as obspy_inventory
import obspy.core.inventory.util as obspy_util
from obspy.core.utcdatetime import UTCDateTime

# Local modules
from ..misc.info_files import read_info_file
from ..misc import FDSN
from .util import create_comments
from ..misc import misc as oi_misc
from ..misc import obspy_routines as oi_obspy
# from ..misc.misc import make_channel_code
from ..instrumentation import Instrument

###############################################################################


class Network:
    """ Everything contained in a network.yaml file

        Has two subclasses:
            stations (.station)
            network_info (..misc.network_info)
    """

    def __init__(self, filename, referring_file=None):
        """ Reads from a network information file

        should also be able to specify whether or not it has read its sub_file
        """
        root, path = read_info_file(filename, referring_file)

        # Set variables outside of the network field
        self.basepath = path
        self.revision = root["revision"].copy()
        self.format_version = root["format_version"]
        net_dict = root["network"]
        self.facility = net_dict["facility"]
        self.campaign = net_dict["campaign_ref_name"]
        self.network_info = FDSN.network_info(net_dict["network_info"])
        self.ref_file = net_dict['ref_file']['$ref']
        self.ref_file_type = net_dict.get('ref_file_type',
                                                 'instrumentation')

        # Set stations in network
        self.stations = dict()
        # print("in network:__init__()")
        for sta_code, sta_dict in net_dict["stations"].items():
            # print(f"net={self.network_info.code}, station={code}")
            station = Station(sta_dict, sta_code, self.network_info.code)
            station.fill_instruments(self,os.path.join(path,filename))
            # print(self.stations[code])
            self.stations[sta_code] = station

    def __repr__(self):
        return f"<{__name__}.Network: code={self.network_info.code}, " +\
               f"facility={self.facility['ref_name']}, " +\
               f"campaign={self.campaign}, {len(self.stations):d} stations>"

    def __make_obspy_inventory(self, stations=None, source=None):
        """
        Make an obspy inventory object with a subset of stations

        stations = list of obs-info.OBS-Station objects
        source  =  value to put in inventory.source
        """
        my_net = self.__make_obspy_network(stations)
        if not source:
            source = self.facility.get('full_name',
                                        self.revision["author"]["first_name"]
                                        + " "
                                        + self.revision["author"]["last_name"])
        my_inv = obspy_inventory.inventory.Inventory([my_net], source)
        return my_inv

    def __make_obspy_network(self, stations):
        """Make an obspy network object with a subset of stations"""
        obspy_stations = []
        for station in stations:
            obspy_stations.append(station.make_obspy_station())

        temp = self.network_info.comments
        comments = None
        if temp:
            comments = create_comments(temp)
        my_net = obspy_inventory.network.Network(
            self.network_info.code,
            obspy_stations,
            description=self.network_info.description,
            comments=comments,
            start_date=self.network_info.start_date,
            end_date=self.network_info.end_date,
        )
        return my_net

    def write_stationXML(self, station_name, destination_folder=None):
        station = self.stations[station_name]
        # print("Creating obsPy inventory object")
        my_inv = self.__make_obspy_inventory([station])
        # print(yaml.dump(my_inv))
        if not destination_folder:
            destination_folder = "."
        fname = os.path.join(
            destination_folder,
            "{}.{}.STATION.xml".format(self.network_info.code, station_name),
        )
        print("Writing to", fname)
        my_inv.write(fname, "STATIONXML")

    def write_station_XMLs(self, destination_folder=None):
        for station_name in self.stations:
            self.write_station(station_name, destination_folder)


class Station:
    """a station from the network information file"""

    def __init__(self, station_dict, station_code, network_code):
        """ Create a station object directly from a network file's
        station: element """
        self.comments = station_dict.get("comments", [])
        self.site = station_dict["site"]
        self.start_date = station_dict["start_date"]
        self.end_date = station_dict["end_date"]
        self.instruments = station_dict["instruments"]
        self.station_location = station_dict["location_code"]
        self.locations = station_dict["locations"]
        self.processing = station_dict.get("processing", [])
        self.supplements = station_dict.get("supplements", [])  # ??
        self.code = station_code
        self.network_code = network_code
        #if "sensors" in station_dict:
        #    self.sensors = station_dict["sensors"]
        #else:
        #    self.sensors = None

    def __repr__(self):
        txt = f"< {__name__}.Station: code={self.code}, "
        for inst in self.instruments:
            if hasattr(inst, "das_components"):
                txt += f"instrument={inst} >"
            else:
                txt += f"instrument= ['{inst.ref_code}','{inst.equipment.serial_number}']"
        return txt

    def fill_instruments(self, net_obj, parent_file):
        """
        Fill station instruments
        
        Should work as well (and be clearer) if I change inst_dict to inst at the
        top of the for loop (and in call to Instrument creator), then remove
        first line and last two lines (append and self.instruments=...)
        
        :param net_obj: parent Network object
        :type net_obj: ~class `obsinfo.network.Network`
        :param parent_file: full path of network file
        :type parent_file: str
        """
        instruments = []
        for inst_dict in self.instruments:
            # Transform inst from dict to obj
            # print(inst_dict)
            inst = self._get_inst(net_obj, inst_dict, parent_file)
            # print(inst)
            inst.load_components(inst.components_file, inst.basepath)
            self.operator = inst.facility  # à verifier??
            # instruments[inst_dict["ref_code"]]=inst
            inst.fill_responses()
            instruments.append(inst)
        self.instruments = instruments
            
    def _get_inst(self, net_obj, inst_dict, parent_file):
        """
        Get an Instrument object
        """
        if net_obj.ref_file_type == "instrumentation":
            # Fill in instrument by reference
            assert 'ref_code' in inst_dict
            inst = Instrument.from_ref(net_obj.ref_file, inst_dict, parent_file)
        elif net_obj.ref_file_type == "instrument_components":
            # Fill in instrument directly
            inst = Instrument(net_obj.ref_file, inst_dict, net_obj.basepath,
                              net_obj.format_version, net_obj.revision, 
                              net_obj.facility, parent_file)
        else:
            raise NameError('"{}" is not an allowed ref_file_type'.format(\
                            net_obj.ref_file_type))
        return inst

    def make_obspy_station(self):
        """
        Create an obspy station object from a fully informed station
        """
        # CREATE CHANNELS
        # print(self)
        channels = []
        for instrument in self.instruments:
            # resource_id = instrument.resource_id
            for key, chan in instrument.das_components.items():
                channel=self._make_obspy_channel(key,chan)
                channels.append(channel)
                # print(yaml.dump(channel))
        # CREATE STATION
        station_loc_code = self.station_location  # david
        if station_loc_code in self.locations:
            sta_loc = self.locations[station_loc_code]
            obspy_lon, obspy_lat = oi_obspy.lon_lats(sta_loc)
        else:
            print("No valid location code for station, either ", end='')
            print("set station location_code or provide a location '00'")
            sys.exit()

        obspy_comments = oi_obspy.comments(self.comments, self.processing,
                                           self.supplements, station_loc_code,
                                           sta_loc)

        # DEFINE Operator
        agency = self.operator["full_name"]
        contacts = None
        if "email" in self.operator:
            contacts = [obspy_util.Person(emails=[self.operator["email"]])]
        website = self.operator.get("website", None)
        operator = obspy_util.Operator([agency], contacts, website)

        # print(obspy_comments)
        sta = obspy_inventory.station.Station(
            code=self.code,
            latitude=obspy_lat,
            longitude=obspy_lon,
            elevation=obspy_types.FloatWithUncertaintiesAndUnit(
                sta_loc["position"]["elev"],
                lower_uncertainty=sta_loc["uncertainties.m"]["elev"],
                upper_uncertainty=sta_loc["uncertainties.m"]["elev"],
            ),
            channels=channels,
            site=obspy_util.Site(getattr(self, "site", "")),
            vault=sta_loc["vault"],
            geology=sta_loc["geology"],
            equipments=[
                oi_obspy.equipment(instrument.equipment)
                for instrument in self.instruments
            ],
            operators=[operator],
            creation_date=start_date,  # Needed to write StationXML
            termination_date=end_date,
            description=None,
            comments=obspy_comments,
            start_date=start_date if start_date else None,
            end_date=end_date if end_date else None,
            restricted_status=None,
            alternate_code=None,
            data_availability=None,
        )
        # print(sta)
        return sta

    def _make_obspy_channel(self,key,chan):
        """
        Make an obspy channel from an obsinfo Station Channel
        """
        # print(key)
        # print(yaml.dump(chan))
        response = oi_obspy.response(chan["response"])
        # loc_code=key.split(':')[1]
        loc_code = chan["location_code"]
        try:
            location = self.locations[loc_code]
        except KeyError:
            print(f"location code {loc_code} not found in ")
            print("self.locations, valid keys are:")
            for key in self.locations.keys():
                print(key)
            sys.exit(2)
        obspy_lon, obspy_lat = oi_obspy.lon_lats(location)
        azi, dip = oi_misc.get_azimuth_dip(
            chan["sensor"].seed_codes, chan["orientation_code"])
        start_date = None
        end_date = None
        start_date_chan = None
        end_date_chan = None
        # Give at least 3 seconds margin around start and end dates

        if "start_date" in chan:
            start_date_chan = UTCDateTime(chan["start_date"])

        if self.start_date:
            start_date = UTCDateTime(self.start_date)

        if "end_date" in chan:
            end_date_chan = UTCDateTime(chan["end_date"])

        if self.end_date:

            end_date = UTCDateTime(self.end_date)

        # print(key)
        # print(yaml.dump(chan))
        # print(location)
        if "localisation_method" in location:
            channel_comment = obspy_util.Comment(
                "Localised using : {}".format(
                        location["localisation_method"])
            )
        else:
            channel_comment = None
        channel_code = make_channel_code(
            chan["sensor"].seed_codes,
            chan["band_code"],
            chan["inst_code"],
            chan["orientation_code"],
            chan["datalogger"].sample_rate,
        )
        start_date = start_date_chan if start_date_chan else start_date
        channel = obspy_inventory.channel.Channel(
            code=channel_code,
            location_code=loc_code,
            latitude=obspy_lat,
            longitude=obspy_lon,
            elevation=obspy_types.FloatWithUncertaintiesAndUnit(
                location["position"]["elev"],
                lower_uncertainty=location["uncertainties.m"]["elev"],
                upper_uncertainty=location["uncertainties.m"]["elev"],
            ),
            depth=location["depth.m"],
            azimuth=obspy_types.FloatWithUncertainties(
                azi[0],
                lower_uncertainty=azi[1] if len(azi) == 2 else 0,
                upper_uncertainty=azi[1] if len(azi) == 2 else 0,
            ),
            dip=dip[0],
            types=["CONTINUOUS", "GEOPHYSICAL"],
            sample_rate=chan["datalogger"].sample_rate,
            clock_drift_in_seconds_per_sample=1
            / (1e8 * float(chan["datalogger"].sample_rate)),
            sensor=oi_obspy.equipment(chan["sensor"].equipment),
            pre_amplifier=oi_obspy.equipment(
                            chan["preamplifier"].equipment)
            if "preamplifier" in chan
            else None,
            data_logger=oi_obspy.equipment(
                            chan["datalogger"].equipment),
            equipment=None,
            response=response,
            description=None,
            comments=[channel_comment] if channel_comment else None,
            start_date=start_date,
            end_date=end_date_chan if end_date_chan else end_date,
            restricted_status=None,
            alternate_code=None,
            data_availability=None,
        )
        return channel

def _make_stationXML_script(argv=None):
    """
    Create StationXML files from a network file and instrumentation file tree
    """
    from argparse import ArgumentParser

    parser = ArgumentParser(prog="obsinfo-makeSTATIONXML", description=__doc__)
    parser.add_argument("network_file", help="Network information file")
    parser.add_argument("-d", "--dest_path",
                        help="Destination folder for StationXML files")
    args = parser.parse_args(argv)

    if args.dest_path:
        if not os.path.exists(args.dest_path):
            os.mkdir(args.dest_path)

    # READ IN NETWORK INFORMATION
    net = Network(args.network_file)
    # print(net)

    for station in net.stations:
        net.write_stationXML(station, args.dest_path)
