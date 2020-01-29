Filenames:
  Make_Model_Configuration_Component_SerialNumber_StartDate_EndDate
    (filters only use the first 4 sections)

Everything except _filters is a list of stages, even if there is only one stage

Stages will be read/created in the order (top first, bottom last):
    Sensor       : sensor     (REQUIRED)
    Preamplifier : ana_filter
    Datalogger   : ana_filter
and multiple stages within one file are ordered "top first" to "bottom last"
