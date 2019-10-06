TO DO
======================

`Questions/suggestions for information files`_

.. _Questions/suggestions for information files: QUESTIONS_infofiles.rst

Bugs
______

- Crashes on empty or absent network.general_information.comments field

Major
______

Use different keys for model & configuration (and version?)
------------------------------------------------------------

Currently ```{MODEL}_{VERSION}_{CONFIGURATION}:```

Could do:
```
{MODEL}:
  {VERSION}:
    {CONFIGURATION}:
    {CONFIGURATION}:
  {VERSION}:
    {CONFIGURATION}:
```
or:
```
{MODEL}:
  "Description"
  "Versions":
    {VERSION}:
      "Description":
      "Configurations":
        {CONFIGURATION}:
        {CONFIGURATION}:
    {VERSION}:
      "Description":
      "Configurations":
        {CONFIGURATION}:
``` 
or even:
```
{MODEL}:
  "Description"
  "Versions":
    "Default":
      "Description":
      "Configurations":
        "Default":
        {CONFIGURATION}:
        {CONFIGURATION}:
    {VERSION}:
      "Description":
      "Configurations":
        "Default":
        {CONFIGURATION}:
        {CONFIGURATION}:
    {VERSION}:
      "Description":
      "Configurations":
        {CONFIGURATION}:
``` 
Would have to specify each of these (or have  default for the version and configuration).
Could choose to use only model and configuration.  Would need to change Python code
(but might be overall easier/clearer).  
```network:stations:{STATION}:instruments:channel_codes_locations:{CODE_LOC}:``
field datalogger_config might need to change to ```datalogger:config:```

Minor
______

- Add ``bad_stations`` field at same level (and with same format) as ``stations``?  This would
  allow one to correctly specify bad stations without the codes trying to make data and
  stationXML from them.  But it would force the user to specify a start_ and end_date and synchronization,
  even if there aren't any.
- Change network.general_information.description to network.general_information.name 
- In obsinfo-make_process_scripts_*, should --append imply --noheader ?
- Change ``network:general_information`` to ``network:fdsn_network_information`` (or 
  ``network:STATIONXML_network_information``, or ``network:experiement_information``).  This field is used to
  generate STATIONXML network information in the absence of informations directly from FDSN.  Its current name
  implies that the information belongs to the campaign, but several campaigns could be part of the same
  experiment/FDSN_network.
- **Define and use a standard naming system for response files**
- Change model naming from ```reference_code:model_config``` to 
   ```model: model```, ```config: config```.
  Within instrumentation and instrument_component files make a new level for the
  config instead of adding to  model name.  Use '1' for
  all models with only one configuration.
  
  * Get rid of "model" in instrumentation: already specified as field
- Make simpler network files in examples:
  * SPOBS_250sps_BUC: one from MOMAR (SPOBS, HOCT and BUC location)
  * BBOBS_61sps_SURFACE: one from PiLAB (BBOBS, acoustic survey and leap_second)
  * HOCT_100sps_ACOUSTIC:
  * MIX: mix of instruments and location methods
  * LEAPSECOND: with leapsecond
  * OBSOLETE:  weird cases and obsolete instruents 
- State somewhere that a given model has the same channels
  - Different configurations can have different responses

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
          
Put location code in instrumentation.yaml
------------------------------------------------------------

(allows proper specification of Hydroctopus, for example)

- Should automatically verify that channel_locations in network.yaml correspond
        
- Or only require a location code in instrumentation.yaml if there are duplicate channel codes?

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

- Should I be able to NOT specify the sample_rate?  (defined in data logger configuration?)

    - OR not specify configuration, but have instrumentation construct it from sample_rate (and dig_filter???)

- Should we use UCUM for response unit names?:

    - "M"->"m", "S"->"s", "COUNTS"->"{counts}", "PA"->"Pa" (or "PAL")
    
    - "V" is already UCUM

- Should I replace "response/stages/delay_correction" by response/delay_correction field: {'samples','seconds', OR 'automatic'}

    - If automatic, just set "corrected" equal to "delay"

    - If "samples" or "seconds", do as above for all stages except last, which is adjusted to fit provided value

    - Instruments should specify the delay applied and the obs-info code
      should verify that this correction corresponds to the delay predicted
      from the digital filter offets and/or stage delays
      
            - Set delay to 0
            
            - If offset is specified, calculate delay from it and input_sample_rate
            
            - If delay is specified, compare to calculated delay, send error if different
            
            - If delay is not specified, set it to the calculated value
            
            - Sum all of the delays
            
            - Compare with any provided delay value


Use `reStructuredText
<http://docutils.sourceforge.net/rst.html>`_ to modify this file.
