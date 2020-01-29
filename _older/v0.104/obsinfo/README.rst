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

+---------------------------+-----------------------+-----------------+---------------+
|    Name                   |    Description        |     Filled by   | Filled when   |
+===========================+=======================+=================+===============+
| **campaign**              | Lists of stations     |                 |               |
|                           | facilities and        |                 |               |
|                           | participants, plus    | Chief scientist | after a data  |
|                           | desired verification. |                 | collection    |
|                           | NOT NEEDED FOR        |                 | campaign      |
|                           | PROCESSING            |                 |               |
+---------------------------+-----------------------+-----------------+---------------+
| **network**               | Deployed stations,    |                 | after a       |
|                           | their instruments     | OBS facility    | campaign      |
|                           | and parameters        |                 |               |
+---------------------------+-----------------------+-----------------+---------------+
| **instrumentation**       | Instrument            | OBS facility    | new/changed   |
|                           | description           |                 | instruments   |
+---------------------------+-----------------------+-----------------+---------------+
| **instrument_components** | Description of basic  | OBS facility    | when there    |
|                           | components (sensors,  | -or-            | are new       |
|                           | digitizers,           | component       | components or |
|                           | amplifiers/filters)   | manufacturer    | calibrations  |
+---------------------------+-----------------------+-----------------+---------------+

There can also be **response** and **filter** files to simplify the input of
repeated elements in **instrument_components** files.

Conceptually, only the **campaign** and **network** files are OBS-specific.
The **instrumentation** files and their subfiles could be replaced by existing
standards such as RESP files or the NRL (Nominal Response Library).  The
advantage of the obsinfo instrumentation file tree is that 1) it provides a
simpler(?) and more standards-compliant way to specify the components and 
2) obsinfo can automatically calculate the sensitivities from these files
(using obsPy).  These files could easily be used to make RESP-files and
NRL directories, if so desired. 

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

Executables
======================

The following command-line executables perform useful tasks:

- ``obsinfo-validate``: validates an information file against its schema
- ``obsinfo-print``: prints a summary of an information file
- ``obsinfo-makeSTATIONXML``: generates StationXML files from a network +
  instrumentation information files


Other subdirectories
======================

`obsinfo/data/`
------------------------------------------------------------

Contains information used by the program:

``data/schema`` contains JSON Schema for each file type.


`obsinfo/_examples/`
------------------------------------------------------------

Contains example information files and scripts:

- ``_examples/Information_Files`` contains a complete set of information files

  * ``.../campaigns`` contains **network** and **campaign**  files

  * ``.../instrumentation`` contains **instrumentation**,
    **instrument_components**, **response** and **filter** files.

- ``_examples/scripts`` contains bash scripts to look at and manipulate these files
  using the Executables.  Running these scripts is a good way to make sure your
  installation works, looking at the files they work on is a good way to start
  making your own information files.

Comments
======================

We use standard MAJOR.MINOR.MAINTENANCE version numbering but, while the
system is in prerelease:

- MAJOR==0

- MINOR increments every time the information 
  file structure changes in a **non-backwards-compatible** way

- MAINTENANCE increments when the code changes or the file structure changes
  in a **backwards-compatible** way

Use `reStructuredText
<http://docutils.sourceforge.net/rst.html>`_ to modify this file.