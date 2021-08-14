from behave import step, use_step_matcher
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from common_python_ui_tests.lib.utils.decorators import format_params

use_step_matcher('parse')


@step('I execute js "{js}" in browser')
@format_params
def execute_js_script(context, js):
    context.log.info(f'Excecuting js in browser:\n{js}')
    context.driver.execute_script(js)


@step('I set listener for {event} js event')
@format_params
def set_event_listener(context, event):
    js_to_execute = 'addEventListener("' + event + '", (e) => {alert("' + event + '");});true;'
    context.log.info(f"Executing JS: {js_to_execute}")
    context.driver.execute_script(js_to_execute)


@step('I see alert that {event} js event happened')
@format_params
def see_and_accept_event_alert(context, event):
    alert = WebDriverWait(context.driver, 30).until(
        EC.alert_is_present(), "Timeout for alert to be present")
    assert alert.text == event, f'Given event name not equals to expected. \n Expected:{alert.text} \n Given:{event}'
    alert.accept()


@step('I accept alert')
def accept_alert(context):
    alert = WebDriverWait(context.driver, 5).until(
        EC.alert_is_present(), "Timeout for alert to be present")
    alert.accept()
