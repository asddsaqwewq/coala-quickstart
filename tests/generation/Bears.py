import os
import sys
import unittest
from copy import deepcopy

from pyprint.ConsolePrinter import ConsolePrinter
from coalib.output.printers.LogPrinter import LogPrinter
from coala_utils.ContextManagers import retrieve_stdout
from coala_quickstart.generation.Bears import (
    filter_relevant_bears, print_relevant_bears)
from coala_quickstart.coala_quickstart import main


class TestBears(unittest.TestCase):

    def setUp(self):
        self.printer = ConsolePrinter()
        self.log_printer = LogPrinter(self.printer)
        self.old_argv = deepcopy(sys.argv)
        del sys.argv[1:]

    def tearDown(self):
        sys.argv = self.old_argv

    def test_filter_relevant_bears(self):
        res = filter_relevant_bears([('Python', 70), ('C', 20)])
        self.assertIn("C", res)
        self.assertIn("Python", res)
        self.assertTrue(len(res["C"]) > 0)
        self.assertTrue(len(res["Python"]) > 0)

    def test_print_relevant_bears(self):
        with retrieve_stdout() as custom_stdout:
            print_relevant_bears(self.printer, filter_relevant_bears(
                [('Python', 70), ('Unknown', 30)]))
            self.assertIn("PycodestyleBear", custom_stdout.getvalue())

    def test_bears_allow_incomplete_sections_mode(self):
        sys.argv.append('--ci')
        sys.argv.append('--allow-incomplete-sections')
        orig_cwd = os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir("bears_ci_testfiles")
        with retrieve_stdout() as custom_stdout:
            main()
            self.assertNotIn("usable", 
                custom_stdout.getvalue())
        os.remove('.coafile')
        os.chdir(orig_cwd) 

    def test_bears_ci_mode(self):
        sys.argv.append('--ci')
        orig_cwd = os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir("bears_ci_testfiles")
        with retrieve_stdout() as custom_stdout:
            main()
            self.assertIn("usable", 
                custom_stdout.getvalue())
        os.remove('.coafile')
        os.chdir(orig_cwd)   
