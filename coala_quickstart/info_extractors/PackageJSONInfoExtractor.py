import json

from coala_quickstart.info_extraction.InfoExtractor import InfoExtractor
from coala_quickstart.info_extraction.Information import (
    LicenseUsedInfo, ProjectDependencyInfo, IncludePathsInfo, ManPathsInfo)


class PackageJSONInfoExtractor(InfoExtractor):
    supported_files = "package.json"
    supported_information_kinds = [
        LicenseUsedInfo,
        ProjectDependencyInfo,
        IncludePathsInfo,
        ManPathsInfo]

    def parse_file(self, file_content):
        return json.loads(file_content)

    def find_information(self, fname, parsed_file):
        results = []

        if parsed_file.get("license"):
            results.append(
                LicenseUsedInfo(fname, parsed_file["license"]))

        if parsed_file.get("dependencies"):
            for package_name, version_range in (
                    parsed_file["dependencies"].items()):
                results.append(
                    ProjectDependencyInfo(fname, package_name, version_range))

        if parsed_file.get("files"):
            results.append(
                IncludePathsInfo(fname, parsed_file["files"]))

        if parsed_file.get("man"):
            results.append(
                ManPathsInfo(fname, parsed_file["man"]))

        return results
