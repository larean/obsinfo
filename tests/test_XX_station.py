"""
 There are several test
"""
import pytest
import os 
import xml.etree.ElementTree as ET
import glob 

from obsinfo.network.network import _make_stationXML_script

path = os.path.dirname(os.path.realpath(__file__))


def test_XX_station(compare):

	# run _makeXML
	_make_stationXML_script([f'{path}/Information_Files/campaigns/MYCAMPAIGN/MYCAMPAIGN.INSU-IPGP.network.yaml','-d', f'{path}/output/'])

	# test all stations

	# exluded element
	excludes = ['Created']
	excludes = [ compare.add_ns(x) for x in excludes]
	stationsXML = os.listdir(f'{path}/output/')
	for stxml in stationsXML:
		xml1 = ET.parse(f"{path}/output/{stxml}")
		xml2 = ET.parse(f"{path}/outputTest/{stxml}")
		assert  compare.xml_compare(compare.getroot(xml1),compare.getroot(xml2),excludes) 
