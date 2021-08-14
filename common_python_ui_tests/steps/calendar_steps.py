# -*- coding: UTF-8 -*-
from behave import *

use_step_matcher('re')


@step('I set "(?P<date_range>Today|Yesterday|Last 7 Days|Last 30 Days)" date range in calendar')
def set_calendar_date(context, date_range):
    context.calendar_widget \
        .open_date_range_calendar() \
        .set_predefined_date_range(date_range) \
        .submit()


@step('I set huge date range in calendar')
def set_huge_date_range(context):
    context.calendar_widget \
        .open_date_range_calendar() \
        .set_huge_date_range() \
        .submit()


@step('date range is limited to (?P<days>\d+) days')
def verify_date_range_is_limited(context, days):
    context.calendar_widget.verify_range_limit(days_limit=days)
