import copy

from termcolor import colored

from coalib.bears.BEAR_KIND import BEAR_KIND
from coalib.collecting import Dependencies
from coalib.collecting.Collectors import collect_bears
from coalib.settings.Setting import Setting
from coala_quickstart.generation.InfoCollector import collect_info
from coala_quickstart.generation.InfoMapping import INFO_SETTING_MAPS
from coala_utils.string_processing.Core import join_names


def fill_settings(sections, acquire_settings, log_printer, project_dir):
    """
    Retrieves all bears and requests missing settings via the given
    acquire_settings method.

    This will retrieve all bears and their dependencies.

    :param sections:         The sections to fill up, modified in place.
    :param acquire_settings: The method to use for requesting settings. It will
                             get a parameter which is a dictionary with the
                             settings name as key and a list containing a
                             description in [0] and the names of the bears
                             who need this setting in all following indexes.
    :param log_printer:      The log printer to use for logging.
    :return:                 A tuple containing (local_bears, global_bears),
                             each of them being a dictionary with the section
                             name as key and as value the bears as a list.
    """
    local_bears = {}
    global_bears = {}

    for section_name, section in sections.items():
        bear_dirs = section.bear_dirs()
        bears = list(section.get('bears', ''))
        section_local_bears, section_global_bears = collect_bears(
            bear_dirs,
            bears,
            [BEAR_KIND.LOCAL, BEAR_KIND.GLOBAL],
            log_printer)
        section_local_bears = Dependencies.resolve(section_local_bears)
        section_global_bears = Dependencies.resolve(section_global_bears)
        all_bears = copy.deepcopy(section_local_bears)
        all_bears.extend(section_global_bears)
        fill_section(section, acquire_settings,
                     log_printer, all_bears, project_dir)

        local_bears[section_name] = section_local_bears
        global_bears[section_name] = section_global_bears

    return local_bears, global_bears


def fill_section(section, acquire_settings, log_printer, bears, project_dir):
    """
    Retrieves needed settings from given bears and asks the user for
    missing values.

    If a setting is requested by several bears, the help text from the
    latest bear will be taken.

    :param section:          A section containing available settings. Settings
                             will be added if some are missing.
    :param acquire_settings: The method to use for requesting settings. It will
                             get a parameter which is a dictionary with the
                             settings name as key and a list containing a
                             description in [0] and the names of the bears
                             who need this setting in all following indexes.
    :param log_printer:      The log printer for logging.
    :param bears:            All bear classes or instances.
    :return:                 The new section.
    """
    # Retrieve needed settings.
    prel_needed_settings = {}
    for bear in bears:
        needed = bear.get_non_optional_settings()
        for key in needed:
            if key in prel_needed_settings:
                prel_needed_settings[key].append(bear.name)
            else:
                prel_needed_settings[key] = [needed[key][0],
                                             bear.name]

    # Strip away existent settings.
    needed_settings = {}
    for setting, help_text in prel_needed_settings.items():
        if setting not in section:
            needed_settings[setting] = help_text

    # Fill the settings with existing values if possible
    extracted_info = collect_info(project_dir)
    satisfied_settings = []

    for setting in needed_settings.keys():
        to_fill_values = list(autofill_value_if_possible(
            setting, section.name, needed_settings[setting][1:],
            extracted_info))

        if len(set(to_fill_values)) == 1:
            section[setting] = to_fill_values[0]
            satisfied_settings.append(setting)

        elif len(to_fill_values) > 1:
            section[setting] = resolve_anomaly(setting,
                                               needed_settings[setting][0],
                                               needed_settings[setting][1:],
                                               to_fill_values)
            satisfied_settings.append(setting)

        else:
            pass

    for setting in satisfied_settings:
        del needed_settings[setting]

    # Get missing ones.
    if len(needed_settings) > 0:
        new_vals = acquire_settings(log_printer, needed_settings, section)
        for setting, help_text in new_vals.items():
            section.append(Setting(setting, help_text))

    return section


def autofill_value_if_possible(setting_key,
                               section_name,
                               bear_name,
                               extracted_information):
    """
    For the given setting configurations, checks if there is a
    possiblity of filling the value from the extracted information,
    and returns the values if these value are applicable.
    """
    if INFO_SETTING_MAPS.get(setting_key):
        for mapping in INFO_SETTING_MAPS[setting_key]:
            scope = mapping["scope"]
            if (scope.check_belongs_to_scope(
                    section_name, bear_name)):
                # look for the values in extracted information
                # from all the ``InfoExtractor`` instances.
                values = extracted_information.get(
                    mapping["info_kind"].__name__)
                if values:
                    for val in values:
                        if scope.check_is_applicable_information(val):
                            yield mapping["mapper_function"](val)
    return None


def is_autofill_possible(setting_key,
                         section_name,
                         bear_name,
                         extracted_info):
    """
    Checks if it is possible to autofill the setting values.
    """
    if INFO_SETTING_MAPS.get(setting_key):
        for mapping in INFO_SETTING_MAPS[setting_key]:
            scope = mapping["scope"]
            if (scope.check_belongs_to_scope(
                    section_name, bear_name)):
                values = extracted_info.get(
                    mapping["info_kind"].__name__)
                for val in values:
                    if scope.check_is_applicable_information(val):
                        return True
    return False


def resolve_anomaly(setting_name,
                    help_string,
                    associated_bears,
                    values):
    """
    Displays multiple possible values for the setting
    to the users and prompts them for actual value to be
    used.
    """
    values = list(set(values))

    STR_ASK_FOR_CORRECT_VALUE = ('coala-quickstart has detected multiple '
                                 'potential values for the setting "{}" ({}) '
                                 'needed by {}. The detected values are: {}.\n'
                                 'Please provide the correct value to use:')
    REPORT_ANOMALY_COLOR = 'green'

    print(colored(STR_ASK_FOR_CORRECT_VALUE.format(setting_name,
                                                   help_string,
                                                   join_names(associated_bears),
                                                   join_names(values)),
                  REPORT_ANOMALY_COLOR))
    return input()
