

import pytest
from obsinfo.network.network import _make_stationXML_script
from CompareXMLTree import XmlTree

@pytest.fixture()
def compare():
	return XmlTree()
