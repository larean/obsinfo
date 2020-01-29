# obsinfo
A system for saving information about Ocean Bottom Seismometers and their deployments and for creating FDSN-standard data and metadata using this information.

## Present Goal
To come out with a first version (v1.x) schema for the information files.  We request input from seismologists and ocean bottom seismometer manufacturers/facilities about what information/capabilities are missing.

## Information files
The system is based on "information" files in JSON or YAML format, filled in by appropriate actors and broken down into different categories to remove redundancy and simplify input as much as possible.

There are 4 main file types:

| Name | Description | Filled by | Filled when |
| ---- | ----------- | --------- | ----------- |
| Test |    Test     |    Test   |    Test     |

| **campaign** | Names of stations and facilities, plus events used for verification.  NOT NECESSARY FOR PROCESSING | Chief scientist | after an expedition |
| **network** |  Deployed stations, their instruments and parameters | OBS facility | after an expedition |
| **instrumentation** | Instrument description | OBS facility | new/changed instruments |
| **instrument-components** | Description of basic components (sensors, digitizers, amplifiers/filters) | OBS facility OR generic | new components/calibrations |

There can also be **response** and **filter** files to simplify the input of repeated elements in **instrument-components** files.

## Python code

The package name is `obsinfo`

`obsinfo.network`, `obsinfo.instrumentation` and `obsinfo.instrument_components` contain code to process the corresponding information files. `obsinfo.misc` contains code common to the above modules

`obspy.addons` contains modules specific to proprietary systems:

  - `obspy.addons.LCHEAPO` creates scripts to convert LCHEAPO OBS data to miniSEED using the `lc2ms` software
  - `obspy.addons.SDPCHAIN` creates scripts to convert basic miniSEED data to OBS-aware miniSEED using the `SDPCHAIN` software suite
  - `obspy.addons.OCA` creates JSON metadata in a format used by the Observatoire de la Cote d'Azur to create StationXML

## Directories

### `data/`
`data/campaigns` contains example **network** and **campaign** information files

`data/instrumentation` contains example **instrumentation** and **instrument-components**, **response** and **filter** information files.

`data/schema` contains JSON Schema for each file type, as well as a script to validate the example files.  The script requires a command-line code called "metadata-validator"

### `scripts/`
Contains:

 - `check_*.py`: print summaries of the contents of information files
 - `obsinfo_make_stationXML.py`: generate stationXML files
 - `obsinfo_make_sdpchain_scripts.py`: generate scripts to transform basic OBS data to FDSN-compatible, clock-corrected (and uncorrected), using the `lc2ms` and `SDPCHAIN` software suites.

## Comments
The python code currently only reads YAML format, but this should be easy to change.

We use standard MAJOR.MINOR.REVISION version numbering, but as long as the system is in prerelease:

* MAJOR=0
* MINOR increments every time the file structure changes
* REVISION increments if the code changes

Use [Github-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to modify this file.