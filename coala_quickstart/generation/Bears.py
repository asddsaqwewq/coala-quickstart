import copy
import re

from pyprint.NullPrinter import NullPrinter

from coala_quickstart.Constants import IMPORTANT_BEAR_LIST
from coala_quickstart.Strings import BEAR_HELP
from coala_quickstart.generation.InfoCollector import collect_info
from coala_quickstart.generation.SettingsFilling import is_autofill_possible
from coalib.settings.ConfigurationGathering import get_filtered_bears
from coalib.misc.DictUtilities import inverse_dicts
from coalib.output.printers.LogPrinter import LogPrinter


def filter_relevant_bears(used_languages,
                          project_dir,
                          printer,
                          arg_parser=None):
    """
    From the bear dict, filter the bears per relevant language.

    :param used_languages:
        A list of tuples with language name as the first element
        and percentage usage as the second element; sorted by
        percentage usage.
    :return:
        A dict with language name as key and bear classes as value.
    """
    log_printer = LogPrinter(NullPrinter())
    used_languages.append(("All", 100))

    bears_by_lang = {
        lang: set(inverse_dicts(*get_filtered_bears([lang],
                                                    log_printer,
                                                    arg_parser)).keys())
        for lang, _ in used_languages
    }

    # Each language would also have the language independent bears. We remove
    # those and put them in the "All" category.
    all_lang_bears = bears_by_lang["All"]
    bears_by_lang = {lang: bears_by_lang[lang] - bears_by_lang["All"]
                     for lang, _ in used_languages}
    bears_by_lang["All"] = all_lang_bears

    extracted_info = collect_info(project_dir)

    selected_bears = {}
    candidate_bears = copy.copy(bears_by_lang)
    to_propose_bears = {}

    # Initialize selected_bears with IMPORTANT_BEAR_LIST
    for lang, lang_bears in candidate_bears.items():
        if lang_bears and lang in IMPORTANT_BEAR_LIST:
            selected_bears[lang] = []
            for bear in lang_bears:
                if bear.__name__ in IMPORTANT_BEAR_LIST[lang]:
                    selected_bears[lang].append(bear)
        if lang_bears and lang not in IMPORTANT_BEAR_LIST:
            selected_bears[lang] = lang_bears

        candidate_bears[lang] = [bear for bear in lang_bears
                                 if selected_bears.get(lang) and
                                 bear not in selected_bears[lang]]

    project_dependency_info = extracted_info["ProjectDependencyInfo"]

    # Use project_dependency_info to propose bears to user.
    for lang, lang_bears in candidate_bears.items():
        matching_dep_bears = get_bears_with_matching_dependencies(
            lang_bears, project_dependency_info)
        to_propose_bears[lang] = set(matching_dep_bears)
        bears_to_remove = [match for match in matching_dep_bears]
        candidate_bears[lang] = [bear for bear in candidate_bears[lang]
                                 if bear not in bears_to_remove]

    for lang, lang_bears in to_propose_bears.items():
        for bear in lang_bears:
            # get the non-optional settings of the bears
            settings = bear.get_non_optional_settings()
            if not settings:
                # no non-optional setting, select it right away!
                selected_bears[lang].append(bear)
            else:
                user_input_reqd = False
                for setting in settings:
                    if not is_autofill_possible(
                            extracted_info, setting.key, lang, bear):
                        user_input_reqd = True

                args = arg_parser.parse_args()

                if user_input_reqd:
                    # Ask user to activate the bear
                    if (not args.non_interactive and
                            prompt_to_activate(bear, printer)):
                        selected_bears[lang].add(bear)
                else:
                    # All the non-optional settings can be filled automatically
                    selected_bears[lang].add(bear)

    return selected_bears


def get_non_optional_settings(bears):
    """
    From the bear dict, get the non-optional settings.

    :param bears:
        A dict with language name as key and bear classes as value.
    :return:
        A dict with Bear class as key and bear non-optional settings as value.
    """
    non_optional_settings = {}
    for language in bears:
        for bear in bears[language]:
            if bear not in non_optional_settings:
                needed = bear.get_non_optional_settings()
                # FIXME: This only finds non-optional settings for immediate
                # dependencies.  See https://github.com/coala/coala/issues/3149
                for bear_dep in bear.BEAR_DEPS:
                    needed.update(bear_dep.get_non_optional_settings())

                non_optional_settings[bear] = needed

    return non_optional_settings


def get_non_optional_settings_bears(bears):
    """
    Return tuple of bears with non optional settings.

    :param unusable_bears:
        A collection of Bear classes.
    """
    non_optional_settings = get_non_optional_settings(bears)
    non_optional_settings = tuple(bear for bear, settings
                                  in non_optional_settings.items()
                                  if settings)
    return non_optional_settings


def remove_unusable_bears(bears, unusable_bears):
    """
    From the bears dict, filter the bears appearing in unusable_bears.

    :param bears:
        A dict with language name as key and bear classes as value.
    :param unusable_bears:
        A collection of Bear classes.
    """
    for language, language_bears in bears.items():
        for bear in tuple(language_bears):
            if bear in unusable_bears:
                bears[language].remove(bear)


def print_relevant_bears(printer, relevant_bears, label='relevant'):
    """
    Prints the relevant bears in sections separated by language.

    :param printer:
        A ``ConsolePrinter`` object used for console interactions.
    :param relevant_bears:
        A dict with language name as key and bear classes as value.
    """
    if label == 'relevant':
        printer.print(BEAR_HELP)

    printer.print("\nBased on the languages used in project the following "
                  "bears have been identified to be %s:" % label)
    for language in relevant_bears:
        printer.print("    [" + language + "]", color="green")
        for bear in relevant_bears[language]:
            printer.print("    " + bear.name, color="cyan")
        printer.print("")


def generate_requirements_map(bears):
    """
    For the given list of bears, returns a dict of the form
    ```
    {
        “requirement_name” : {
            “requirement_type” : NpmRequirement,
            "version" : ">=0.4.2"
            “bear” : "bear_wrapping_the_executable",
        }
    }
    ```
    """
    requirements_meta = {}
    for bear in bears:
        for req in bear.REQUIREMENTS:
            to_add = {
                "bear": bear,
                "version": req.version,
                "type": req.type
            }
            requirements_meta[req.package] = to_add
    return requirements_meta


def get_bears_with_matching_dependencies(bears, dependency_info):
    """
    Matches the `REQUIREMENTS` filed of bears against a list
    of ``ProjectDependencyInfo`` instances.

    Return a list of the tuples of the form
    (bear, ProjectDependencyInfoInstance)
    """
    requirements_map = generate_requirements_map(bears)
    matched_requirements = []
    for req, req_info in requirements_map.items():
        for dep in dependency_info:
            # Check if names of requirements match
            if dep.value == req:
                installed_version = dep.version.value
                bear_requirement_version = req_info["version"]
                if installed_version and bear_requirement_version:
                    is_newer_version = is_version_newer(
                        installed_version, bear_requirement_version)
                    if is_newer_version:
                        matched_requirements.append(req)
                else:
                    # No comparison can be made as the info is missing
                    matched_requirements.append(req)

    result = []
    for bear in bears:
        all_req_satisfied = True
        for req in bear.REQUIREMENTS:
            if req.package not in matched_requirements:
                all_req_satisfied = False
        if bear.REQUIREMENTS and all_req_satisfied:
            result.append(bear)
    return result


def is_version_newer(semver1, semver2):
    """
    :returns:
        True if semver1 is latest or matches semver2,
        False otherwise.
    """
    semver1 = tuple(map(int, (re.sub("[^0-9\.]", "", semver1).split("."))))
    semver2 = tuple(map(int, (re.sub("[^0-9\.]", "", semver2).split("."))))
    return semver1 >= semver2


def prompt_to_activate(bear, printer):
    """
    Prompts the user to activate a bear.
    """
    PROMPT_TO_ACTIVATE_STR = ("coala-quickstart has found {} to be useful "
                              "based of dependencies discovered from your "
                              "project files. \n Would you like to activate "
                              "it? (y/n)")
    printer.print(PROMPT_TO_ACTIVATE_STR)

    choice = input().lower()

    if choice.startswith('y'):
        return True
    elif choice.startswith('n'):
        return False
    else:
        return prompt_to_activate(bear)
