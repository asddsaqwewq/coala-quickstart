import os
import unittest

from coala_quickstart.info_extractors.PackageJSONInfoExtractor import (
    PackageJSONInfoExtractor)
from coala_quickstart.info_extraction.Information import (
    LicenseUsedInfo, ProjectDependencyInfo, IncludePathsInfo, ManPathsInfo,
    VersionInfo)
from tests.TestUtilities import generate_files


test_file = """ {
    "name": "awesome-packages",
    "version": "0.8.0",
    "license": "MIT",
    "dependencies": {
        "coffeelint": "~1",
        "ramllint": ">=1.2.2 <1.2.4"
    },
    "files": ["dist"],
    "man" : ["./man/foo.1", "./man/bar.1"]
}
"""


class PackageJSONInfoExtractorTest(unittest.TestCase):

    def setUp(self):
        self.current_dir = os.getcwd()

    def test_extracted_information(self):

        with generate_files(
              ["package.json"],
              [test_file],
              self.current_dir) as gen_file:

            self.uut = PackageJSONInfoExtractor(
                ["package.json"],
                self.current_dir)

            extracted_information = self.uut.extract_information()
            extracted_information = extracted_information["package.json"]
            print(extracted_information)

            information_types = extracted_information.keys()

            self.assertIn("LicenseUsedInfo", information_types)
            license_info = extracted_information["LicenseUsedInfo"]
            self.assertEqual(len(license_info), 1)
            self.assertEqual(license_info[0].value, "MIT")

            self.assertIn("ProjectDependencyInfo", information_types)
            dep_info = extracted_information["ProjectDependencyInfo"]
            self.assertEqual(len(dep_info), 2)
            self.assertIn(dep_info[0].value, ["coffeelint", "ramllint"])
            self.assertIsInstance(dep_info[0].version_range, VersionInfo)
            self.assertIn(
                dep_info[0].version_range.value, ["~1", ">=1.2.2 <1.2.4"])

            self.assertIn("ManPathsInfo", information_types)
            man_paths_info = extracted_information["ManPathsInfo"]
            self.assertEqual(len(man_paths_info), 1)
            self.assertEqual(man_paths_info[0].value, ["./man/foo.1", "./man/bar.1"])

            self.assertIn("IncludePathsInfo", information_types)
            include_paths_info = extracted_information["IncludePathsInfo"]
            self.assertEqual(len(include_paths_info), 1)
            self.assertEqual(include_paths_info[0].value, ["dist"])
