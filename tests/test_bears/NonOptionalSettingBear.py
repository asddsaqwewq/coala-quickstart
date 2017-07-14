from coalib.bearlib.abstractions.Linter import linter
from dependency_management.requirements.NpmRequirement import NpmRequirement


@linter(executable='some_linter',
        output_format='regex',
        output_regex=r'.+:(?P<line>\d+):(?P<message>.*)')
class NonOptionalSettingBear:
    """
    A linter bear that wraps 'some_linter' and has non-optional settings.
    """
    LANGUAGES = {'All'}
    REQUIREMENTS = {NpmRequirement('some_linter', '2')}

    @staticmethod
    def create_arguments(filename,
                         file,
                         config_file,
                         non_optional_setting: bool,
                         another_setting: int):
        return ()
