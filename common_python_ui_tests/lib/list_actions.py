import logging
import random

from selenium.common.exceptions import NoSuchElementException

log = logging.getLogger(__name__)


class ListActions:

    def get_list_item(self, value, *locator):
        menu = self.driver.find_elements(*locator)
        for item in menu:
            if item.text == value:
                log.info(f'Selected item: {item.text}')
                return item
        else:
            raise NoSuchElementException(f'Cannot find element "{value}"')

    def get_random_list_item(self, *locator):
        elements_list = self.driver.find_elements(*locator)
        random_item = random.choice(elements_list)
        log.info(f'Selected item: {random_item.text}')
        return random_item

    def get_first_list_item(self, *locator):
        elements_list = self.driver.find_elements(*locator)
        first_item = elements_list[0]
        log.info(f'Selected item: {first_item.text}')
        return first_item

    def get_elements_list(self, *locator):
        return self.driver.find_elements(*locator)

    def values_unicity_assertion(self, values_list):
        for item in values_list:
            if not item.text == '':
                assert values_list[0].text == item.text, f"List '{values_list[0].text}' contain '{item.text}' value"

    def check_values_in_list(self, value, *locator):
        actual_elements_list = self.driver.find_elements(*locator)
        for item in actual_elements_list:
            if not item.text == '':
                assert item.text == value, f"List of '{value}' values contains '{item.text}'"

    def compare_values_with_list(self, expected_values, list):
        for item in list:
            if not item.text == '':  # Workaround for empty list elements
                assert item.text in expected_values, f"List of '{expected_values}' values contains '{item.text}'"

    def verify_value_is_present_in_list(self, expected_value, *locator):
        actual_elements_list = self.driver.find_elements(*locator)
        values_list = []
        for element in actual_elements_list:
            values_list.append(element.text)
        log.info(f'Values in the list: {values_list}')
        assert expected_value in values_list, f"Expected value '{expected_value}' not present in the list: {values_list}"
