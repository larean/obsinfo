This directory contains sample YAML files used to create data-center data and 
metadata after an OBS "campaign" (data collection, can be one or several cruises):
  - {CAMPAIGN}.campaign.yaml: to be filled in by the chief scientist 
  - {CAMPAIGN}.{FACILITY}.network.yaml: to be filled in by the OBS facility operator 
  - {FACILITY}.instrumentation.yaml: to be filled in by the OBS facility operator.
     This is an inventory of park instruments and only needs to be updated  when new
     instruments are created.
  - {FACILITY}.instrumentation-components.yaml: to be filled in by the OBS facility operator.
     This is an inventory of instrumentation components and only needs to be updated  when new
     components are added.

These files can either be in YAML or JSON format.  We use the YAML format
because it is easier to read/write by humans and it allows repeated values to
be specified once then referenced throughout the file.  

We also provide JSON-SCHEMA files.  JSON-SCHEMA is more complete and better
documented than any YAML schemas.  To validate your YAML file, convert it to
JSON (https://www.json2yaml.com/convert-yaml-to-json) and then validate it
against the appropriate schema file (https://www.jsonschemavalidator.net)
