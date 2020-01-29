The codes here can be used to check the instrument_components, instrumentation
and network files, or to make StationXML or OCA-JSON files.  The latter are
an example of what you might provide to a national center that creates metadata
from its own database of your instrument components.

obs-info.py has all of the important routines, the other scripts just use it.

Your Python installation should be 3.x and you should have the obspy and pyyaml
packages installed