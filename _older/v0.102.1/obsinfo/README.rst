===================
 obsinfo
===================

A system for for creating FDSN-standard data and metadata for ocean bottom
seismometers using the simplest possible, standardized information files 

 Current goal
======================
To come out with a first version (v1.x) schema for the information files.  We
would like input from seismologists and ocean bottom seismometer
manufacturers/facilities about what information/capabilities are missing.

 Information files
======================

The system is based on "information" files in JSON or YAML format, filled in
by appropriate actors and broken down into different categories to remove
redundancy and simplify input as much as possible.

There are 4 main file types:
+---------------------------+----------------------+-----------------+---------------+
|    Name                   |    Description       |     Filled by   | Filled when   |
+===========================+======================+=================+===============+
| **campaign**              | Lists of stations    |                 |               |
|                           | facilities and       |                 |               |
|                           | participants, plus   | Chief scientist | after a data  |
|                           | desired verification |                 | collection    |
|                           | NOT NEEDED FOR       |                 | campaign      |
|                           | PROCESSING           |                 |               |
+---------------------------+----------------------+-----------------+---------------+
| **network**               | Deployed stations,   |                 | after a       |
|                           | their instruments    | OBS facility    | campaign      |
|                           | and parameters       |                 |               |
+---------------------------+----------------------+-----------------+---------------+
| **instrumentation**       | Instrument           | OBS facility    | new/changed   |
|                           | description          |                 | instruments   |
+---------------------------+----------------------+-----------------+---------------+
| **instrument-components** | Description of basic | OBS facility    | when there    |
|                           | components (sensors, | -or-            | are new       |
|                           | digitizers,          | component       | components or |
|                           | amplifiers/filters)  | manufacturer    | calibrations  |
+---------------------------+----------------------+-----------------+---------------+

There can also be **response** and **filter** files to simplify the input of
repeated elements in **instrument-components** files.

 Python code
======================

The package name is ``obsinfo``

``obsinfo.network``, ``obsinfo.instrumentation`` and
``obsinfo.instrument_components`` contain code to process the corresponding
information files. ``obsinfo.misc`` contains code common to the above modules

`obspy.addons` contains modules specific to proprietary systems:

  - ``obspy.addons.LCHEAPO`` creates scripts to convert LCHEAPO OBS data to
    miniSEED using the ``lc2ms`` software
  - ``obspy.addons.SDPCHAIN`` creates scripts to convert basic miniSEED data
    to OBS-aware miniSEED using the ``SDPCHAIN`` software suite
  - ``obspy.addons.OCA`` creates JSON metadata in a format used by the
    Observatoire de la Cote d'Azur to create StationXML

 Directories
======================

 `data/`
-----------------------

``data/campaigns`` contains example **network** and **campaign** information files

``data/instrumentation`` contains example **instrumentation** and
**instrument-components**, **response** and **filter** information files.

``data/schema`` contains JSON Schema for each file type, as well as a script
to validate the example files.  The script requires a command-line code called
"metadata-validator"

### `scripts/`
-----------------------

Contains:

 - ``check_*.py``: print summaries of the contents of information files
 - ``obsinfo_make_stationXML.py``: generate stationXML files
 - ``obsinfo_make_sdpchain_scripts.py``: generate scripts to transform basic OBS
   data to FDSN-compatible, clock-corrected (and uncorrected), using the 
   ``lc2ms`` and ``SDPCHAIN`` software suites.

 Comments
======================

The python code currently only reads YAML format, but this should be easy to change.

We use standard MAJOR.MINOR.MAINTENANCE version numbering, but as long as the
system is in prerelease, MAJOR==0, MINOR acts as MAJOR and MAINTENANCE AS MINOR,,
That is:

* MINOR increments every time the file structure changes in a non-backwards
  compatible way
* MAINTENANCE increments if the code changes of the file structure changes in a
  backwards-compatible way

Use [reStructuredText](http://docutils.sourceforge.net/rst.html) to modify this file.