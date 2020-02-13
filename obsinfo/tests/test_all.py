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
from pprint import pprint
import xml.etree.ElementTree as ET
from CompareXMLTree import XmlTree
from obsinfo.network.network import _make_stationXML_script
from obsinfo.misc.info_files import (validate, _read_json_yaml,
                                     _read_json_yaml_ref, read_info_file)
from obsinfo.info_dict import InfoDict
from obsinfo.instrumentation import (Instrumentation, InstrumentComponent,
                                     Datalogger, Preamplifier, Sensor, 
                                     Response, Stage, Filter)


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
        # print(fname_A)
        A = _read_json_yaml_ref(fname_A)
        AB = _read_json_yaml_ref(os.path.join(self.testing_path, "jsonref_AB.json"))
        self.assertTrue(A==AB)
        
    def test_readJSONREF_yaml(self):
        """
        Test JSONref using a YAML file.
        """
        A = _read_json_yaml_ref(os.path.join(self.testing_path, "jsonref_A.yaml"))
        AB = _read_json_yaml_ref(os.path.join(self.testing_path, "jsonref_AB.yaml"))
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
        os.remove('temp')

    def test_filter(self):
        """
        Test reading a filter file.
        """
        A = read_info_file(os.path.join(self.infofiles_path, 
            "instrumentation",
            "sensors",
            "responses",
            "PolesZeros",
            "Sercel_L22D_C510-S2000_generic.filter.yaml"))
        obj = Filter.from_info_dict(A['filter'])
        # print(obj)
        
    def test_stage(self):
        """
        Test reading a stage file.
        
        Have to force-feed sample rates, which are provided at Response level
        """
        A = read_info_file(os.path.join(
            self.infofiles_path, 
            "instrumentation",
            "dataloggers",
            "responses",
            "TI_ADS1281_FIR1.stage.yaml"))
        obj = Stage.from_info_dict(A['stage'])
        # print(obj)
        obs_obj = obj.to_obspy()
        # print(obs_obj)

    def test_response(self):
        """
        Test reading and combining response files.
        """
        A = read_info_file(os.path.join(
            self.infofiles_path, 
            "instrumentation",
            "sensors",
            "responses",
            "Trillium_T240_SN400-singlesided_theoretical.response.yaml"))
        B = _read_json_yaml_ref(os.path.join(
            self.infofiles_path, 
            "instrumentation",
            "dataloggers",
            "responses",
            "TexasInstruments_ADS1281_100sps-linear_theoretical.response.yaml"))
        
        obj_A = Response.from_info_dict(A['response'])
        obj_B = Response.from_info_dict(B['response'])
        obj = obj_A + obj_B
        # print(obj)
        obs_obj = obj.to_obspy()
        # print(obs_obj)

    def test_datalogger(self):
        """
        Test reading datalogger instrument_compoents.
        """
        A = read_info_file(os.path.join(
            self.infofiles_path, 
            "instrumentation",
            "dataloggers",
            "LC2000.datalogger.yaml"))
        
        obj = InstrumentComponent.from_info_dict(A)
        obj = InstrumentComponent.from_info_dict(A['datalogger'])
        obj = Datalogger.from_info_dict(A['datalogger'])
        # print(obj)
        # print(obj.equipment)

    def test_sensor(self):
        """
        Test reading sensor instrument_compoents.
        """
        A = read_info_file(os.path.join(
            self.infofiles_path, 
            "instrumentation",
            "sensors",
            "NANOMETRICS_T240_SINGLESIDED.sensor.yaml"))
        
        obj = InstrumentComponent.from_info_dict(A)
        obj = InstrumentComponent.from_info_dict(A['sensor'])
        obj = Sensor.from_info_dict(A['sensor'])
        # print(obj)
        # print(obj.equipment)

    def test_instrumentation(self):
        """
        Test reading instrumentation.
        """
        A = read_info_file(os.path.join(
            self.infofiles_path, 
            "instrumentation",
            "SPOBS2.instrumentation.yaml"))
        obj = Instrumentation.from_info_dict(A['instrumentation'])

    def test_InfoDict_update(self):
        """
        Test InfoDict.update()
        """
        A = InfoDict(a=1, b=dict(c=2, d=3))
        A.update(dict(b=dict(d=4, e=5)))
        self.assertTrue(A == InfoDict(a=1, b=dict(c=2, d=4, e=5)))
        

    def test_InfoDict_daschannels(self):
        """
        Test InfoDict.complete_das_channels()
        """
        A = InfoDict(base_channel=dict(a=1, b=dict(c=2, d=3)),
                     das_channels={'1': dict(b=dict(c=5)), '2': dict(a=4)})
        A.complete_das_channels()
        # print(A)
        self.assertTrue(
            A == InfoDict(
                das_channels={'1': dict(a=1, b=dict(c=5, d=3)),
                              '2': dict(a=4, b=dict(c=2, d=3))}))
        

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
