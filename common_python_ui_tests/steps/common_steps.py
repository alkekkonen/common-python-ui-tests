import logging

from behave import *

from common_python_ui_tests.lib.utils.decorators import format_params

log = logging.getLogger(__name__)

use_step_matcher('re')


@step('I set var "(?P<name>[^\"]+)" to "(?P<value>[^\"]+)" in "(?P<level>[^\"]+)" vars')
def set_var(context, name, value, level):
    context.add_param(level, name, context.format(value))
    context.log.info(f'Scenario var "{name}" in level, {level}, now has value: {value}')


@step('I set var "(?P<name>[^\"]+)" to "(?P<value>[^\"]+)" from config')
@format_params
def set_var_from_config(context, name, value):
    conf_val = eval('context.env_config.' + value.replace(':', '.'))
    context.add_param('scenario', name, context.format(conf_val))
    context.log.info(f'Using config param: "{value}" scenario var "{name}" now has value: {conf_val}')


@step('I set var "(?P<name>[^\"]+)" to "(?P<value>[^\"]+)"')
@format_params
def set_var_scenario(context, name, value):
    context.add_param('scenario', name, value)
    context.log.info(f'Scenario var "{name}" now has value: {value}')