*******************
Information files
*******************

Basic principals
==========================

- In JSON or YAML format

- Base-level fields:

  - ``format_version`` (REQUIRED): version of the information file format
  - ``revision`` (REQUIRED): Who made the file and when
  - {LEVEL}: where ``LEVEL`` is one of the levels described below

- Optional fields:

  - ``notes``: Notes that will not be translated into the StationXML file.
    Can be at almost any level
  - ``extras``: Fields that don't exist in the definition, but maybe should.
    Can be at almost any level
  - ``yaml_anchors``: At base level.  Used to define YAML anchors (groups
    of objects that can be inserted elsewhere, reducing redundancy/errors)

External files are referenced using

  - "$ref" for hard-coded files.  This uses the
    `JSON Pointers <https://tools.ietf.org/html/rfc6901>`_ model, but
    can read YAML files as well.
  - "$config" for files that should be evaluated at run time.  A separate
    "config" parameter must be provided, at which time a "$ref" is constructed
    as "{`$config:value}/config`".  This is most often used to provide data
    loggger configurations.

Network Level
==========================

Specify the stations deployed by an OBS facility during an experiment.  You
could specify the entire station/instrument/response in this file, but
JSON References are generally used to specify instruments or instrument
components.
Fields are:

:`facility`: Basic information about the OBS facility.  ``ref_name`` should
    match the second field in the filename.  ``full_name`` will be
    put in the StationXML file
  
:`campaign_ref_name`: Should match the ``ref_name`` field in the Campaign file
   
:`network_info`: FDSN network information.  If you have declared a network
    with FDSN, the contents of these fields should match the
    values on the FDSN website
   
:`stations`: descriptions of each station.  Subfields are objects with key = 
    {`STATION_NAME`} and value = `Station Level`_ object.

Station Level
==========================

Description of one station.
  
:`site`: StationXML "site" field
  
:`start_date`: StationXML station "start_date" field.  Will also be used for
    channels if they are not separately entered
    
:`end_date`: Counterpart of "start_date".
  
:`location_code`: Station location code.  Will also be used for
    channels if they are not separately entered.

:`locations`: descriptions of each location code:  fields are the same
    as in StationXML except ``uncertainties.m`` (all values are in
    meters) and ``localisation_method`` (description of how the
    location was determined)
    
:`processing`: Provenance information about how the data was transformed from
    raw to the final version.  There is no corresponds field in
    StationXML, so subfields are saved as StationXML comments
    
:`extras`: Information that has no other place in the Network file schema.
    Subfields are saved to StationXML comments.

:`instruments`: List of instruments making up the station. In the list below,
   later fields can modify earlier ones
    
    :`base`: Full instrument description (see `Instrumentation Level`_)
      
    :`datalogger_config`: shortcut for `channel_mods:base:datalogger:config`
          
    :`serial_number`: Instrument serial number: if it corresponds to a field
        under "`serial_numbers`" at the **Instrumentation Level**, will use
        the modifications specified there.
                  
    :`channel_mods`: [*optional*] Modifications to instrument channels.
                    
        :`base`: Modifications applied to all channels.
        
        :`by_orientation/{ORIENTATION-CODE}`: Modifications applied to
          individual channels, specified by their SEED orientation code (see
          **Instrument_Component Level** Sensor-specific fields)
      
        :`by_chan_loc/{CHAN_LOC-CODE}`: Modifications applied to individual
         channels, specified using the channel_location code ("`CCC_LL`").
          Use only when a station has more than one channel with the same
          orientation code.  Overrides `by_orientation`

        :`by_das/{DAS-CODE}`: Modifications applied to individual channels,
          specified using the data acquisition channel code.
          Use when a station has more than one channel with the same
          orientation code.  Overrides `by_orientation` or `by_chan_loc`

Instrumentation Level
==========================

Specify a scientfic instrument (OBS, field station), from sensor to datalogger

Fields are:

:`equipment`: Corresponds to StationXML Equipment object
  
:`base_channel`: Description of one channel.  Should correspond to the most
                 common channel on the instrumentation (for example) a seismometer
                 channel on an ocean-bottom seismometer.  Has subfields
                 "`datalogger`", "`preamplifier`" and "`sensor`" (see 
                 `Instrument_Component Level`_ for details)
:`das_channels`: descriptions of individual channels. Has required subfield
                 `orientation_code` and optional subfields `preamplifier`, 
                 `sensor` and `datalogger`, where the provided values replace
                 those in `base_channel`

:`configurations`: optional configurations. 
      
:`serial_numbers`: changes to configurations based on serial number.  Possible
                   fields are `equipment`, `base_channel` and `das_channel`, 
                   for which  the provided values replace those given in
                   the instrumentation definition
   
Instrument_Component Level
==========================

Specify an instrument component: `sensor`, `preamplifier` or `datalogger`.

Common fields:
-----------------------------

:`equipment`: Corresponds to StationXML Equipment object
  
:`config_description`: Description of the default configuration.  Can be left
                       empty if there is only one configuration.

:`response_stages`: a list of response stages (see `Response Level`_)

:`configurations`: optional configurations.  Fields are any of the
                   Instrument_Component fields (including specific ones for the
                   type (`datalogger`, `preamplifier` or `sensor`)

Datalogger-specific fields:
-----------------------------

:`sample_rate`: samples per second

:`delay_correction`: time correction applied to data to compensate FIR delay:

    :numeric: seconds delay to specify in last stage (for software correction
              of delay)
    :True: specify a correction in each stage corresponding to the specified
           delay in that stage
    :False: No correction will be specified (same as numeric = 0)

Sensor-specific fields:
-----------------------------

:`seed_codes`: SEED codes to give to channels using this sensor

    :`band_base`: Base SEED band code: "B" for broadband, "S" for short
                  period: obsinfo will determine the sample-rate-dependent band
                  codes to use for a given acquisition channel.
    :`instrument`: SEED instrument code
    :`orientation`: SEED orientation codes that can be associated with this
                    sensor. Each code is a key for an object containing:

                    :`azimuth.deg`: 2-element array of [value, uncertainty]
                    :`dip.deg`: 2-element array of [value, uncertainty]
 
Response Level
==========================

:`stages`: List of response stages, most sub-elements are StationXML fields

    :`description`: string
    
    :`input_units`: object with fields `name` and `description`
    
    :`output_units`: object with fields `name` and `description`
    
    :`gain`: object with fields ``value`` and ``frequency``
    
    :`filter`: `Filter Level`_ element

Filter Level
==========================

Description of a filter.  Fields depend on the ``type``

Common fields:
-----------------------------

:`type`: "`PolesZeros`", "`Coefficients`", "`ResponseList`",
         "`FIR`", "`ANALOG`", "`DIGITAL`" or "`AD_CONVERSION`"

`PolesZeros`-specific fields:
-------------------------------

:`units`: string (only "`rad/s`" has been verified)

:`poles`: List of poles in the above units.  Each elements is a 2-element array
          containing the real and imaginary parts

:`zeros`:  List of zeros, specified as above

:`normalization_frequency`: As in StationXML

:`normatlization_factor`: As in StationXML


`FIR`-specific fields:
-------------------------------

:`symmetry`: "`ODD`", "`EVEN`" or "`NONE`"

:`delay.samples`: samples delay for this FIR stage

:`coefficients`: list of FIR coefficients

:`coefficient_divisor`: Value to divide coefficients by to obtain equal energy
                        in the input and the output


`Coefficients`-specific fields:
-------------------------------

:`transfer_function_type`: "`ANALOG (RADIANS/SECOND)`", "`ANALOG (HERTZ)`", or
                           "`DIGITAL`"

:`numerator_coefficients`: list

:`denominator_coefficients`: list


`ResponseList`-specific fields:
-------------------------------

List of [frequency (Hz), amplitude, phase (degrees)] lists


`ANALOG`-specific fields:
-------------------------------

None.  Becomes a StationXML `PolesZeros` stage without poles or zeros,
`normalization_freq` = 0 and `normalization_factor` = 1.0


`DIGITAL`-specific fields:
-------------------------------

None.  Becomes a StationXML `Coefficients` stage with 
`numerator` = [1.0] and `denominator` = []


`AD_CONVERSION`-specific fields:
-------------------------------

:`input_full_scale`: full scale value (volts)

:`output_full scale`: full scale value (counts)

Behaves the same as `DIGITAL`, the fields are for information only.


