from common_python_ui_tests.lib.common_pages.customer_login_page import CustomerLoginPage
from common_python_ui_tests.lib.common_pages.hub_login_page import HubLoginPage
from common_python_ui_tests.lib.common_pages.widgets.calendar_widget import CalendarWidget


class Pages:
    '''
    Pages class sets up pages of current app. Current app can be set via 'go_to_ui_page' step.
    Add another 'app_name' values is necessary
    NOTE: If you use this framework as an external lib, move this class into your project
    '''

    def __init__(self, context, app_name):
        self.app_name = app_name
        self.driver = context.driver  # Can be removed

    def set_up(context, app_name):
        if app_name == 'your_app':
            context.login_page = HubLoginPage(context.driver)
            context.staff_login_table = CustomerLoginPage(context.driver)
            context.main_page = MainPage(context.driver)  # Here should be the object of your app's main page
            context.calendar_widget = CalendarWidget(context.driver)
        else:
            raise ValueError(f"Unknown app: '{app_name}'")
