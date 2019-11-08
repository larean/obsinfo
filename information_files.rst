======================================
Information files
======================================


Basic principals of information files
======================================

- They are in JSON or YAML
- All the information that obsinfo will read is in a base level field with the
  same name as the information file type (``"network"``, ``"instrumentation"``,
  ...)
     
  - The ``extras``  subfield is for fields that are not defined in the schema.

- The base level also has the following fields:

  - ``format_version`` (REQUIRED): version of the information file format
  - ``revision`` (REQUIRED): Who made the file and when
  - ``notes``: Notes about the contents that will not be saved/transferred
    elsewhere
  - ``yaml_anchors``: used to define the YAML anchors (a section of data that
    can be named an inserted elsewhere, allowing the user to avoid typing
    redundancy/errors)

- External files are referenced using "$ref" and the JSON Pointers syntax, but we do NOT
  use JSON pointers, allowing us to partially read files downstream and to use YAML in
  addition to JSON

Network files
======================================

Theses are the files that specify the stations deployed by an OBS facility
during an experiment.  Fields are:

:general_information: Fields that correspond to FDSN network information.  If there is already
   an FDSN network defined, the contents of these fields should match the
   FDSN values
   
:campaign_ref_name: Should match the first part of the filename and
  the ``ref_name`` field in the Campaign file
   
:facility: Basic information about the OBS facility.  ``ref_name`` should
  match the second field in the filename.  ``full_name`` will be put in the
  StationXML file
  
:ref_files: Files that the ``station:{STATION}:instruments`` fields will refer
  to.  ``instrument_components`` is needed if any of the instruments are
  fully described, ``instrumentation`` if any are described by reference.
  
:stations: the main field.  Subfields are station names.

:stations\:{STATION}:  Description of one station.  The information here goes
  almost directly into stationXML.
  
  :site: StationXML "site" field
  
  :start_date: StationXML station "start_date" field.  Will also be used for
    channels if they are not separately entered
    
  :end_date: Counterpart of "start_date".
  
  :location_code: StationXML station "location_code".  Will be used for channels
    if they are not separately entered.
    
  :locations: descriptions of each "location_code":  fields are the same
    as in StationXML except ``uncertainties.m`` (all values are in meters) and
    ``localisation_method`` (description of how the location was determined)
    
  :processing: Provenance information about how the data was transformed from
    raw to the final version.  Corresponds to nothing in StationXML, so the
    subfields are saved in StationXML comments
    
  :extras: Information that has no other place in the Network file schema.
    For new fields.  Subfields are saved to StationXML comments.

  :instruments: List of instruments making up the station.  Often just one
    element.  Each element is either an instrument reference ("ref") or a full
    instrument description.  Full instrument descriptions are described under
    "Instrumentation files".  Instrument references contain:
    
    :code: Instrument code, corresponding to a code specified in the
      instrumentation file.  This is the only required field
      
    :config: A particular configuration of the instrument, specified in the
      instrumentation file.
      
    :serial_number: Instrument serial number, either corresponds to a particular
      set-up in the instrument file, or just sets the ``serial_number`` field
      in the Station XML file
      
    :channel_mods:  Modifications to the instrument channels. Generally, the
      datalogger configuration will have to be specified to indicate the
      sampling rate and perhaps any configurable gain or filtering.
    
      :base: applied to all channels of the instrument.  Must include
        datalogger configuration.

      **ONLY USE ONE OF THE FOLLOWING**
      
      :by_orientation/{ORIENTATION-CODE}: applied to individual channels
        (added to base_channel_mods). Channels are specified by their SEED
        orientation code (as specified in the instrumentation file)
      
      :by_das/{DAS-CODE}: Same as above, but using the data acquisition code
        rather than the orientation code.  Used when a station has more than
        one channel with the same orientation code.

*Should I add (or even force) ``instruments:[N]:ref:datalogger_config`` as a
shortcut for ``instruments:[N]:ref:channel_mods:datalogger:config``?*

Linkages between information files
======================================
{xx} indicates a variable value/field name: CN= *DAS component number*, RC= *reference code*, SN= *serial number*, 
CL= *channel_location code*, DC= *datalogger configuration*, SC= *station code*, CC= *component code*, URL = *file locator*


+---------------------------------------------------------------------+---------------------------------------------------+
|    Referring file/field:                                            |    Target file/field.                             |
+=====================================================================+===================================================+
|     **network**                                                     |        **instrumentation**                        |
+---------------------------------------------------------------------+---------------------------------------------------+
| ``instrumentation:{$ref: URL}``                                     |   file name/URL                                   |
+---------------------------------------------------------------------+---------------------------------------------------+
| ``stations:{SC}:instrument:reference_code:{RC}``                    | ``instruments:generic:{RC}``                      |
|                                                                     |                                                   |
|                                                                     | ``instruments:specific:{RC}``                     |
+---------------------------------------------------------------------+---------------------------------------------------+
| ``stations:{SC}:instrument:serial_number:{RC}``                     | ``instruments:specific:{SN}``                     |
+---------------------------------------------------------------------+---------------------------------------------------+
+---------------------------------------------------------------------+---------------------------------------------------+
|     **network**                                                     |        **instrument_components**                  |
+---------------------------------------------------------------------+---------------------------------------------------+
| ``stations:{SC}:instrument:channel_locations:{CL}:                  | ``instrument_blocks:datalogger:generic:           |
| datalogger_config:{DC}``                                            | {RC}_{DC}``                                       |
+---------------------------------------------------------------------+---------------------------------------------------+
+---------------------------------------------------------------------+---------------------------------------------------+
|     **instrumentation**                                             |        **instrument_components**                  |
+---------------------------------------------------------------------+---------------------------------------------------+
| ``instrument_components:{$ref: URL}``                               |   file name/URL                                   |
+---------------------------------------------------------------------+---------------------------------------------------+
| ``instruments:generic:{RC}:das_components:{CN}:sensor:{CC}``        | ``instrument_blocks:sensor:generic:{CC}``         |
|                                                                     |                                                   |
| ``instruments:specific:{RC}:{SN}:das_components:{CN}:sensor:{CC}``  | ``instrument_blocks:sensor:specific:{SN}:{CC} ``  |
+---------------------------------------------------------------------+---------------------------------------------------+
| ``instruments:generic:{RC}:das_components:{CN}:datalogger``         | ``instrument_blocks:datalogger:generic``          |
|                                                                     |                                                   |
| ``instruments:specific:{RC}:{SN}:das_components:{CN}:datalogger``   | ``instrument_blocks:datalogger:specific:{SN} ``   |
+---------------------------------------------------------------------+---------------------------------------------------+
| ``instruments:generic:{RC}:das_components:{CN}:preamplifier``       | ``instrument_blocks:preamplifier:generic``        |
|                                                                     |                                                   |
| ``instruments:specific:{RC}:{SN}:das_components:{CN}:preamplifier`` | ``instrument_blocks:preamplifier:specific:{SN} `` |
+---------------------------------------------------------------------+---------------------------------------------------+
