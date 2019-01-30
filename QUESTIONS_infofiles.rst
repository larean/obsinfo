====================================================
QUESTIONS/TODOs for INFORMATION FILES
====================================================

v1.0 of obsinfo should have a stable information file format, so this format
is probably the most important issue to settle right away.
Here are notes on what should be or *might want to be* changed
in the information files.  You can look in INFORMATION_FILES.rst
for the basic principals behind these files.

- **Separate obs-specific from "standard" (StationXML-compliant) information?**
  Some of the fields under ``station`` correspond to nothing in a StationXML
  file.  They are used for processing and are currently included as comments
  in StationXML files.  Putting them into an ``extras`` or ``addons`` field
  would have the following pros and cons:
  
  - PRO: might make obsinfo more attractive to non-obs users
  - CON: might make it LESS attractive to other seafloor users (such as OBM)
    and some of these features could even be useful for "standard" data
    
- Define and use a standard naming system for response files

- **Allow a generic and a specific instrument_components file?**  The
  generic version could become a standard library (downloadable or
  consultable online), the specific one would apply for custom
  sensors or specific calibrations
  
- **Allow files/references to be URLs**.  Linguistically it is already there,
  but the code is not.  This way, one could use a remove instrumentation catalog
  rather than having to carry it with you.
  
- **Explicitly separate configurations for instrument-components**. Currently, datalogger configurations
  are written as {DATALOGGER}_{CONFIG}, for example ``LC2000_LOGGER_62`` and ``LC2000_LOGGER_125``.  Should we
  instead use {DATALOGGER}:{CONFIG}?  The same question could be asked for PreAmplifiers (different configs for
  different gains, for example) and Sensors (different configs for different shunts on geophones, single-sided
  versus differential on seismometers, etc).  The problem is that we only explicitly specify configurations for
  dataloggers, and this nomenclature would take extra space, especially for components with only one configuration.
  And what would be call {CONFIG} for a component with only one configuration?  DEFAULT?

