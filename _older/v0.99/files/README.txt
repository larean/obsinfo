This directory contains sample "obs-info" files:
  - {FACILITY}.instrument-components.yaml: to be filled in by the OBS facility operator.
     This is an inventory of instrumentation components and only needs to be updated when new
     components are added.
  - {FACILITY}.instrumentation.yaml: to be filled in by the OBS facility operator.
     This is an inventory of park instruments and only needs to be updated when new
     instrumentation is created.
  - {CAMPAIGN}.{FACILITY}.network.yaml: to be filled in by the OBS facility operator
            after a campaign
  - {CAMPAIGN}.campaign.yaml: to be filled in by the chief scientist after a campaign

The first three files are needed to make fully-informed data and metadata after
a campaign.  The last file is useful for providing validation information to the
chief scientist and for confirming that the stations (and facilities) expected
by the chief scientist conform to those provided by the facility(ies).

These files can be in YAML or JSON format.  We use YAML because it is easier to 
read and write by humans. We also provide JSON-SCHEMA files to validate these files.

The RESPONSE_* directory contains individual sensor, datalogger and filter stages
that are referenced in the instrument-components.yaml file
