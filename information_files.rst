*******************
Information files
*******************

Basic principals
===================================

- Files are in JSON or YAML format

- The files describe a hierearchy of objects, from Network to Filter, allows the user to fully
  specify seismological network stations. 
  
- Most of the objects correspond to StationXML elements, but there are also fields that
  specify processing steps and allow configuration of the instrumentation.

- Filenames are {specific element}.{type}.{yaml,json}, where {type} is one of
  the levels described below.

- The base-level object of each file contains information about the file, plus
  a type-specific object:

  - ``format_version`` (REQUIRED): version of the information file format
  - ``revision`` (REQUIRED): Who made the file and when
  - ``yaml_anchors`` (optional):  Used to define YAML anchors (groups
    of objects that can be inserted elsewhere, reducing redundancy/errors)
  - {type}: same as in the filename, with format described in the corresponding
    level below

- Any level of the file can have the following optional fields:

  - ``notes``: Notes that will not be translated into the StationXML file.
  - ``extras``: Fields that don't exist in the definition, but maybe should.

External files are referenced using
  `JSON Pointers <https://tools.ietf.org/html/rfc6901>`_ syntax ("``$ref:``"), which we
  have expanded to work on YAML files as well. [#]_
  
.. [#] In the future, we could add a ``$config:`` key, which would not read in the referenced file immediately,
  allowing the code to evaluate some of the ``config`` and ``serial_number``
  information first.  This could reduce the amount of information read in, but is
  it worth the added complexity?

Configuration
===================================
Stations can be configured based on instrumentation/component serial numbers
and/or configurations, or direct entry of values to modify.

1) **Configuration definitions**: specify the different configurations
   possible, using the fields:
   
   - ``serial_number_definitions``: (differences between individual elements)
   - ``config_definitions``: (run-time changes/options for a given element)
  
2) **Configuration specifications**: specify which configuration is
   used by a given instrumentation and/or station, using the fields:

   - ``serial_number``
   - ``config``
   or direct specification of the fields to change
   
A ``config`` specification implements the corresponding ``config_definition``, whereas
a ``serial_number`` specification implements the corresponding ``serial_number_description``
AND sets the corresponding ``equipment:serial_number`` field.  If a ``config`` has no corresponding
``config_deinition``, an error is returned, but there is no error if a ``serial_number`` has no corresponding
``serial_number_definition``.
``serial_number definition`` objects, ``config_definition`` objects and direct specification
of fields to change use the same structure as the object that they
modify, but specify only the parts that are to be changed. For
example, if a Datalogger was specified in the file
"`LC2000.datalogger.yaml`" as (note: this is a simplifed datalogger object which would not validate)::
   
   datalogger:
        equipment:
            model: "CS5321/22"
            description: "CS5321/22 delta-sigma A/D converter + FIR digital filter"
        note: "I like to write things down"
        sample_rate: 125
        configuration_definitions:
            "125sps":
                equipment:
                    description: "CS5321/22 delta-sigma A/D converter + FIR digital filter [config=125sps]"
                sample_rate: 125
            "500sps":
                equipment:
                    description: "CS5321/22 delta-sigma A/D converter + FIR digital filter [config=500sps]"
                sample_rate: 500
    
then instantiating the datalogger as::
    
        base: $ref: "LC2000.datalogger.yaml"
        config: "500sps"

would return::

        equipment:
            model: "CS5321/22"
            description: "CS5321/22 delta-sigma A/D converter + FIR digital filter  [config=500sps]"
        note: "I like to write things down"
        sample_rate: 500
    
Most configuration specifications are made in the Network file, although
`Instrument Component Configuration`_ specifications can also be made in the
Instrumentation File.  Specifications made at higher levels (towards
``Network``) override those made at lower levels.

Objects
===================================
A chain of objects is needed to fully specify a station and its processing.
All of the objects can be in one file, but they are usually divided into
different files for clarity, portability, and to avoid repetition (DRY).
Typical file levels are Network, Instrumentation, Instrument Components
(Sensors, Dataloggers and Preamplifiers), Responses and Filters.

Network
*********************************

Specify the stations deployed by an OBS facility during an experiment.  Fields
are:

:`facility`: Basic information about the OBS facility.  ``ref_name`` should
    match the second field in the filename.  ``full_name`` will be
    put in the StationXML file
  
:`campaign_ref_name`: Should match the ``reference_name`` field in the
    Campaign file
   
:`network_info`: FDSN network information.  If you have declared a network
    with FDSN, the contents of these fields should match the
    values on the FDSN website
   
:`stations`: descriptions of each station.  Subfields are objects with key = 
    {`STATION_NAME`} and value = `Station`_ object.

Station
*********************************

Description of one station.
  
:`site`: StationXML "site" field
  
:`start_date`: StationXML station ``start_date`` field.  Also used for
    channels if they are not separately entered
    
:`end_date`: StationXML station ``end_date`` field.
  
:`location_code`: Station location code.  Will also be used for
    channels if they are not separately entered.

:`locations`: descriptions of each location code:  fields are the same
    as in StationXML except ``uncertainties.m`` (all values are in
    meters) and ``localisation_method`` (description of how the
    location was determined)
    
:`processing`: Provenance information about how the data was transformed from
    raw to the final version.  There is no corresponds field in
    StationXML, so subfields are saved as StationXML comments
    
:`extras`: Subfields are saved to StationXML comments.

:`instruments`: List of `Instrumentation Configuration`_ s making up the
   station   

Instrumentation Configuration
*********************************
A configured `Instrumentation`_ object

In the list below, later fields can modify earlier ones
    
:`base`: An `Instrumentation`_ object

Configuration Specification Fields (all optional)
-----------------------------

:`serial_number`: Specify the `Instrumentation`_  serial number (and
    ``serial_number_definition`` if it exists)
              
:`config`: Specify the `Instrumentation`_ ``configuration_definition``
  
:`datalogger_config`: Specify the `Datalogger`_ ``configuration_definition``
    for all channels (shortcut for
    ``channel_mods: {base: {datalogger: config}}``

:`datalogger_serial_number`: Specify the `Datalogger`_ ``serial_number`` (and
    ``serial_number_definition`` if it exists).  Shortcut for
    ``channel_mods: {base: {datalogger: serial_number}}``

:`sensor_config`: Shortcut for
    ``channel_mods: {base: {sensor: config}}``

:`sensor_serial_number`: Shortcut for
    ``channel_mods: {base: {sensor: serial_number}}``

:`preamplifier_config`: Shortcut for
    ``channel_mods: {base: {preamplifier: config}}``

:`preamplifier_serial_number`: Shortcut for
    ``channel_mods: {base: {preamplifier: serial_number}}``

:`channel_mods`: Specify `Channel`_ configurations.
                
    :`base`: Configurations applied to all channels.
    
    :`by_orientation/{ORIENTATION-CODE}`: Configurations applied to
      individual channels, keyed by their SEED orientation code
  
    :`by_das/{DAS-CODE}`: Configurations applied to individual channels,
      keyed by their data acquisition system (DAS) code.
      Use when a station has more than one channel with the same
      orientation code.

Channel Configuration
*********************************
Specify `Instrument Channel`_ modificiations and deployment-specific information

:`sensor`: Modifications to Sensor (see `Instrument Component Configuration`_)

:`datalogger`: Modifications to Datalogger (see `Instrument Component Configuration`_)

:`preamplifier`: Modifications to Preamplifier (see `Instrument Component Configuration`_)

:`location_code`: Channel's location code
              
:`start_date`: Channel start date (if different from station)

:`end_date`: channel end date (if different from station)
              

Instrument Component Configuration
*********************************
Specify `Instrument Component`_ modifications

:`base`: Full Instrument Component description (see `Instrument Component`_)

Configuration Specification Fields
-----------------------------

:`config`: Activate `Instrument Component`_-level
    ``configuration_definition``
  
:`serial_number`: Specify Instrument Component serial number and apply
    corresponding ``serial_number_definitions``, if they exist
              

Instrumentation
*********************************

Specify a scientfic instrument (OBS, field station), as equipment and channels

Fields are:

:`equipment`: Corresponds to StationXML Equipment object
  
:`base_channel`: (optional) A `Channel`_ object.
                 Simplifies specifying ``das_channels`` (below) if
                 the same datalogger|preamplifier|sensor is used on more than
                 one channel.  Choose the most common instrumentation channel
                 (for example, many seismometers have the same sensor
                 description on three channels).  The "`orientation_code`"
                 subfield is ignored.
:`das_channels`: A possibly incomplete `Channel`_ object.  Values provided
                 replace those in `base_channel`

Configuration Definition Fields
-----------------------------

Modifications to the above-mentioned fields.

:`configuration_definitions`: optional configurations 
      
:`serial_number_definitions`: serial number based modifications
   

Channel
*********************************

Specify an Instrumentation Channel (Instrument Components and an
orientation code). `Responses`_ for each Instrument component are stacked
from sensor (top) to datalogger (bottom)

Fields: 
-----------------------------
:sensor:  Sensor Instrument_Component

:preamplifier: Preamplifier Instrument_Component (optional)

:datalogger: Datalogger Instrument_Component

:orientation_code: SEED orientation code.

Instrument Component
*********************************

Specify an Instrument Component: `sensor`, `preamplifier` or `datalogger`.

Shared fields:
-----------------------------

:`equipment`: Corresponds to StationXML Equipment object
  
:`config_description`: Description of the default configuration.  Can be left
                       empty if there is only one configuration.

:`responses_ordered`: an ordered list of responses (see `Response Level`_)

Configuration Definition Fields
---------------------

modifications to the above-mentioned fields (plus any specific to the given
Instrument Component type).
    
:`serial_number_definitions`: serial-number based modifications

:`configuration_definitions`: optional configurations 


Component-specific Fields: 
-----------------------------

Datalogger
---------------------

:`sample_rate`: samples per second

:`delay_correction`: time correction applied to data to compensate FIR delay:

    :numeric: seconds delay to specify in last stage (for software correction
              of delay)
    :True: specify a correction in each stage corresponding to the specified
           delay in that stage
    :False: No correction will be specified (same as numeric = 0)

Sensor
---------------------

:`seed_codes`: SEED codes to give to channels using this sensor

    :`band_base`: Base SEED band code: "B" for broadband, "S" for short
                  period: obsinfo will determine the sample-rate-dependent band
                  codes to use for a given acquisition channel.
    :`instrument`: SEED instrument code
    :`orientation`: SEED orientation codes that can be associated with this
                    sensor. Each code is a key for an object containing:

                    :`azimuth.deg`: 2-element array of [value, uncertainty]
                    :`dip.deg`: 2-element array of [value, uncertainty]

Preamplifier
---------------------
None
 
Response
*********************************

:`stages`: List of response stages, most sub-elements are StationXML fields

    :`description`: string
    
    :`name`: string [``None``]

    :`input_units`: object with fields ``name`` and ``description``
    
    :`output_units`: object with fields ``name`` and ``description``
    
    :`gain`: object with fields ``value`` and ``frequency``
    
    :`decimation_factor`: factor by which this stage decimates data [1]
    
    :`output_sample_rate`: output sample rate [sps]
    
    :`delay`: Delay in seconds of the stage [0]
    
    :`calibration_date`: date of calibration that gave this response [`None`[
    
    :`filter`: `Filter`_ object

Filter
*********************************

Description of a filter.  Keys depend on the ``type``

Common fields:
-----------------------------

:`type`: "`PolesZeros`", "`Coefficients`", "`ResponseList`",
         "`FIR`", "`ANALOG`", "`DIGITAL`" or "`AD_CONVERSION`"

`PolesZeros`-specific fields:
-------------------------------

:`units`: string (only ``rad/s`` has been verified)

:`poles`: List of poles in the above units.  Each elements is a 2-element array
          containing the real and imaginary parts

:`zeros`:  List of zeros, specified as above

:`normalization_frequency`: As in StationXML

:`normatlization_factor`: As in StationXML


`FIR`-specific fields:
-------------------------------

:`symmetry`: ``ODD``, ``EVEN`` or ``NONE``

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
``normalization_freq`` = 0 and ``normalization_factor`` = 1.0


`DIGITAL`-specific fields:
-------------------------------

None.  Becomes a StationXML `Coefficients` stage with 
``numerator = [1.0]`` and ``denominator = []``


`AD_CONVERSION`-specific fields:
-------------------------------

:`input_full_scale`: full scale value (volts)

:`output_full scale`: full scale value (counts)

Behaves the same as `DIGITAL`, the fields are for information only.


