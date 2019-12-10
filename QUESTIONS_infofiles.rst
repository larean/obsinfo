====================================================
QUESTIONS/IDEAS for INFORMATION FILES
====================================================

v1.0 of obsinfo should have a stable information file format, so this format
is probably the most important issue to settle .
Here are notes on what should be or *might want to be* changed
in the information files.  You can look in INFORMATION_FILES.rst
for the basic principals behind these files.

- **Allow a separate instrument-configurations.yaml file?**
  Instead of declaring YAML_ANCHORS at top, make a file with all of the
  possible configurations, for example: SPOBS2_125sps, SPOBS_250sps, etc.
  This would become the new $ref_file for the network files (which would then
  have three possible ref-file-types: "instrumentation", "instrument_components",
  or "instrument-configurations"
  
  - PRO: Would make network files smaller and eliminate having to copy
    headers from file to file.
  - CON: Would add another layer (of confusion?) to obsinfo.  Some of the 
    "configuration" elements 
  
- **Have separate files for each instrument and instrument-component**
  This is already done at the response level.   Might also have separate
  file types for datalogger-component, preamplifier-component and
  sensor-component.  Might need an overall facility.yaml file
  
  - PRO: Would allow the declared instruments to be easily seen.  Would allow
    updating one instrument (or component) without putting the same revision
    date on the others.  Might simplify schema files
  - CON: The common information currently at the top of each file would have 
    to be put in a separate file.  Would have to rethink directory (a different
    directory for each file type.  If directory structure changes, would have
    to change file references in each file (unless there is also a 
    dependencies.yaml file)
  
- **Allow instrument-components to be specified using other formats as well**

  Such as REF, for people who are used to using that

- **Allow files/references to be URLs**.  Would allow you to use a remote
  instrumentation catalog rather than having to carry it with you.
  The nomenclature is already there, but the code is not.  
