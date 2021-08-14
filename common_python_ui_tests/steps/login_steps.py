# -*- coding: UTF-8 -*-
import time
from behave import step, use_step_matcher

from common_python_ui_tests.lib.apps.Pages import Pages

use_step_matcher('re')


# NOTE: If you use this framework as an external lib, move this step into your project
@step('I go to the (?P<page>[^\"]+) of \"(?P<app_name>[^\"]+)\"(?:| with query params \"(?P<params>[^\"]+)\")')
def go_to_ui_page(context, page, app_name=None, params=None):
    app_name = app_name or context.env_config.get('default_app_name')
    Pages.set_up(context, app_name)
    context.app_name = app_name
    ui_config_section = context.env_config.get(app_name)
    ui_endpoint = ui_config_section.get(page)
    gui_version = context.config.gui_version or getattr(ui_config_section, 'version', '')
    url = ui_endpoint.format(version=gui_version)
    if params:
        params_dict = get_query_params_from_config(params, ui_config_section)
        url = get_url_with_params(url, params_dict)
    context.log.info(f'URL to go: {url}')
    context.driver.get(url)


# Page Object login step (uses default common_pages set up from common_pages.py)
@step('I log in as \"(?P<user>[^\"]+)\" user(?: with \"(?P<password>[^\"]+)\" password|)')
def log_in_as_user(context, user, password=None):
    user_creds = find_user_credentials(context.env_config, context.app_name, user)
    user_name = user_creds[0]
    password = password or user_creds[1]
    context.login_page.login(username=user_name, password=password)


@step('I log in via User Portal as \"(?P<user>[^\"]+)\" (?:staff user|user)(?: with "(?P<password>[^\"]+)" password|)')
def log_into_portal_as_user(context, user, password=None):
    credentials = get_user_credentials(context, user, password)
    if 'staff' in user:
        context.login_page.switch_role()
        # Step expects that staff name in env config has format "<user's Id> + '_staff'"
        doctor_name = user.split('_staff')[0]
        context.staff_login_page.appears() \
            .login(doctor_name=doctor_name, staff_name=credentials[0], password=credentials[1])
    else:
        context.login_page.login(username=credentials[0], password=credentials[1])


@step('I logged successfully')
def successful_login_check(context):
    context.main_page.appears()


@step('login error displayed with text "(?P<expected_text>[^\"]+)"')
def login_error_displayed_with_text(context, expected_text):
    context.login_page.login_error_displayed_with_text(expected_text)


@step('application access error displayed')
def login_error_displayed(context):
    context.access_error_page.appears()


@step('I log out from error page')
def return_to_shub(context):
    context.access_error_page.logout()
    context.login_page.appears()


@step('I log out')
def logging_out(context):
    context.main_page.logout()
    context.login_page.appears()


@step('I wait "(?P<duration>[\d]+)" seconds')
def wait_for(context, duration):
    context.log.info('Start time {}'.format(time.time()))
    time.sleep(int(duration))


def get_user_credentials(context, user, password=None):
    user_creds = find_user_credentials(context.env_config, context.app_name, user)
    return user_creds[0], password or user_creds[1]


def find_user_credentials(config, app_name, user):
    user_name = user
    password = 'default_password'  # Make sure it's not a bad idea for your case
    user_config = config.get(app_name).get(user) or config.get(user)
    if user_config:
        assert len(user_config) >= 2, 'Invalid user config value. Expected at least 2 elements'
        return user_config
    return user_name, password
