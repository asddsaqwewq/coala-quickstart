from coala_quickstart.info_extraction.Info import Info


class LicenseUsedInfo(Info):
    description = "License of the project."
    value_type = (str,)


class VersionInfo(Info):
    description = "Version range information."
    value_type = (str,)


class ProjectDependencyInfo(Info):
    description = "Dependency of the project."
    value_type = (str,)

    def __init__(self,
                 source,
                 value,
                 extractor=None,
                 version=None):
        super().__init__(source, value, extractor, version_range=version)


class PathsInfo(Info):
    description = "File path globs mentioned in the file."
    value_type = ([str],)


class IncludePathsInfo(PathsInfo):
    description = "Target files to perform analysis."


class IgnorePathsInfo(PathsInfo):
    description = "Files to ignore during analysis."


class ManPathsInfo(Info):
    description = "Related to man-pages"
