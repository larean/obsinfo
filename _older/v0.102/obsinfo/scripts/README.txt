These codes can be used to check the instrument_components, instrumentation
and network files, or to make StationXML or OCA-JSON files.  The latter are
an example of what you might provide to a national center that creates metadata
from its own database of your instrument components.

check_*.py provide a list of the elements in the Instrument_Components, 
       Instrumentation and Network files, and check for the existance of files
       downstream
       
make_*.py can be used to create metadata files or command strings to process data

Your Python installation should be 3.x and you should have the obsinfo package
installed (to install the  version in this directory, run 'pip install -e obsinfo')