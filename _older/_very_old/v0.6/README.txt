This directory contains sample YAML files used to process data and meta
data after an OBS experiment:
  - {CAMPAIGN}.campaign.yaml: to be filled in by the chief scientist 
    for each campaign
  - {CAMPAIGN}.{FACILITY}.network.yaml: to be filled in by the OBS facility operator 
    for each campaign
  - {FACILITY}.instrumentation.yaml: to be filled in by the OBS facility operator
    as an inventory of their park, and added to when new
    instruments or configurations are added.

All of the elements to be read in by an exterior software are contained in a 
top-level field with the same name as the file type ('campaign','network' or
'instrumentation').  

======================================================
ELEMENTS OF EACH FILE TYPE
======================================================
**CAMPAIGN**
campaign:
    reference_name: CAMPAIGN (string)
    version: (string)
    reference_scientist:
        name: (string)
        institution: (string)
        email: (string)
        telephone: (string)
    OBS_facilities:
        FACILITY_REFERENCE-NAME (string):
            contact: (string)
            stations: (list of strings)
        FACILITY2_REFERENCE-NAME (string):
            ...
        FACILITY3_REFERENCE-NAME (string):
            ...
        ...
    FDSN_network:
        code: (string)
        name: (string)
        description: (string)
        DOI: (string)
        URL: (string)
        email: (string)
        telephone: (string)
        start_date: (string or Timestamp)
        end_date: (string or Timestamp)
    event_samples: 
        # the data/metadata preparation center should send plots of these
        #   events to the reference scientist for validation before
        #   transferring the data/metadata to the data center
        # the plots will be sorted by distance if source_latitude and
        #   source_longitude are provided, by station name otherwise 
        TITLE_1 (string):
            date: (string or Timestamp)
            duration: (numeric (seconds) or string using UCUM(?) units)
            source_latitude: (floating point, optional)
            source_longitude: (floating point, optional)
        TITLE_2 (string):
            date: ~
            duration: ~
            ...
        TITLE_3 (string):
        ...
    # The following fields are optional
    expeditions:
        NAME_1 (string):
            ship: (string)
            start_date: (string or Timestamp)
            end_date: (string or Timestamp)
            comments: (string)
        NAME_2 (string):
            ...
        ...

======================================================
**NETWORK**
network:
    version: (string)
    instrumentation_file: (string, usually "{FACILITY}.instrumentaion.yaml)
    stations:
        STATION1_NAME (string):
            site: (string)
            FDSN_name: (string, station name to use for data center, if different)
            start_date: (timestamp)
            end_date:  (timestamp)
            sample_rate: (numeric)
            time_base: (string)
            comment_list: (list of strings for extra processing/information, such as specific tools/commmands used to correct time, leap second corrections...)
            instrument:
                model: (string, must be in instrumentation_file)
                serial_number: (string, must be in instrumentation_file)
            clock_correction_linear:
                reference: (str, "GPS" is only one used for now)
                start_sync_reference: (timestamp)
                start_sync_instrument: (timestamp or offset in seconds after start_sync_reference)
                end_sync_reference: (timestamp)
                end_sync_instrument: (timestamp or offset in seconds after end_sync_reference)
            location_codes:
                LOCATION_CODE (2-letter string):
                    latitude: (float)
                    longitude: (float)
                    elevation: (float, ground level in meters above sea level)
                    depth: (float, meters of sensor below ground level)
                    vault: (string, usually "Sea floor")
                    geology: (string)
                    loc_type: (string)
                    lat_uncert_m: (numeric)
                    lon_uncert_m: (numeric)
                    elev_uncert_m: (numeric)
        STATION2_NAME (string):
            ...
        STATION3_NAME (string):
            ...
        ...
======================================================
**INSTRUMENTATION*
# DBIRD version:
#     requires a directory structure containing the specified DBIRD_files.  
# See after for proposed StationXML (or RESP?) version
instrumentation:
    facility:
        reference_name: (string, should correspond to {FACILITY})
        full_name: (string)
        email: (string)
        website: (string)
        phone_number: (string)
    version: (string)
    response_format: "DBIRD"
    response_directory: (string, base directory for DBIRD files)
    instruments:
        MODEL1 (string):
            SERIAL_NUMBER_1 (string or "generic"):
                equipment: #description of the overall instrument)
                    type: (string)
                    description (string)
                    manufacturer: (string)
                    vendor: (string)
                    model: (string, should be same as instruments:MODEL)
                    serial_number: (string)
                datalogger: #description of the instrument's datalogger
                     type: (string)
                    description (string)
                    manufacturer: (string)
                    vendor: (string)
                    model: (string)
                    serial_number: (string)
                digitizer: #description and response of the datalogger's digitizer
                    type: (string)
                    description (string)
                    manufacturer: (string)
                    vendor: (string)
                    model: (string)
                    serial_number: (string)
                    DBIRD_file: (string)
                digital_filter: #description and response of the datalogger's digital filter
                    type: (string)
                    description (string)
                    manufacturer: (string)
                    vendor: (string)
                    model: (string)
                    serial_number: (string)
                    DBIRD_file: (string)
                channels:
                    # First letter is "S" for all short period sensors
                    #  "B" for all wide/broadband (>10s) sensors                   
                    CHAN_LOC_CODE_1 (string, SEED CHANNEL CODE + ":" + LOC CODE):
                        ana_filter: # description and response
                            type: (string)
                            description (string)
                            manufacturer: (string)
                            vendor: (string)
                            model: (string)
                            serial_number: (string)
                            DBIRD_file: (string)
                        sensor: # description, response, dip and azimuth
                             type: (string)
                            description (string)
                            manufacturer: (string)
                            vendor: (string)
                            model: (string)
                            serial_number: (string)
                            DBIRD_file: (string)
                            azimuth: (numeric)
                            dip: (numeric)
                    CHAN_LOC CODE_2:
                        ...
                    CHAN_CODE_3:
                    ...
        MODEL2 (string):
            ...
        MODEL3 (string):
            ...

# StationXML version:
#     Makes for a shorter (but less flexible) YAML file
#     Not implemented, just proposed
instrumentation:
    facility:
        reference_name: (string, should correspond to {FACILITY})
        full_name: (string)
        email: (string)
        website: (string)
        phone_number: (string)
    version: (string)
    response_format: "StationXML"
    response_directory: (string, base directory for StationXML files)
    instruments:
        MODEL1 (string):
            SERIAL_NUMBER_1 (string or "generic"):
                # Example with no modifications
                StationXML_file: (string)
            SERIAL_NUMBER_2 (string or "generic"):
                # Example with modifications to multi-instrument StationXML file
                StationXML_file: (string)
                modifications:
                    # Use same structure as in the "DBIRD version" but can leave
                    # out any fields that are not to be changed
                    equipment:
                        serial_number: (string)
                        ...
                    datalogger:
                        serial_number: (string)
                        ...
                    ...
                    channels:
                        CHAN_LOC_CODE_1:
                            sensor:
                                serial_number: (string)
                                manufacturer: (string)
                                ...
                            ...
                        CHAN_LOC_CODE_2:
                            ...
                        CHAN_LOC_CODE_3:
                            ...
                        ...
            SERIAL_NUMBER_3 (string or "generic"):
                ...
        MODEL2 (string):
            ...
        MODEL3 (string):
            ...
======================================================
VERSIONS
======================================================
0.5: INSTRUMENTATION file: 
        - Add parameters allowing full specification of StationXML
           <Equipment>, <Datalogger>, <Preamplifier> and <Sensor> fields.
        - Add "dip" and "azimuth" for each channel.
        - Made instances self-contained (at the expense of some streamlining).
     All files (no effect on output):
        - Made repeated node names UPPER_CASE
0.6: CAMPAIGN file:
        - added "version:"
        - changed "name:" to "reference_name:"
        - in "FDSN_network:"
            added "description:"
        - changed information in "OBS_facilities:" (previously "OBS_providers:")
            changed "email:" to "contact:"
            eliminated "representative:", "chief_engineer:" (in NETWORK file)
            added "stations:"
        - in "data_sample:"
            eliminated "ordering:" (automatically by distance if source_latitude
                                    and source_longitude provided, by station
                                    name otherwise)
    NETWORK file:
        - Changed name to {CAMPAIGN}.{FACILITY}.network.yaml
            Allows each facility to provide it's own stations' information
        - Added "instrumentation-file:"
        - Removed "network_info:"
        - in "stations:"
            changed key to be facility's station name
            within each station:
                - added "FDSN_name:"
                - added "geology:", "vault:" and "site:"
            
    INSTRUMENTATION file:         
        - Add "response_directory:" (absolute or relative pathname)
        Serial numbers: changed default string from "Default" to "generic"
                
