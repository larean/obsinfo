TO DO
======================

`Questions/suggestions for information files`_

.. _Questions/suggestions for information files: QUESTIONS_infofiles.rst

Bugs
______

- Crashes on empty or absent network.general_information.comments field

Minor
______

- Network file:

    - Add ``bad_stations`` field at same level (and with same format) as
      ``stations``?  This would allow one correct specification of bad stations
      without the codes trying to make data from them.  But it would force the
      user to specify a start_date and end_date for data recovery statistics.
      
    - Change ``network.general_information.description`` to 
     ``network.general_information.name`` 
     
    - Change ``network:general_information`` to
      ``network:fdsn_network_information`` (or
      ``network:STATIONXML_network_information``, or 
      ``network:experiement_information``).  This field is used to generate
      STATIONXML network information in the absence of informations directly
      from FDSN.  Its current name implies that the information belongs to the
      campaign, but several campaigns could be part of the same
      experiment/FDSN_network.
      
- ?Put location code in instrumentation.yaml?
 
    - (allows proper specification of Hydroctopus, for example)
   
    - Should automatically verify that channel_locations in network.yaml
      correspond        
     
    - Or only require a location code in instrumentation.yaml if there are
      duplicate channel codes?

- Code

   * ``In obsinfo-make_process_scripts_*``, should ``--append`` imply
     ``--noheader`` ?

   * Flatten the directory structure:
     * Put instrumentation.py, instrument.py, instrument_components.py,
       instrument_component.py, network.py and station.py at top level
     * maybe put station in network.py, instrument in instrumentation.py
       and instrument_component in instrument_components.py?
     * will allow me to make a "test/" directory at this level
   
- Define and use a standard naming system for response files

- Change model naming from ``reference_code:model_config`` to 
  ``reference_code: MODEL_VERS``, ``config: CONFIG``.
  
- Remove ``delay_correction_samples`` from ``instrument_components:datalogger``
  ( I don't think it's used anymore anyway)

  
- Make simpler network files in examples:

    - SPOBS_EXPT: one from MOMAR (SPOBS, HOCT and BUC location)
    - BBOBS_EXPT: one from PiLAB (BBOBS, acoustic survey and leap_second)
    - MANY_LOCS: showing many different location methods
    - HOCT_EXPT: showing an instrument with many of the same sensors
    - LEAPSECOND: with leapsecond
    - LANDSTATION: Showing full specification of each channels acquistion chain
    - CUSTOM-CONFIGS1: Show specification of gains
    - CUSTOM-CONFIGS2: Show specification of gains and sensors
    - OBSOLETE:  weird cases and obsolete instruments 
    
- State somewhere that a given instrument should have a fixed number of channels
  - Different configurations can change anything about the responses/components

Major
______

Use different keys for ref_code & configuration 
------------------------------------------------------------

 - As much information as possible in ref_code (description, channel list)
 - A ref code fixes the number of channels?
 - Configuration just modifies values established in ref_code?
 - ``network:stations:{STATION}:instruments:channel_codes_locations:{CODE_LOC}:``
   field datalogger_config might need to change to ``datalogger:config:``
 - Also put specifics inside "generic"s? both at ``ref_code`` level and perhaps
   at ``config`` level
 - MAYBE:
 
    * Allow common parts of ``das_components`` to be specified as
    ``base_component``? 
    
      - ``base_component`` would requires ``datalogger``, ``preamplifier``
        and ``sensor``
      - ``das_component`` would require ``orientation_code`` 
      - order of reading would be(right overwrites left): base_component ->
        das_components -> configurations -> serial_number -> network file specs::

   
Current model (151-line example)::

    instruments:
        generic:    # model_config
            "BBOBS_1_1":
                equipment:
                    <<: *EQUIPMENTTYPE_EMPTY
                    type: "Broadband Ocean Bottom Seismometer"
                    description: >-
                          "LCHEAPO 2000 Broadband Ocean Bottom Seismometer, 
                          configuration 1: all channels preamp gain = 0.225.
                          valid before 2012-11" 
                    manufacturer: "Scripps Inst. Oceanography - INSU"
                    model: "BBOBS1_1"
                das_components:
                    "1":
                        orientation_code : "2"
                        datalogger:  {reference_code: "LC2000_LOGGER"}
                        preamplifier: {reference_code: "LCHEAPO_BBOBS-GAIN_0P225X"}
                        sensor: {reference_code: "NANOMETRICS_T240_SINGLESIDED"}
                    "2":
                        orientation_code : "1"
                        datalogger:  {reference_code: "LC2000_LOGGER"}
                        preamplifier: {reference_code: "LCHEAPO_BBOBS-GAIN_0P225X"}
                        sensor: {reference_code: "NANOMETRICS_T240_SINGLESIDED"}
                    "3":
                        orientation_code : "Z"
                        datalogger:  {reference_code: "LC2000_LOGGER"}
                        preamplifier: {reference_code: "LCHEAPO_BBOBS-GAIN_0P225X"}
                        sensor: {reference_code: "NANOMETRICS_T240_SINGLESIDED"}
                    "4":
                        orientation_code : "H"
                        datalogger: {reference_code: "LC2000_LOGGER"}
                        preamplifier: {reference_code: "LCHEAPO_DPG-CARD"}
                        sensor: {reference_code: "SIO_DPG"}
            "BBOBS_1_2":
                equipment:
                    <<: *EQUIPMENTTYPE_EMPTY
                    type: "Broadband Ocean Bottom Seismometer"
                    description: >-
                          "LCHEAPO 2000 Broadband Ocean Bottom Seismometer, 
                          configuration 2: vertical channel preamp gain = 1.0.
                          valid from 2012-11 on" 
                    manufacturer: "Scripps Inst. Oceanography - INSU"
                    model: "BBOBS1_2"
                das_components:
                    "1":
                        orientation_code : "2"
                        datalogger:  {reference_code: "LC2000_LOGGER"}
                        preamplifier: {reference_code: "LCHEAPO_BBOBS-GAIN_0P225X"}
                        sensor: {reference_code: "NANOMETRICS_T240_SINGLESIDED"}
                    "2":
                        orientation_code : "1"
                        datalogger:  {reference_code: "LC2000_LOGGER"}
                        preamplifier: {reference_code: "LCHEAPO_BBOBS-GAIN_0P225X"}
                        sensor: {reference_code: "NANOMETRICS_T240_SINGLESIDED"}
                    "3":
                        orientation_code : "Z"
                        datalogger:  {reference_code: "LC2000_LOGGER"}
                        preamplifier: {reference_code: "LCHEAPO_BBOBS-GAIN_1X"}
                        sensor: {reference_code: "NANOMETRICS_T240_SINGLESIDED"}
                    "4":
                        orientation_code : "H"
                        datalogger: {reference_code: "LC2000_LOGGER"}
                        preamplifier: {reference_code: "LCHEAPO_DPG-CARD"}
                        sensor: {reference_code: "SIO_DPG"}
        specific:   # can be specified by orientation codes (if unique) or das_component
            "BBOBS_1_1":
                "01":
                    das_components:
                        "1": &BBOSBS1_1_01_SISMO
                            datalogger: {serial_number: "21"}
                            preamplifier: {serial_number: "21"}
                            sensor:     {serial_number: "Sphere01"}
                        "2":
                            <<: *BBOSBS1_1_01_SISMO
                        "3":
                            <<: *BBOSBS1_1_01_SISMO
                        "4":
                            datalogger: { serial_number: "21"}
                            preamplifier: { serial_number: "21"}
                            sensor:     { serial_number: "5004"}                    
                "02":
                    das_components:
                        "1": &BBOSBS1_1_02_SISMO
                            datalogger: { serial_number: "22"}
                            preamplifier: { serial_number: "22"}
                            sensor:     { serial_number: "Sphere02"}
                        "2":
                            <<: *BBOSBS1_1_02_SISMO
                        "3":
                            <<: *BBOSBS1_1_02_SISMO
                        "4":
                            datalogger: {  serial_number: "22"}
                            preamplifier: {  serial_number: "22"}
                            sensor:     { serial_number: "5018"}                    
                "03":
                    das_components:
                        "1": &BBOSBS1_1_03_SISMO
                            datalogger: {  serial_number: "23"}
                            preamplifier: {  serial_number: "23"}
                            sensor:     { serial_number: "Sphere03"}
                        "2":
                            <<: *BBOSBS1_1_03_SISMO
                        "3":
                            <<: *BBOSBS1_1_03_SISMO
                        "4":
                            datalogger: {  serial_number: "23"}
                            preamplifier: {  serial_number: "23"}
                            sensor:     { serial_number: "5027"}                    
            "BBOBS_1_2":
                "01":
                    das_components:
                        "1": &BBOSBS1_2_01_SISMO
                            preamplifier: {  serial_number: "21"}
                            datalogger: {  serial_number: "21"}
                            sensor:     { serial_number: "Sphere01"}
                        "2":
                            <<: *BBOSBS1_2_01_SISMO
                        "3":
                            <<: *BBOSBS1_2_01_SISMO
                        "4":
                            preamplifier: {  serial_number: "21"}
                            datalogger: {  serial_number: "21"}
                            sensor:     { serial_number: "5004"}                    
                "02":
                    das_components:
                        "1": &BBOSBS1_2_02_SISMO
                            datalogger: {  serial_number: "22"}
                            preamplifier: {  serial_number: "22"}
                            sensor:     { serial_number: "Sphere02"}
                        "2":
                            <<: *BBOSBS1_2_02_SISMO
                        "3":
                            <<: *BBOSBS1_2_02_SISMO
                        "4":
                            datalogger: {  serial_number: "22"}
                            preamplifier: {  serial_number: "22"}
                            sensor:     { serial_number: "5018"}                    
                "03":
                    das_components:
                        "1": &BBOSBS1_2_03_SISMO
                            datalogger: {  serial_number: "23"}
                            preamplifier: {  serial_number: "23"}
                            sensor:     { serial_number: "Sphere03"}
                        "2":
                            <<: *BBOSBS1_2_03_SISMO
                        "3":
                            <<: *BBOSBS1_2_03_SISMO
                        "4":
                            datalogger: {  serial_number: "23"}
                            preamplifier: {  serial_number: "23"}
                            sensor:     { serial_number: "5027"}                    

Using separate configuration (93 lines)::

    instruments:
        "BBOBS1":
            equipment:
                <<: *EQUIPMENTTYPE_EMPTY
                type: "Broadband Ocean Bottom Seismometer"
                description: "LCHEAPO 2000 Broadband Ocean Bottom Seismometer" 
                manufacturer: "Scripps Inst. Oceanography - INSU"
                model: "BBOBS1"
            das_components:
                "1":
                    orientation_code : "2"
                    datalogger:  {reference_code: "LC2000_LOGGER"}
                    preamplifier: 
                        reference_code: "LCHEAPO_BBOBS-GAIN"
                        config: "0P225X"
                     sensor: 
                        reference_code: "NANOMETRICS_T240"
                        config: "SINGLESIDED"
               "2":
                    orientation_code : "1"
                    datalogger:  {reference_code: "LC2000_LOGGER"}
                    preamplifier: 
                        reference_code: "LCHEAPO_BBOBS-GAIN"
                        config: "0P225X"
                    sensor: 
                        reference_code: "NANOMETRICS_T240"
                        config: "SINGLESIDED"
                "3":
                    orientation_code : "Z"
                    datalogger:  {reference_code: "LC2000_LOGGER"}
                    preamplifier: 
                        reference_code: "LCHEAPO_BBOBS-GAIN"
                        config: "0P225X"
                    sensor: 
                        reference_code: "NANOMETRICS_T240"
                        config: "SINGLESIDED"
                "4":
                    orientation_code : "H"
                    datalogger: {reference_code: "LC2000_LOGGER"}
                    preamplifier: {reference_code: "LCHEAPO_DPG-CARD"}
                    sensor: {reference_code: "SIO_DPG"}
            configurations:
                default_key: "2012+"
                keys:
                    "pre_2012":
                        description: "all channels have preamp gain = 0.225"
                    "2012+":
                        description: "vertical channel has preamp gain = 1.0"
                        das_components:
                            "3":
                                preamplifier: 
                                    reference_code: "LCHEAPO_BBOBS-GAIN"
                                    config: "1X""
            serial_numbers:
                "01":
                    das_components:
                        "1": &BBOSBS1_1_01_SISMO
                            datalogger: {serial_number: "21"}
                            preamplifier: {serial_number: "21"}
                            sensor:     {serial_number: "Sphere01"}
                        "2":
                            <<: *BBOSBS1_1_01_SISMO
                        "3":
                            <<: *BBOSBS1_1_01_SISMO
                        "4":
                            <<: *BBOSBS1_1_01_SISMO
                            sensor:     { serial_number: "5004"}                    
                "02":
                    das_components:
                        "1": &BBOSBS1_1_02_SISMO
                            datalogger: { serial_number: "22"}
                            preamplifier: { serial_number: "22"}
                            sensor:     { serial_number: "Sphere02"}
                        "2":
                            <<: *BBOSBS1_1_02_SISMO
                        "3":
                            <<: *BBOSBS1_1_02_SISMO
                        "4":
                            <<: *BBOSBS1_1_02_SISMO
                            sensor:     { serial_number: "5018"}                    
                "03":
                    das_components:
                        "1": &BBOSBS1_1_03_SISMO
                            datalogger: {  serial_number: "23"}
                            preamplifier: {  serial_number: "23"}
                            sensor:     { serial_number: "Sphere03"}
                        "2":
                            <<: *BBOSBS1_1_03_SISMO
                        "3":
                            <<: *BBOSBS1_1_03_SISMO
                        "4":
                            <<: *BBOSBS1_1_03_SISMO
                            sensor:     { serial_number: "5027"}  
                            
adding the "base_component" concept (63 lines)::

    instruments:
        "BBOBS1":
            equipment:
                <<: *EQUIPMENTTYPE_EMPTY
                type: "Broadband Ocean Bottom Seismometer"
                description: "LCHEAPO 2000 Broadband Ocean Bottom Seismometer" 
                manufacturer: "Scripps Inst. Oceanography - INSU"
                model: "BBOBS1"
            base_component:
                datalogger:
                    reference_code: "LC2000_LOGGER"
                preamplifier: 
                    reference_code: "LCHEAPO_BBOBS-GAIN"
                    config: "0P225X"
                sensor: 
                    reference_code: "NANOMETRICS_T240"
                    config: "SINGLESIDED"
            das_components:
                "1": {orientation_code : "2"}
                "2": {orientation_code : "1"}
                "3":
                    orientation_code : "Z"
                    preamplifier: 
                        reference_code: "LCHEAPO_BBOBS-GAIN"
                        config: "1X"
                "4":
                    orientation_code : "H"
                    preamplifier: {reference_code: "LCHEAPO_DPG-CARD"}
                    sensor: {reference_code: "SIO_DPG"}
            configurations:
                default_key: "2012+"
                keys:
                    "pre_2012":
                        description: "all channels with preamp gain = 0.225"
                        das_components:
                            "3":
                                preamplifier: 
                                    reference_code: "LCHEAPO_BBOBS-GAIN"
                                    config: "0P225X"
                    "2012+:
                        description: "vertical channel with preamp gain = 1.0"
            serial_numbers:
                "01":
                    base_component:
                        datalogger: {serial_number: "21"}
                        preamplifier: {serial_number: "21"}
                        sensor:     {serial_number: "Sphere01"}
                    das_components:
                        "4": {sensor: { serial_number: "5004"} }                   
                "02":
                    base_component:
                        datalogger: {serial_number: "22"}
                        preamplifier: {serial_number: "22"}
                        sensor:     {serial_number: "Sphere02"}
                    das_components:
                        "4": {sensor: { serial_number: "5018"}}                    
                "03":
                    base_component:
                        datalogger: {serial_number: "23"}
                        preamplifier: {serial_number: "23"}
                        sensor:     {serial_number: "Sphere03"}
                    das_components:
                        "4": {sensor: { serial_number: "5027"}}                    


Allow user to specify complete instruments for a network
------------------------------------------------------------

 - Allowing instrument-components file specification in network files?
 - Create  sample network files with gain configs entered
 - Create another with full instrument (but still around a base instrument
   that at least indicates the datalogger)
 - Should we allow a simple "gain" entry?  Or do we put this as the datalogger config

MAYBES:
-------------------


Define a "field separation" character?
------------------------------------------------------------

Define a character to separate "fields" in filenames and keys within the information files?
For now, '_' is used both to separate words and fields, so it's not easy to see what is a "key"
and what is a "field".  '#' can't be used in the filenames because it has a specific
meaning in JSON Pointers.  '.' (as in SeisComp3 Data Structure) is not very visual
but might be the simplest and is already used for separating fields from their unit definition
(as with "embargo_period.a", "duration.s" and duration.m" in network files)
Examples (using '.') would include:

- Data logger configurations (in instrument_component files): INDENTIFIER.CONFIG, e.g.:

    - LC2000_LOGGER.62sps
    
    - LC2000_LOGGER.125sps
    
    - OPENSOURCE_LOGGER.100sps_zerophase
    
    - OPENSOURCE_LOGGER.100sps_minphase

    - OPENSOURCE_LOGGER.100sps_minphase_4x

- Response filenames: MAKE.MODEL.CONFIG.CALIBRATION.response.yaml, e.g.:

    - Scripps.LCPO2000-CS5321.62sps.theoretical.response.yaml)
    
    - Scripps.LCPO2000-CS5321.125sps.theoretical.response.yaml)
    
    - SIO-LDEO.DPG.generic.theoretical.response.yaml)
    
    - SIO-LDEO.DPG.5004.calibrated.response.yaml)
    
- Instruments (in instrumention files):  IDENTIFIER.CONFIG, e.g.:

    - BBOBS1.1
    
    - BBOBS1.2
    
Allow generic and specific instrument_components files
------------------------------------------------------------

(with associated subdirectories)

- Could the generic one be specified in the specific one? 
        
- Should the instrument_component file(s) just specify the official     
  azimuth,dip values (e.g., "Z","N","E" for most seismometers), leaving
  the instrumentation file to change their azimuths and dips and/or
  change their names? (N->1, changes uncertainty to 180)? 
          
Allow network.yaml files to specify instrument orientations
------------------------------------------------------------

Change campaign.OBS_facilities.facilty.stations
------------------------------------------------------------

to station_names? or station_codes?

Add naming participants in campaign files
------------------------------------------------------------

So that DOIs are properly informed.

Maybe to network files too, so that facilities indicate the right people (might also help with resolving information gaps).

QUESTIONS    
======================

- Should I change network/general_information to network/fdsn_information?

- Should we use UCUM for response unit names?:

    - "M"->"m", "S"->"s", "COUNTS"->"{counts}", "PA"->"Pa" (or "PAL")
    
    - "V" is already UCUM

Use `reStructuredText
<http://docutils.sourceforge.net/rst.html>`_ to modify this file.
