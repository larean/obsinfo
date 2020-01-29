This directory contains sample YAML files used to process data and meta
data after an OBS experiment:
  - {CAMPAIGN}.campaign.yaml: to be filled in by the chief scientist 
    for each campaign
  - {CAMPAIGN}.network.yaml: to be filled in by the OBS facility operator 
    for each campaign
  - {OPERATOR}.instrumentation.yaml: to be filled in by the OBS facility operator
    when they first make the inventory of their park, and added to when new
    instruments/configurations are added.

All of the files contain the elements to be read in a top-level field with the
same name as the file type ('campaign','network' or 'instrumentation').  They
may also contain elements used to construct these values ("repeated nodes") in
another top-level field, called "repeated_nodes" by default.  As is standard in 
YAML, an empty field is specified by the symbol "~".

======================================================
ELEMENTS OF EACH FILE TYPE
======================================================
**CAMPAIGN**
campaign:
    name: CAMPAIGN_NAME (string)
    reference_scientist:
        name: (string)
        institution: (string)
        email: (string)
        telephone: (string)
    OBS_providers:
        FACILITY_NAME (string):
            email: (string)
            representative: (string)
            chief_engineer: (string)
        FACILITY_NAME_2 (string):
            ...
        FACILITY_NAME_3 (string):
            ...
        ...
    FDSN_network:
        code: (string)
        name: (string)
        DOI: (string)
        URL: (string)
        email: (string)
        telephone: (string)
        start_date: (string or Timestamp)
        end_date: (string or Timestamp)
    data_sample: 
        # the data/metadata preparation center should send plots of the
        # following events to the reference scientist for validation before
        # submitting the data/metadata to the data center
        TITLE_1 (string):
            date: (string or Timestamp)
            duration: (numeric, seconds)
            source_latitude: (floating point, optional)
            source_longitude: (floating point, optional)
            ordering: ['name', 'distance'] ('name' by default, 'distance' requires
                                          source_latitude and source_longitude)
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
    network_info:
        code: (string, should correspond to value in original data files)
        location: (string, describes geographic location of the network)
    stations:
        STATION_NAME_1 (string):
            name_old: (string, station name in orig data files, if different)
            instrument:
                facility: (string)
                model: (string, must be in FACILITY.instrumentation.yaml)
                serial_number: (string, must be in FACILITY.instrumentation.yaml)
            sample_rate: 62.5
            time_base: "Seascan MCXO, ~1e-9 nominal drift"
            comments_time: (string)
            comments_other: (list of strings)
            start_sync_GPS: (timestamp)
            start_sync_inst: (timestamp or offset in seconds after start_sync_GPS)
            end_sync_GPS: (timestamp)
            end_sync_inst: (timestamp or offset in seconds after end_sync_GPS)
            start_date: (timestamp)
            end_date:  (timestamp)
            location_codes:
                LOCATION_CODE (2-letter string):
                    latitude: (float)
                    longitude: (float)
                    elevation: (float, ground level in meters above sea level)
                    depth: (float, meters of sensor below ground level)
                    loc_type: (string)
                    lat_uncert_m: (numeric)
                    lon_uncert_m: (numeric)
                    elev_uncert_m: (numeric)
        STATION_NAME_2 (string):
            ...
        STATION_NAME_2 (string):
            ...
        ...
======================================================
**INSTRUMENTATION**
# Presumes the existence of a filesystem containing the specified DBIRD files.  
instrumentation:
    facility:
        short_name: (string, should correspond to value used in
                     network:stations:instrument)
        full_name: (string)
        email: (string)
        website: (string)
        phone_number: (string)
    version: (string)
    models:
        MODEL_1 (string):
            SERIAL_NUMBER (string or "Default"):
                comments: (string)
                digitizer_name: (string)
                digitizer_DBIRD_file: (string, DBIRD file path/name)
                digitizer_serial_number: (string)
                digital_filter_name: (string)
                digital_filter_DBIRD_file: (string, DBIRD file path/name)
                digital_filter_serial_number: (string)
                channels:
                    CHAN_CODE_1 (SEED CHANNEL CODE, "?" for wildcards):
                        ana_filter_name: (string)
                        ana_filter_DBIRD_file: (string, DBIRD file path/name)
                        ana_filter_serial_number: (string)
                        sensor_name: (string)
                        sensor_serial_number: (string)
                        sensor_DBIRD_file: (string, DBIRD file path/name)
                    CHAN_CODE_2:
                        ...
                    CHAN_CODE_3:
                    ...
        MODEL_2 (string):
            ...
        MODEL_3 (string):
            ...
