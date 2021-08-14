from selenium.webdriver.common.by import By

from common_python_ui_tests.lib.base_page import BasePage


class HubLoginPage(BasePage):
    USERNAME_INPUT = (By.NAME, 'username')
    PASSWORD_INPUT = (By.NAME, 'password')
    LOGIN_FORM = (By.CSS_SELECTOR, '#loginbox')
    LOGIN_BUTTON = (By.CSS_SELECTOR, '#form_0')
    LOGIN_ERROR = (By.CSS_SELECTOR, '#invalidNameOrPass')

    def appears(self):
        self.element_is_visible(self.LOGIN_FORM)
        return self

    def login(self, username, password):
        self.fill(username, *self.USERNAME_INPUT)
        self.fill(password, *self.PASSWORD_INPUT)
        self.click_element(*self.LOGIN_BUTTON)
        return self

    def login_error_displayed_with_text(self, expected_text):
        notification = self.driver.find_element(*self.LOGIN_ERROR)
        assert notification.text.strip() == expected_text, "'{}' value found instead of '{}' expected" \
            .format(notification.text, expected_text)
        return notification.is_displayed()
