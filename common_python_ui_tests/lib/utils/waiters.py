from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

DEFAULT_TIMEOUT = 30


class Waiters:
    """
    Wrappers for Selenium 'expected_conditions' tools
    """

    @staticmethod
    def wait_visible(driver, locator, timeout=DEFAULT_TIMEOUT, message='Element not visible'):
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(locator), message
        )

    @staticmethod
    def wait_invisible(driver, locator, timeout=DEFAULT_TIMEOUT, message='Element is visible'):
        return WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located(locator), message
        )

    @staticmethod
    def wait_disappear(driver, locator, timeout=DEFAULT_TIMEOUT, message='Element is present'):
        return WebDriverWait(driver, timeout).until_not(
            EC.presence_of_element_located(locator), message
        )

    @staticmethod
    def wait_clickable(driver, locator, timeout=DEFAULT_TIMEOUT, message='Element is not clickable'):
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(locator), message=message
        )

    @staticmethod
    def wait_unclickable(driver, locator, timeout=DEFAULT_TIMEOUT, message='Element is clickable'):
        return WebDriverWait(driver, timeout).until(
            lambda driver: driver.find_element(*locator).is_enabled() is False, message=message)
