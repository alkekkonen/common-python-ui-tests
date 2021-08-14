# -*- coding: UTF-8 -*-

import logging
import os
import random
import re
import traceback
import time
import types
import uuid
from datetime import datetime

import yaml
from common_python_ui_tests.lib.file_storage.external_storage import ExternalStorage
from common_python_ui_tests.lib.file_storage.storage import Storage
from common_python_ui_tests.lib.file_storage.storage import LocalStorage
from requests import HTTPError
from selenium.common.exceptions import WebDriverException

from common_python_ui_tests.config import initialize_config
from common_python_ui_tests.lib.browser import WebDriverProvider, IEWebDriverProvider
from common_python_ui_tests.lib.utils.dicts import FlatDict

EXTERNAL_CACHE_LOCATION = os.path.join(os.getcwd(), 'features', 'data', 'storage', 'external')
LOCAL_STORAGE_LOCATION = os.path.join(os.getcwd(), 'features', 'data', 'storage', 'local')


#
# Feature methods
#


def before_all(context):
    try:
        context.log = logging.getLogger()
        context.suppress_logging = False

        add_property(context, 'table_params', table_params)
        add_property(context, 'text_params', text_params)
        add_property(context, 'table_first', table_first)
        add_property(context, 'action_params', action_params)
        add_property(context, 'outline_params', outline_params)
        add_property(context, 'all_params', all_params)
        add_property(context, 'params_format', params_format)

        add_function(context, 'format', apply_format)
        add_function(context, 'format_dict', format_dict)
        add_function(context, 'add_param', add_param)
        add_function(context, 'get_param', get_param)
        add_function(context, 'eval', context_eval)

        context.env_config = initialize_config(env=context.config.env,
                                               use_consul=context.config.consul,
                                               jwt=context.config.jwt)

        context.params_top = {}
        context.params_feature = {}
        context.params_scenario = {}

        context.params_top['file_storage_url'] = context.env_config.aws_storage_url
        context.params_top['hook_server_url'] = context.env_config.hook_server_url
        context.params_top['default_user'] = context.env_config.default_user
        context.params_top['str256'] = 'x' * 256
        context.params_top['str255'] = 'x' * 255
        context.global_implicit_wait_time = context.config.implicit_wait
        context.app = None

        context.http_options = {'verify_ssl': not context.env_config.ignore_ssl}

        if context.config.use_storage == 'local':
            Storage.init(LocalStorage(LOCAL_STORAGE_LOCATION))
        else:
            Storage.init(ExternalStorage(EXTERNAL_CACHE_LOCATION))
            if not context.config.do_not_clear_storage_cache:
                Storage.clear_cache()
            if context.config.copy_to_local_storage:
                Storage.instance.backup_folder = LOCAL_STORAGE_LOCATION
    except Exception:
        traceback.print_exc()
        raise


def after_all(context):
    pass


def before_feature(context, feature):
    context.params_feature = {}
    context.feature_short_name = short_name(context.feature.filename)
    context.i18n_api = True if 'i18n_api' in context.feature.tags else False
    init_feature_logging(context, feature)


def after_feature(context, feature):
    deinit_feature_logging(context, feature)


def before_scenario(context, scenario):
    if context.config.browser in {'ie', 'internet_explorer'}:
        driver_provider = IEWebDriverProvider
    else:
        driver_provider = WebDriverProvider
    use_driver_proxy = True if 'driver_proxy' in scenario.effective_tags else False
    use_browser_stack = True if context.config.browser == 'browser_stack' else False
    if use_browser_stack:
        binary_path = context.config.binary_path
        context.env_config.browser = "browser-stack"
        context.env_config.client_type = context.config.client_type
        context.env_config.browser_stack.binary_path = binary_path
        context.env_config.headless = False
        tags = scenario.effective_tags[1:]
        for client_name, client in context.env_config.browser_stack.desired_capabilities.items():
            current_date = datetime.now()
            client["name"] = "/".join(tags)
            client["build"] = f'{client["build"]} {current_date.year}-{current_date.month}-{current_date.day}'
        driver = driver_provider(context.env_config, use_driver_proxy)
    else:
        driver = driver_provider(context.config, use_driver_proxy)
    context.driver = driver.prepare_options().create_driver().get_instance()
    context.log.info('BROWSER: {}'.format(context.driver))

    context.current = None
    context.bookmarks = {}
    context.params_scenario = {}
    context.pre_saved = {}
    context.additional_browsers = {}

    # Declare any params you desire, like:
    scenario.my_param = random.randint(10 ** 8, 10 ** 9 - 1)  # Just an example
    scenario.uuid = uuid.uuid4()

    # Set any params you desire, like:
    context.params_scenario['my_param'] = scenario.my_param
    context.params_scenario['uuid'] = scenario.uuid

    context.scenario_short_name = short_name(context.scenario.name)
    context.log.info('Starting scenario [{0.name}] with rnd {0.rnd}'.format(scenario))


def before_step(context, st):
    context.log.info('ENTERING STEP: {step}'.format(step=st.name))


def after_step(context, st):
    context.log.info(f'{st.status} STEP: {st.name}')
    if st.status == 'failed':
        context.last_occured_exception = st.exception
        if not context.suppress_logging:
            context.log.error(f'Error Message: {st.exception}')
        if hasattr(context, 'driver'):
            full_path = os.path.join(
                context.log_dir, '{}{}{}'.format(
                    time.strftime('%Y_%m_%d_%H_%M_%S-'),
                    'failed_screenshot', '.png'))
            context.driver.get_screenshot_as_file(full_path)
            context.log.info("SCREENSHOT: {}".format(full_path))
    if context.env_config.get('screenshots', False) and ('driver' in context) and (
            'selenium.webdriver' in str(type(context.driver))):
        full_path = os.path.join(
            context.env_config.screenshots,
            time.strftime('%Y_%B_%d_%H_%M_%S-') + st.name.replace(' ', '_') + '.png')
        context.driver.get_screenshot_as_file(full_path)


def after_scenario(context, scenario):
    if hasattr(context, 'driver'):
        # Close browser
        context.driver.close()
        for browser in context.additional_browsers.values():
            try:
                browser.close()
            except WebDriverException:
                context.log.info('Could not close additional browser')

    if scenario.status is not 'passed':
        if _error_on_server_side(context):
            if hasattr(context, 'client') and context.client is not None:
                healthcheck = None
                try:
                    healthcheck = context.client.healthcheck()
                except Exception as exc:
                    context.log.info("Can't get healthcheck due to exception: {}".format(exc.message))
                    print("Can't get healthcheck due to exception: {}".format(exc.message))
                if healthcheck is not None:
                    context.log.info(healthcheck)
                    print(healthcheck)
            else:
                context.log.info("Client is not created, so healthcheck is unavailable.")
                print("Client is not created, so healthcheck is unavailable.")
    # httplib.HTTPConnection.debuglevel = 0
    context.log.info('Finished scenario [{0.name}]\n\n\t\t*****************************\n'.format(scenario))
    context.driver.quit()


def _error_on_server_side(context):
    return (hasattr(context, 'last_occured_exception')
            and isinstance(context.last_occured_exception, HTTPError)
            and context.last_occured_exception.response.status_code >= 500)


#
# Help methods
#

def init_feature_logging(context, feature):
    log_dir = os.path.abspath(os.path.dirname('./features/logs/'))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    context.log_dir = log_dir
    ft = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s', '%m/%d/%Y %I:%M:%S %p')
    fh = logging.FileHandler(os.path.join(log_dir, '{}.log'.format(context.feature_short_name)), mode='w+',
                             encoding='utf8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(ft)

    context.log_fh = fh
    context.log.addHandler(fh)

    sth = context.log.handlers[0]
    context.log_sth = sth
    context.log.removeHandler(sth)
    context.log.addHandler(context.log_sth)


def deinit_feature_logging(context, feature):
    context.log.removeHandler(context.log_fh)
    context.log.addHandler(context.log_sth)


def short_name(long_name):
    return '_'.join(x.strip('_') for x in re.split('\W+', long_name))[:100].lower()


def table_params(context):
    return context.table and [{key: context.format(value) for key, value in row.as_dict().items()} for row in
                              context.table]


def outline_params(context):
    return {key: value for key, value in context.active_outline.as_dict().items()}


def text_params(context):
    return apply_format(context, str(context.text))


def table_first(context):
    return context.table_params and context.table_params[0]


def action_params(context):
    return FlatDict(context.table_first or text_params(context) or {})


def all_params(context):
    result = context.action_params
    result.update(context.outline_params)
    return result


def add_param(context, level, name, value):
    getattr(context, 'params_{}'.format(level))[name] = value


def get_param(context, level, name):
    return getattr(context, 'params_{}'.format(level))[name]


def context_eval(context, expr, level=None):
    params = getattr(context, 'params_{}'.format(level)) if level else context.params_format
    try:
        return eval(expr, {}, params)
    except (NameError, SyntaxError):
        return None


def params_format(context):
    params = {}
    params.update(context.params_top)
    params.update(context.params_feature)
    params.update(context.params_scenario)

    return params


def apply_format(context, obj):
    if isinstance(obj, str) and obj == 'None':
        return None
    # TODO condition was added for check_entity_with_link_that_has_or_has_no_substring_in_url
    # because context.format(' no ') returns boolean value False, not 'no'
    elif isinstance(obj, str) and obj.strip() == 'no':
        return 'no'
    # "NO" is a valid yaml  (yaml.load("NO") -> False) so we should escape this case. Example CS-5635
    elif isinstance(obj, str) and obj == 'NO':
        return 'NO'
    elif obj == '':
        return obj
    elif isinstance(obj, str) and obj.strip() == '':
        return obj
    elif obj is None:
        return obj
    elif isinstance(obj, (str, dict)):
        obj = str(obj)
        obj = replace_placeholders(obj, context.params_format)
        try:
            res = yaml.load(obj)
            return res
        except:
            return obj
    elif isinstance(obj, list):
        return [apply_format(context, x) for x in obj]
    else:
        raise NotImplemented('Incorrect variable call. Should be something '
                             'like I get "<{var_name}>" item')


def replace_placeholders(obj, params):
    pattern = '\<{([^>]+)\}>'
    items = re.finditer(pattern, obj)
    for item in items:
        assert item.group(0)[2:-2] in params.keys() or \
               item.group(0)[2:-2].split('.')[0] in params.keys(), \
            f'There is NO variable "{item.group(0)[2:-2]}" in context params'
        value = item.group(0).strip("<>").format(**params)
        item_string = item.group(0)
        if isinstance(item_string, str):
            item_string = item_string.replace('[', '\[').replace(']', '\]')
        obj = re.sub(item_string, str(value), obj)
    return obj


def add_property(inst, name, method):
    cls = type(inst)
    setattr(cls, name, property(method))


def add_function(inst, name, method):
    setattr(inst, name, types.MethodType(method, inst))


def format_text(text, kwargs):
    pattern = '<{{{0}}}>'
    for key, value in kwargs.items():
        text = re.sub(pattern.format(key), str(value), text)
    return text


def format_dict(node, params):
    def is_enumerable(node):
        return isinstance(node, list) or isinstance(node, dict)

    def is_str(node):
        return isinstance(node, str)

    def enum(node):
        if isinstance(node, list):
            return enumerate(node)
        elif isinstance(node, dict):
            return node.items()
        else:
            raise Exception('Cannot create enum for node that is not a list {0}'.format(node))

    def format(strr):
        return strr.format(**params)

    for key, value in enum(node):
        if is_enumerable(value):
            format_dict(value, params)
        elif is_str(value):
            node[key] = format(value)

    return node
