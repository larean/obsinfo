======================================
Information files
======================================


Basic principals of information files
======================================

- They are in JSON or YAML
- The base level for each type of file has the same fields, except the one containing all of the information that obsinfo will import:

  - ``format_version``: version of the information file format
  - ``revision``: Who made the file and when
  - ``notes``: Notes about the contents that will not be saved/transferred elsewhere
  - ``yaml_anchors``: used to define the YAML anchors (a section of data that
    can be named an inserted elsewhere, allowing the user to avoid typing redundancy/errors
    and make the YAML files smaller and more readable
  - ``extras``: Is this a good idea?
  - ``{TYPE}``, where ``{TYPE}`` is one of the information file types and is the last
    field in the filename.  This is where all of the information that obsinfo will
    read is stored
    
- Within a given version, new fields are put within the open-form ``extras`` field.

- Other files are referenced using "$ref" and the JSON Pointers syntax, but we do NOT
  use JSON pointers, allowing us only partially read files downstream and to use YAML in
  addition to JSON
  
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
