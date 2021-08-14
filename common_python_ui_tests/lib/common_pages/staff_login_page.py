from selenium.webdriver.common.by import By

from common_python_ui_tests.lib.common_pages.customer_login_page import CustomerLoginPage


class StaffLoginPage(CustomerLoginPage):
    STAFF_USERNAME_INPUT = (By.NAME, 'staffname')
    SWITCH_ROLE_BUTTON = (By.ID, 'doctorLogin')

    def appears(self):
        self.element_is_visible(self.LOGIN_FORM)
        self.element_is_visible(self.STAFF_USERNAME_INPUT)
        return self

    def login(self, doctor_name, staff_name, password):
        self.fill(doctor_name, *self.USERNAME_INPUT)
        self.fill(staff_name, *self.STAFF_USERNAME_INPUT)
        self.fill(password, *self.PASSWORD_INPUT)
        self.click_element(*self.LOGIN_BUTTON)
        return self

    def switch_role(self):
        self.click_element(*self.SWITCH_ROLE_BUTTON)
        return self
