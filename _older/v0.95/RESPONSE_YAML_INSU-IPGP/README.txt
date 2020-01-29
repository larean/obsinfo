Should specify what the elements of the filename mean.

"datalogger" directory REPLACES "digitizer" and "digital filter", because StationXML
doesn't have a place for both.

I don't change "ana_filt" to "preamplifier" because the ana_filt logically covers
other analog stages than a classic preamplifier (data_logger might actually have
analog stages as well).

Should I allow every type to have a list of stages?

Specify that element order will always be SENSOR -> ANA_FILT -> DATALOGGER when
constructing STATIONXML and that stages listed within each file will be put in order as well.