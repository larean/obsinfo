This directory contains:
  - the /campaigns directory, which has subdirectories for each data collection
    campaign. each subdirectory contains: 
      - {CAMPAIGN}.{FACILITY}.network.yaml: to be filled in by the OBS facility operator
      - {CAMPAIGN}.campaign.yaml: to be filled in by the chief scientist
  - the /instrumentation directory, which contains subdirectories to be filled in by the facility operator.
     each subdirectory corresponds to a facilty update and contains:
      - instrument_components.yaml: An inventory of instrumentation components.
      - instrumentation.yaml: An inventory of park instruments.
      - a /responses directory containing individual sensor, datalogger and filter stages
  - the /schemas directory containing JSON schemas for each file, which can be
    used to validate the information files using online tools or the
    metadata-validator tool that we developped (big so I can't send it here)


The information files can be in YAML or JSON format.


