import os
import unittest

from coala_quickstart.info_extraction.Info import Info
from coala_quickstart.info_extraction.InfoExtractor import InfoExtractor
from coala_quickstart.info_extraction.InfoScope import InfoScope


class InfoScopeTest(unittest.TestCase):

    def setUp(self):

        class DummyInfoExtractor(InfoExtractor):

            def parse_file(self, file_content):
                return file_content

            def find_information(self, fname, parsed_file):
                return [Info(
                    fname,
                    'Dummy information it is!')]

        class NoInfoExtractor(InfoExtractor):

            def parse_file(self, fname, file_content):
                return file_content

            def find_information(self, fname, parsed_file):
                return []

        class InfoA(Info):
            description = 'Information A'
            value_type = (str, int)
            example_values = ['coala', 111]

        self.InfoA = InfoA
        self.DummyInfoExtractor = DummyInfoExtractor
        self.NoInfoExtractor = NoInfoExtractor

        self.info_1 = InfoA(
            'source_file_1',
            'info_1_value',
            DummyInfoExtractor(['some_file'], os.getcwd()),
            extra_param='extra_param_value')

        self.info_2 = InfoA(
            'source_file_2',
            'info_2_value',
            NoInfoExtractor(['some_file'], os.getcwd()),
            extra_param='extra_param_value')

        self.global_scope = InfoScope("global",
                                      sections=[],
                                      bears=[])

        self.section_scope = InfoScope("section",
                                       sections=["python"],
                                       bears=[])

        self.bear_scope_with_section = InfoScope(
            "bear", sections=["python"], bears=["coalaBear"])

        self.bear_scope_without_section = InfoScope(
            "bear", sections=[], bears=["coalaBear"])

    def test_api(self):
        uut = InfoScope("bear",
                        ["some", "sections"],
                        ["some", "bears"],
                        allowed_sources=["some_filename"],
                        allowed_extractors=[self.DummyInfoExtractor])

        self.assertEqual(uut.level, "bear")
        self.assertEqual(uut.sections, ["some", "sections"])
        self.assertEqual(uut.bears, ["some", "bears"])
        self.assertEqual(uut.allowed_sources, ["some_filename"])
        self.assertEqual(uut.allowed_extractors, [self.DummyInfoExtractor])

    def test_check_belongs_to_scope(self):
        uut = self.global_scope
        # global scope should be acceptable for
        # any section or bear.
        self.assertTrue(uut.check_belongs_to_scope(
            "any_random_section", "any_random_bear"))
        self.assertTrue(uut.check_belongs_to_scope("", ""))

        uut = self.section_scope
        self.assertFalse(uut.check_belongs_to_scope(
            "any_random_section", "any_random_bear"))
        self.assertFalse(uut.check_belongs_to_scope("", ""))
        self.assertTrue(uut.check_belongs_to_scope(
            "python", "any_random_bear"))

        uut = self.bear_scope_with_section
        self.assertFalse(uut.check_belongs_to_scope(
            "any_random_section", "any_random_bear"))
        self.assertTrue(uut.check_belongs_to_scope(
            "python", "coalaBear"))
        self.assertFalse(uut.check_belongs_to_scope(
            "", "coalaBear"))

        uut = self.bear_scope_without_section
        self.assertFalse(uut.check_belongs_to_scope(
            "any_random_section", "any_random_bear"))
        self.assertTrue(uut.check_belongs_to_scope(
            "python", "coalaBear"))
        self.assertTrue(uut.check_belongs_to_scope(
            "", "coalaBear"))

    def test_check_is_applicable_information(self):
        # restriction on allowed_sources
        uut = InfoScope("global", allowed_sources=["source_file_1"])
        self.assertTrue(uut.check_is_applicable_information(self.info_1))
        self.assertFalse(uut.check_is_applicable_information(self.info_2))

        # restriction on allowed_extractors
        uut = InfoScope("global", allowed_extractors=(self.DummyInfoExtractor,))
        self.assertTrue(uut.check_is_applicable_information(self.info_1))
        self.assertFalse(uut.check_is_applicable_information(self.info_2))

        # no restrictions
        uut = InfoScope("global")
        self.assertTrue(uut.check_is_applicable_information(self.info_1))
        self.assertTrue(uut.check_is_applicable_information(self.info_2))

        # make sure `level` doesn't affect applicability of ``Info`` instance
        uut = InfoScope("bear")
        self.assertTrue(uut.check_is_applicable_information(self.info_1))
        self.assertTrue(uut.check_is_applicable_information(self.info_2))
