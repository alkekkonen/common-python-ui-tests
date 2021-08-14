from abc import ABCMeta, abstractmethod

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys

from common_python_ui_tests.lib.utils.waiters import Waiters


class BasePage(metaclass=ABCMeta):
    def __init__(self, driver):
        self.driver = driver

    @abstractmethod
    def appears(self):
        """Must be implemented for all inherited page objects"""

    def open_page(self, address):
        self.driver.get(address)

    def get_page_title(self):
        return self.driver.title

    def click_element(self, *locator):
        try:
            self.driver.find_element(*locator).click()
        except TimeoutException:
            pass

    def get_element_by_order(self, *locator, order):
        elements_list = self.driver.find_elements(*locator)
        return elements_list[order - 1]

    def clear_input(self, *locator):
        self.driver.find_element(*locator).send_keys(Keys.CONTROL, "a", Keys.BACKSPACE)

    def fill(self, text, *locator):
        self.clear_input(*locator)
        self.driver.find_element(*locator).send_keys(text)

    def get_element_text(self, *locator):
        return self.driver.find_element(*locator).text

    def is_element_enabled(self, *locator):
        return self.driver.find_element(*locator).is_enabled()

    def element_is_visible(self, element, time_to_wait=10):
        Waiters.wait_visible(self.driver, timeout=time_to_wait, locator=element)

    def element_disappeared(self, element, time_to_wait=10):
        Waiters.wait_disappear(self.driver, timeout=time_to_wait, locator=element)

    def is_element_present(self, *locator):
        try:
            self.driver.find_element(*locator)
        except NoSuchElementException:
            return False
        return True

    def switch_to_window(self, window):
        window_after = self.driver.window_handles[window]
        self.driver.switch_to_window(window_after)
