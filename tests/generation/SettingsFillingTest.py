import os
import unittest

from pyprint.ConsolePrinter import ConsolePrinter

from coalib.bears.GlobalBear import GlobalBear
from coalib.bears.LocalBear import LocalBear
from coala_utils.ContextManagers import (
    simulate_console_inputs, retrieve_stdout)
from coalib.output.ConsoleInteraction import acquire_settings
from coalib.output.printers.LogPrinter import LogPrinter
from coalib.settings.Section import Section
from coalib.settings.Setting import Setting
from coalib.settings.SectionFilling import fill_settings
from coala_quickstart.generation.SettingsFilling import fill_section
from tests.TestUtilities import bear_test_module, generate_files


editorconfig_1 = """
[*]
indent_style = tab
end_of_line = lf
insert_final_newline = true
charset = utf-8
trim_trailing_whitespace = true
indent_size = 4
"""

editorconfig_2 = """
[*]
# This contains conflicting indent style with editorconfig_1
indent_style = space
[**/abc/]
indent_style = tab
"""


class GlobalTestBear(GlobalBear):

    def __init__(self):
        GlobalBear.__init__(self, {}, Section('irrelevant'), None)

    @staticmethod
    def get_non_optional_settings():
        return {'global name': 'global help text',
                'key': 'this setting does exist'}


class LocalTestBear(LocalBear):

    def __init__(self):
        LocalBear.__init__(self, [], '', Section('irrelevant'), None)

    @staticmethod
    def get_non_optional_settings():
        return {'local name': 'local help text',
                'global name': 'this setting is needed by two bears'}


class SettingsFillingTest(unittest.TestCase):

    def setUp(self):
        self.project_dir = os.path.dirname(os.path.realpath(__file__))
        self.log_printer = LogPrinter(ConsolePrinter())
        self.section = Section('test')
        self.section.append(Setting('key', 'val'))

    def test_fill_settings(self):
        sections = {'test': self.section}
        with simulate_console_inputs() as generator:
            fill_settings(sections,
                          acquire_settings,
                          self.log_printer,
                          fill_section_method=fill_section,
                          project_dir=self.project_dir)
            self.assertEqual(generator.last_input, -1)

        self.section.append(Setting('bears', 'SpaceConsistencyTestBear'))

        with simulate_console_inputs('True'), bear_test_module():
            local_bears, global_bears = fill_settings(
                sections, acquire_settings, self.log_printer,
                fill_section_method=fill_section, project_dir=self.project_dir)

            self.assertEqual(len(local_bears['test']), 1)
            self.assertEqual(len(global_bears['test']), 0)

        self.assertEqual(bool(self.section['use_spaces']), True)
        self.assertEqual(len(self.section.contents), 3)

    def test_fill_settings_autofill(self):
        self.section = Section('test')
        sections = {'test': self.section}

        self.section.append(Setting('bears', 'SpaceConsistencyTestBear'))

        with simulate_console_inputs() as generator, bear_test_module():
            with generate_files([".editorconfig"],
                                [editorconfig_1],
                                self.project_dir) as gen_files:
                local_bears, global_bears = fill_settings(
                    sections, acquire_settings, self.log_printer,
                    fill_section_method=fill_section,
                    project_dir=self.project_dir)

                self.assertEqual(len(local_bears['test']), 1)
                self.assertEqual(len(global_bears['test']), 0)
                # The value for the setting is automatically taken
                # from .editorconfig file.
                self.assertEqual(generator.last_input, -1)

        self.assertEqual(bool(self.section['use_spaces']), False)

    def test_fill_settings_autofill_conflicting_values(self):
        self.section = Section('test')
        sections = {'test': self.section}

        self.section.append(Setting('bears', 'SpaceConsistencyTestBear'))

        with simulate_console_inputs("False") as generator, \
                bear_test_module(), retrieve_stdout() as sio:
            with generate_files([".editorconfig"],
                                [editorconfig_2],
                                self.project_dir):
                local_bears, global_bears = fill_settings(
                    sections, acquire_settings, self.log_printer,
                    fill_section_method=fill_section,
                    project_dir=self.project_dir)

                self.assertEqual(len(local_bears['test']), 1)
                self.assertEqual(len(global_bears['test']), 0)

                prompt_msg = (
                    'coala-quickstart has detected multiple potential values '
                    'for the setting "use_spaces"')
                self.assertIn(prompt_msg, sio.getvalue())
                self.assertEqual(generator.last_input, 0)

        self.assertEqual(bool(self.section['use_spaces']), False)

    def test_fill_section(self):
        # Use the same value for both because order isn't predictable (uses
        # dict)
        with simulate_console_inputs(0, 0):
            new_section = fill_section(self.section,
                                       acquire_settings,
                                       self.log_printer,
                                       [LocalTestBear,
                                        GlobalTestBear],
                                       self.project_dir)

        self.assertEqual(int(new_section['local name']), 0)
        self.assertEqual(int(new_section['global name']), 0)
        self.assertEqual(new_section['key'].value, 'val')
        self.assertEqual(len(new_section.contents), 3)

        # Shouldnt change anything the second time
        new_section = fill_section(self.section,
                                   acquire_settings,
                                   self.log_printer,
                                   [LocalTestBear, GlobalTestBear],
                                   self.project_dir)

        self.assertTrue('local name' in new_section)
        self.assertTrue('global name' in new_section)
        self.assertEqual(new_section['key'].value, 'val')
        self.assertEqual(len(new_section.contents), 3)

    def test_dependency_resolving(self):
        sections = {'test': self.section}
        self.section['bears'] = 'DependentBear'
        with simulate_console_inputs('True'), bear_test_module():
            fill_settings(sections,
                          acquire_settings,
                          self.log_printer,
                          fill_section_method=fill_section,
                          project_dir=self.project_dir)

        self.assertEqual(bool(self.section['use_spaces']), True)
