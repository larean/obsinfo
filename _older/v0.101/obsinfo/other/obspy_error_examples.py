#!/usr/bin/env python3
""" 
Examples of errors/inconsistencies in obspy v1.10
"""
import obspy.core.util.obspy_types as obspy_types
from obspy.core import inventory

# DOESN'T WORK
lat=inventory.util.Latitude(40.0,.005,.005)
lon=inventory.util.Longitude(-40.0,.005,.005)
elev=obspy_types.FloatWithUncertaintiesAndUnit(10.0,.5,.5)
#WORKS
lat=inventory.util.Latitude(40.0,lower_uncertainty=.005,upper_uncertainty=.005)
lon=inventory.util.Longitude(-40.0,lower_uncertainty=.005,upper_uncertainty=.005)
elev=obspy_types.FloatWithUncertaintiesAndUnit(10.0,lower_uncertainty=.5,upper_uncertainty=.5)
# ELEVATION CLAIMS TO BE A FLOAT, BUT WORKS WITH FloatWithUncertaintiesAndUnit

print(lon,lat,elev)
# VALUE TYPES NOT SPECIFIED IN ONLINE DOCS (HAVE TO DRILL DOWN INTO SOURCE)