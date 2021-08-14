# -*- coding: UTF-8 -*-
from behave import step, use_step_matcher

use_step_matcher('parse')


@step('I switch to "{frame_name}" iframe')
def switch_to_iframe(context, frame_name):
    context.driver.switch_to_iframe(wait_time=30, frame_name=frame_name)


@step('I switch back from iframe')
def switch_to_default_content(context):
    context.driver.switch_back_from_iframe()


def iframe(f):
    def wrapper(context, *args, **kwargs):
        iframe_id = getattr(context.app, 'iframe_id', None)
        if not iframe_id or context.driver.IFRAME_FOCUS == iframe_id:
            f(context, *args, **kwargs)
        else:
            switch_to_iframe(context, context.app.iframe_id)
            f(context, *args, **kwargs)
            switch_to_default_content(context)

    return wrapper
