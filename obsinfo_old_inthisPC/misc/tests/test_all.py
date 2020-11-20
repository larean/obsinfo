#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Functions to test obsinfo/misc functions
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from future.builtins import *  # NOQA @UnusedWildImport

import os
import glob
import unittest
import obsinfo.misc.yamlref
import inspect
import xml.etree.ElementTree as ET
from CompareXMLTree import XmlTree
from obsinfo.network.network import _make_stationXML_script
from obsinfo.misc.info_files import validate


class TestADDONSMethods(unittest.TestCase):
    """
    Test suite for misc obsinfo operations.
    """
    def setUp(self):
        self.path = os.path.dirname(os.path.abspath(inspect.getfile(
            inspect.currentframe())))
        self.testing_path = os.path.join(self.path, "data")
        self.infofiles_path = os.path.join(os.path.split(self.path)[0],
                                           '_examples',
                                           'Information_Files')

    def test_makeSTATIONXML(self):
        """
        Test STATIONXML creation.
        """
        for fname in ["SPOBS.INSU-IPGP.network.yaml",
                      "BBOBS.INSU-IPGP.network.yaml"]:
            net_file = os.path.join(self.infofiles_path, "campaign", fname)
            _make_stationXML_script([net_file, "-d", "."])

            compare = XmlTree()
            # excluded elements
            excludes = ["Created", "Real", "Imaginary", "Numerator",
                        "CreationDate", "Description", "Module"]
            excludes_attributes = ["startDate", "endDate"]
            excludes = [compare.add_ns(x) for x in excludes]

            for stxml in glob.glob("*.xml"):
                xml1 = ET.parse(stxml)
                xml2 = ET.parse(os.path.join(self.testing_path, stxml))
                self.assertTrue(compare.xml_compare(
                    compare.getroot(xml1), compare.getroot(xml2),
                    excludes=excludes,
                    excludes_attributes=excludes_attributes))
                os.remove(stxml)

    def test_validate_networks(self):
        """
        Test validate network files
        """
        for fname in glob.glob(os.path.join(self.infofiles_path,
                                            "campaign",
                                            "*.network.yaml")):
            self.assertTrue(validate(fname,quiet=True))

    def test_validate_instrumentation(self):
        """
        Test validate instrumentation files
        """
        for fname in glob.glob(os.path.join(self.infofiles_path,
                                            "instrumentation",
                                            "*.instrumentation.yaml")):
            self.assertTrue(validate(fname,quiet=True))

    def test_validate_instrument_components(self):
        """
        Test validate instrument_components files
        """
        for fname in glob.glob(os.path.join(self.infofiles_path,
                                            "instrumentation",
                                            "*.instrument_components.yaml")):
            self.assertTrue(validate(fname,quiet=True))

    def test_validate_responses(self):
        """
        Test validate instrumentation files
        """
        for fname in glob.glob(os.path.join(self.infofiles_path,
                                            "instrumentation",
                                            "responses",
                                            "*",
                                            "*.response.yaml")):
            self.assertTrue(validate(fname,quiet=True))

    def test_validate_filters(self):
        """
        Test validate instrumentation files
        """
        for fname in glob.glob(os.path.join(self.infofiles_path,
                                            "instrumentation",
                                            "responses",
                                            "_filters",
                                            "*",
                                            "*.filter.yaml")):
            self.assertTrue(validate(fname,quiet=True))

    def test_yamlref_load(self):
        """
        Test yamlref reading of identical json and yaml files
        """
        with open(os.path.join(self.testing_path, 'test_noref.yaml')) as fp:
            a = obsinfo.misc.yamlref.load(fp)
        with open(os.path.join(self.testing_path, 'test_noref.json')) as fp:
            b = obsinfo.misc.yamlref.load(fp)
        self.assertTrue(a == b)

    def test_yamlref_replacerefs(self):
        """
        Test yamlref replacing of "$ref"s
        """
        infile = os.path.join(self.testing_path, 'test_ref.yaml')
        with open(infile) as fp:
            a = obsinfo.misc.yamlref.load(fp, base_uri=f'file://{infile}')
        infile = os.path.join(self.testing_path, 'test_noref.yaml')
        with open(infile) as fp:
            b = obsinfo.misc.yamlref.load(fp)
        print(a)
        print(b)
        self.assertTrue(a == b)

def suite():
    return unittest.makeSuite(TestADDONSMethods, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
