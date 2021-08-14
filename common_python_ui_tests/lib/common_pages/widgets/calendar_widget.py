from datetime import timedelta, datetime

from dateutil import parser
from selenium.webdriver.common.by import By

from common_python_ui_tests.lib.base_page import BasePage
from common_python_ui_tests.lib.list_actions import ListActions
from common_python_ui_tests.lib.utils.date_formatter import CustomDateTimeFormatter as Formatter


# Specific object to interact with 'react-date-range' React component (https://www.npmjs.com/package/react-date-range)
class CalendarWidget(BasePage, ListActions):
    CALENDAR_WIDGET = (By.CSS_SELECTOR, '.rdr-DateRange')
    PREDEFINED_RANGES_LIST = (By.CSS_SELECTOR, '.rdr-PredefinedRangesItem')
    DATE_RANGE = (By.XPATH, '//*[@data-element="date-range"]')
    SUBMIT_BUTTON = (By.XPATH, '//main//button[@type="submit"]')
    FIRST_DAY = (
        By.XPATH,
        '//div[@class="rdr-Calendar"][1]//span[(@class="rdr-Day" or @class="rdr-Day rdr-Sunday") and text()="1"]')
    LAST_DAY = (
        By.XPATH,  # Duct tape for February case
        '//div[@class="rdr-Calendar"][2]//span[(@class="rdr-Day" or @class="rdr-Day rdr-Sunday") and text()="28"]')
    START_MONTH_PREV_BUTTON = (
        By.XPATH, '//div[@class="rdr-Calendar"][1]//button[@class="rdr-MonthAndYear-button prev"]')
    START_MONTH_NEXT_BUTTON = (
        By.XPATH, '//div[@class="rdr-Calendar"][1]//button[@class="rdr-MonthAndYear-button next"]')
    END_MONTH_PREV_BUTTON = (By.XPATH, '//div[@class="rdr-Calendar"][2]//button[@class="rdr-MonthAndYear-button prev"]')
    END_MONTH_NEXT_BUTTON = (By.XPATH, '//div[@class="rdr-Calendar"][2]//button[@class="rdr-MonthAndYear-button next"]')

    def appears(self):
        self.element_is_visible(self.DATE_RANGE)
        return self

    def open_date_range_calendar(self):
        self.click_element(*self.DATE_RANGE)
        self.element_is_visible(self.CALENDAR_WIDGET)
        return self

    def set_predefined_date_range(self, range):
        self.element_is_visible(self.PREDEFINED_RANGES_LIST)
        ListActions.get_list_item(self, range, *self.PREDEFINED_RANGES_LIST).click()
        return self

    def set_huge_date_range(self):
        self.click_element(*self.START_MONTH_PREV_BUTTON)
        self.click_element(*self.FIRST_DAY)
        self.click_element(*self.LAST_DAY)
        return self

    def check_week_range(self):
        today = Formatter.get_formatted_datetime('%B {S} %Y', datetime.now())
        week_ago = Formatter.get_formatted_datetime('%B {S} %Y', datetime.now() - timedelta(days=7))
        actual_week_ago, actual_today = self.__get_actual_dates()
        assert today == actual_today, (
            f'Expected for current date {today}, found {actual_today} instead.')
        assert week_ago == actual_week_ago, (
            f'Expected for a date week ago {week_ago}, found {actual_today} instead.')

    def verify_range_limit(self, days_limit):
        start_date, end_date = self.__get_actual_dates()
        month_threshold = Formatter.get_formatted_datetime('%B {S} %Y',
                                                           parser.parse(start_date) + timedelta(days=float(days_limit)))
        assert end_date == month_threshold, f'Expected end date is {month_threshold}, found {end_date} instead.'

    def submit(self):
        self.click_element(*self.SUBMIT_BUTTON)

    def __get_actual_dates(self):
        date_input_text = self.get_element_text(*self.DATE_RANGE)
        return [d.strip() for d in date_input_text.split(u"\u2014")]
