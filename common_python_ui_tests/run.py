# -*- coding: UTF-8 -*-

import logging

import behave.configuration
import behave_r2
import sys
import time
from behave import __main__
from behave.configuration import setup_parser
from common_api_tests.lib.helper_classes import CapturedStdOut

log = logging.getLogger(__name__)

behave.configuration.options += [
    (('--env',),
     dict(help='Environment where tests are run', required=False)),
    (('--consul',),
     dict(help='Download configuration from Consul', action='store_true', required=False)),
    (('--jwt',),
     dict(help='Use given JSON Web Token', required=False)),
    (('--gui',),
     dict(help='GUI on which to perform the tests, currently support: aplus, highrespu', required=False)),
    (('--gui_version',),
     dict(help='version of GUI on which to perform the tests, to support app config section shall have version key'
               'if not specified, from the config will be taken,otherwise - override the config value', required=False)),

    (('--check-scenarios-unique',),
     dict(action='store_true',
          help='Does "dry-run" of scenarios with validation that they all have unique names')),
    (('--use_storage',),
     dict(default='astcoord',
          help='What storage tests should get files from ["astcoord", "local"].')),
    (('--do_not_clear_storage_cache',),
     dict(action='store_true')),
    (('--copy_to_local_storage',),
     dict(action='store_true')),
    (('--browser',),
     dict(help='Specify browser to use as default', required=False)),
    (('--client_type',),
     dict(help='Specify client to run via browserstack (for example, iPhone or Edge)', required=False)),
    (('--headless',),
     dict(help='Applicable to Chrome only, if specified - will run in headless mode', action='store_true')),
    (('--screenshots',),
     dict(help='Specify directory for screenshots', required=False)),
    (('--split',),
     dict(help='Split the library and put resulting files into specified dir. Dir-ry is required.', required=False)),
    (('--debug',),
     dict(help='turns on debug mode (ipdb on failed step), for use only along with "--no-capture" flag.',
          action='store_true',
          required=False)),
    (('--config_folder',),
     dict(help=' Mock config_folder', required=False)),
    (('--chrome_log',),
     dict(help='enables verbose logging from Chrome in /features/logs/chrome.json',
          action='store_true',
          required=False)),
    (('--implicit_wait',),
     dict(help='An implicit wait is to tell WebDriver to poll the DOM for a certain'
               ' amount of time when trying to find an element or elements',
          default=20, type=int,
          required=False)),
    (('--mobile_device_name',),
     dict(help='Set mobile device name. This is the additional setting for running test via mobile emulation',
          required=False)),
    (('--r2',),
     dict(help='Turns on special junit report generation. Use for R2 runs',
          action='store_true')),
    (('--has_non_pr_smoke',),
     dict(help='This flag allow to run tests without tags check. '
               'Currently tests without "smoke" and "pr" could NOT be run on prod env',
          action='store_true',
          required=False)),
    (('--binary_path',),
     dict(help='Browser Stack binary path', default='', required=False, type=str)),
]

if __name__ == '__main__':
    parsed = setup_parser().parse_args()
    if parsed.show_skipped:
        sys.argv.append('--no-skipped')
    if parsed.split:
        if not parsed.dry_run:
            sys.argv.append('--dry-run')
        st_time = time.time()
        with CapturedStdOut(parsed.split) as out:
            __main__.main()
        log.info("\n\n\n\t Lasted for {0}".format(time.time() - st_time))
    else:
        behave_r2.run_behave(parsed)
