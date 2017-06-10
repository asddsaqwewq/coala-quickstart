from coala_quickstart.info_extraction.Info import Info

from dependency_management.requirements.ExecutableRequirement import (
    ExecutableRequirement)
from dependency_management.requirements.PackageRequirement import (
    PackageRequirement)


class LicenseUsedInfo(Info):
    description = "License of the project."
    value_type = [""]


class LinterUsedInfo(Info):
    description = "Linter used in project."
    value_type = ["", PackageRequirement, ExecutableRequirement]

    def __init__(self,
                 source,
                 value,
                 is_supported_by_coala=True,
                 version=None):
        super().__init__(source, value)
        self.is_supported_by_coala = is_supported_by_coala
        self.version = version


class ProjectDependencyInfo(Info):
    description = "Dependency of the project."
    value_type = ["", PackageRequirement]

    def __init__(self,
                 source,
                 value,
                 version_range=None):
        super().__init__(source, value)
        self.version_range = version_range


class PathsInfo(Info):
    description = "File path globs mentioned in the file."
    value_type = [[""]]


class IncludePathsInfo(PathsInfo):
    description = "Target files to perform analysis."
    value_type = [[""]]


class IgnorePathsInfo(PathsInfo):
    description = "Files to ignore during analysis."
    value_type = [[""]]


class ManPathsInfo(Info):
    description = "Related to man-pages"
    value_type = [[""]]


class ScriptsInfo(Info):
    description = "Other language scripts inside the file"
    value_type = ""

    def __init__(self,
                 source,
                 value,
                 script_type=None):
        super().__init__(source, value)
        self.script_type = script_type
