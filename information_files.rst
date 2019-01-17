======================================
Information files


Basic principals of information files
======================================

- They are in JSON or YAML
- The base level for each type of file has the same fields, except the one containing all of the information that obsinfo will import:

  - ``format_version``: version of the information file format
  - ``revision``: Who made the file and when
  - ``notes``: Notes about the contents that will not be saved/transferred elsewhere
  - ``yaml_anchors``: are used to define the YAML anchors (a section of data that
    can be named an inserted elsewhere), which allows one to avoid redundancy in
    typing and makes YAML files smaller and more readable
  - ``extras``: Is this a good idea?
  - ``{TYPE}``, where ``{TYPE}`` is one of the information file types and is the last
    field in the filename.  This is where all of the information that obsinfo will
    read is stored
    
- Within a given version, new fields are put within the open-form ``extras`` field.

- Other files are referenced using "$ref" and the JSON Pointers syntax, but we do NOT
  use JSON pointers, which allows to do only partial reads and to allow YAML as
  an information file language
  
Linkages between information files
======================================

- network file references to instruments
 
  - in the network file:
  
    - the instrumentation file name is found in ``network:instrumentation`` field
    - the `reference_code` and  ``serial_number`` are found in ``network:stations:NAME:instrument:``
    
  - in the instrumentation file:
  
    - the `reference_code` is found in ``instrumentation:instruments:generic`` and (possibly) ``instrumentation:instruments:generic``and  ``serial_number`` are found in ``network:stations:NAME:instrument:``

