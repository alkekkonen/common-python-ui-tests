# -*- coding: UTF-8 -*-
from collections import Counter
from urllib.parse import urlparse, parse_qs

from behave import *
from common_python_ui_tests.steps import common_steps

from common_python_ui_tests.lib.utils.decorators import format_params

use_step_matcher('parse')


@step('I memorize current url to var "{saved_url}"')
def memorize_current_url_to_var(context, saved_url):
    context.log.info(f'URL saved: {saved_url}')
    common_steps.set_var_scenario(context, saved_url, context.driver.current_url)


@step('I follow url from var "{saved_url}"')
def follow_stored_url(context, saved_url):
    url_to_go = context.get_param('scenario', saved_url)
    context.log.info(f'URL to go: {url_to_go}')
    context.driver.get(url_to_go)


@step('query params from URL saved as array to var "{query_params}"')
def save_query_params(context, query_params):
    query = urlparse(context.driver.current_url).query
    parsed_query = parse_qs(query)
    common_steps.set_var_scenario(context, query_params, parsed_query)


@step('query params from URL equals to params from var "{query_params}"')
def save_query_params(context, query_params):
    query = urlparse(context.driver.current_url).query
    actual_values = parse_qs(query)
    expected_values = context.format(query_params)
    assert Counter(actual_values) == Counter(expected_values), \
        f'Query params are different: expected {expected_values}, {actual_values} found'


@step('current url contains "{path}"')
@format_params
def check_current_url(context, path):
    current_url = context.driver.current_url
    assert path in current_url, "Url {} does not contains {}".format(current_url, path)
