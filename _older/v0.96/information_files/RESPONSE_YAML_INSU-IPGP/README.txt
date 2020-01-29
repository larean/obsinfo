Filenames:
  Instances:  Fabricant#Modèle#Paramétrisation#Composante#Serialnumber#Datededébut#Datedefin
  Responses : Fabricant#Modèle#Paramétrisation#Composante

Every type has a list of stages, even if there is only one stage

Sensor can have "sensor" and "ana_filter" components
Preamplifier can only have "sensor" components
Datalogger can have "anafilter", "digitizer" and "dig_filter" components

Stages will be read/created in the following order (top first, bottom last):
    Sensor       : sensor     (REQUIRED)
    Sensor       : ana_filter
    Preamplifier : ana_filter
    Datalogger   : ana_filter
    Datalogger   : digitizer  (REQUIRED)
    Datalogger   : dig_filter (REQUIRED)
and multiple stages within one file are ordered "top first" to "bottom last"