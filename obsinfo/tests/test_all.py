#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Functions to test the lcheapo functions
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from future.builtins import *  # NOQA @UnusedWildImport

import os
import glob
import unittest
import inspect
import xml.etree.ElementTree as ET
from CompareXMLTree import XmlTree
from obsinfo.network.network import _make_stationXML_script
from obsinfo.misc.info_files import validate, read_json_yaml, read_json_yaml_ref


class TestADDONSMethods(unittest.TestCase):
    """
    Test suite for obsinfo operations.
    """
    def setUp(self):
        self.path = os.path.dirname(os.path.abspath(inspect.getfile(
            inspect.currentframe())))
        self.testing_path = os.path.join(self.path, "data")
        self.infofiles_path = os.path.join(os.path.split(self.path)[0],
                                           '_examples',
                                           'Information_Files')

    def assertTextFilesEqual(self, first, second, msg=None):
        with open(first) as f:
            str_a = f.read()
        with open(second) as f:
            str_b = f.read()

        if str_a != str_b:
            first_lines = str_a.splitlines(True)
            second_lines = str_b.splitlines(True)
            delta = difflib.unified_diff(
                first_lines, second_lines,
                fromfile=first, tofile=second)
            message = ''.join(delta)

            if msg:
                message += " : " + msg

            self.fail("Multi-line strings are unequal:\n" + message)

    def test_readJSONREF_json(self):
        """
        Test JSONref using a JSON file.
        """
        fname_A = os.path.join(self.testing_path, "jsonref_A.json")
        print(fname_A)
        A = read_json_yaml_ref(fname_A)
        AB = read_json_yaml_ref(os.path.join(self.testing_path, "jsonref_AB.json"))
        self.assertTrue(A==AB)
        
    def test_readJSONREF_yaml(self):
        """
        Test JSONref using a YAML file.
        """
        A = read_json_yaml_ref(os.path.join(self.testing_path, "jsonref_A.yaml"))
        AB = read_json_yaml_ref(os.path.join(self.testing_path, "jsonref_AB.yaml"))
        self.assertTrue(A==AB)
        
    def test_validate_json(self):
        """
        Test validation on a YAML file.
        
        The test file as an $ref to a file that doesn't exist, a field that
        is not specified in the the schema, and lacks a field required in 
        the schema
        """
        test_file = os.path.join(self.testing_path, 'json_testschema.json')
        test_schema = os.path.join(self.testing_path,
                                   'json_testschema.schema.json')
        # self.assertFalse(validate(test_file, schema_file=test_schema, quiet=True))
        
        # Run the code
        cmd = f'obsinfo-validate -s {test_schema} {test_file} > temp'
        os.system(cmd)

        # Compare text files
        self.assertTextFilesEqual(
            'temp',
            os.path.join(self.testing_path, 'json_testschema.out.txt')
            )
        # os.remove('temp')

#     def test_makeSTATIONXML(self):
#         """
#         Test STATIONXML creation.
#         """
#         for fname in ["SPOBS.INSU-IPGP.network.yaml",
#                       "BBOBS.INSU-IPGP.network.yaml"]:
#             net_file = os.path.join(self.infofiles_path, "campaign", fname)
#             _make_stationXML_script([net_file, "-d", "."])
# 
#             compare = XmlTree()
#             # excluded elements
#             excludes = ["Created", "Real", "Imaginary", "Numerator",
#                         "CreationDate", "Description", "Module"]
#             excludes_attributes = ["startDate", "endDate"]
#             excludes = [compare.add_ns(x) for x in excludes]
# 
#             for stxml in glob.glob("*.xml"):
#                 xml1 = ET.parse(stxml)
#                 xml2 = ET.parse(os.path.join(self.testing_path, stxml))
#                 self.assertTrue(compare.xml_compare(
#                     compare.getroot(xml1), compare.getroot(xml2),
#                     excludes=excludes,
#                     excludes_attributes=excludes_attributes))
#                 os.remove(stxml)

#     def test_validate_networks(self):
#         """
#         Test validate network files
#         """
#         for fname in glob.glob(os.path.join(self.infofiles_path,
#                                             "campaign",
#                                             "*.network.yaml")):
#             self.assertTrue(validate(fname,quiet=True))
# 
#     def test_validate_instrumentation(self):
#         """
#         Test validate instrumentation files
#         """
#         for fname in glob.glob(os.path.join(self.infofiles_path,
#                                             "instrumentation",
#                                             "*.instrumentation.yaml")):
#             self.assertTrue(validate(fname,quiet=True))
# 
    def test_validate_dataloggers(self):
        """
        Test validate datalogger files
        """
        for fname in glob.glob(os.path.join(self.infofiles_path,
                                            "instrumentation",
                                            "dataloggers",
                                            "*.datalogger.yaml")):
            self.assertTrue(validate(fname,quiet=True))
        for fname in glob.glob(os.path.join(self.infofiles_path,
                                            "instrumentation",
                                            "dataloggers",
                                            "responses",
                                            "*.response.yaml")):
            self.assertTrue(validate(fname,quiet=True))
        for fname in glob.glob(os.path.join(self.infofiles_path,
                                            "instrumentation",
                                            "dataloggers",
                                            "responses",
                                            "FIR",
                                            "*.filter.yaml")):
            self.assertTrue(validate(fname,quiet=True))

#     def test_validate_preamplifiers(self):
#         """
#         Test validate preamplifier files
#         """
#         for fname in glob.glob(os.path.join(self.infofiles_path,
#                                             "instrumentation",
#                                             "preamplifiers",
#                                             "*.preamplifier.yaml")):
#             self.assertTrue(validate(fname,quiet=True))
#         for fname in glob.glob(os.path.join(self.infofiles_path,
#                                             "instrumentation",
#                                             "preamplifiers",
#                                             "responses",
#                                             "*.response.yaml")):
#             self.assertTrue(validate(fname,quiet=True))
# 
    def test_validate_sensors(self):
        """
        Test validate sensor files
        """
        for fname in glob.glob(os.path.join(self.infofiles_path,
                                            "instrumentation",
                                            "sensors",
                                            "*.sensor.yaml")):
            self.assertTrue(validate(fname,quiet=True))
        for fname in glob.glob(os.path.join(self.infofiles_path,
                                            "instrumentation",
                                            "sensors",
                                            "responses",
                                            "*.response.yaml")):
            self.assertTrue(validate(fname,quiet=True))
        for fname in glob.glob(os.path.join(self.infofiles_path,
                                            "instrumentation",
                                            "sensors",
                                            "responses",
                                            "PoleZeros",
                                            "*.filter.yaml")):
            self.assertTrue(validate(fname,quiet=True))


def suite():
    return unittest.makeSuite(TestADDONSMethods, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
