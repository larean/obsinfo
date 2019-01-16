TO DO
======================

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