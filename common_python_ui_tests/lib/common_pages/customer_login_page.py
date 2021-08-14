from common_python_ui_tests.lib.base_page import BasePage
from selenium.webdriver.common.by import By


class CustomerLoginPage(BasePage):
    LOGIN_FORM = (By.CSS_SELECTOR, '.title-Login')
    USERNAME_INPUT = (By.NAME, 'username')
    PASSWORD_INPUT = (By.NAME, 'password')
    SEARCH_INPUT = (By.NAME, 'search')
    REMEMBER_ME_CHECKBOX = (By.NAME, 'rememberUsername')
    LOGIN_BUTTON = (By.CLASS_NAME, 'loginActionButton')
    LOGIN_ERROR = (By.CSS_SELECTOR, '#invalidNameOrPass')
    SWITCH_ROLE_BUTTON = (By.CSS_SELECTOR, '.staff-role')
    PROVIDER_LINK = (By.ID, 'providerLink')
    FORGOT_LINK = (By.ID, 'forgot')


    def appears(self):
        self.element_is_visible(self.LOGIN_FORM)
        self.element_is_visible(self.SEARCH_INPUT)
        return self

    def login(self, username, password):
        self.fill(username, *self.USERNAME_INPUT)
        self.fill(password, *self.PASSWORD_INPUT)
        self.click_element(*self.LOGIN_BUTTON)
        return self

    def switch_role(self):
        self.click_element(*self.SWITCH_ROLE_BUTTON)
        return self

    def login_error_displayed_with_text(self, expected_text):
        notification = self.driver.find_element(*self.LOGIN_ERROR)
        assert notification.text.strip() == expected_text, "'{}' value found instead of '{}' expected" \
            .format(notification.text, expected_text)
        return notification.is_displayed()
