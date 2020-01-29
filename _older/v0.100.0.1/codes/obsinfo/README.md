# obsinfo
A system for creating metadata for Ocean Bottom Seismometers

Based on "information" files in YAML or JSON format (the code
currently only handles YAML, but this should be easy to change). 

## Information files
There are 4 main types of files:
Name | Description | Filled by | Filled when
-----|-------------|-----------|-------------
**campaign** | Names of stations and facilities, plus events used for verification.  NOT NECESSARY FOR PROCESSING | Chief scientist | after an expedition
**network** |  Deployed stations, their instruments and parameters | OBS facility | after an expedition 
**instrumentation** | Instrument description | OBS facility | new/changed instruments
**instrument-components** | Description of basic components (sensors, digitizers, amplifiers/filters) | OBS facility OR generic | new components/calibrations

JSON Schema are provided for each file types

## Code
core module reads information files and combine into a complete station description.
stationxml module outputs stationXML files

## Version nomenclature
We use the standard MAJOR.MINOR.REVISION version numbering, but as long as the system
is in prerelease:
* MAJOR=0
* MINOR increments every time the file structure changes
* REVISION increments if the code changes

Use [Github-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to modify this file.