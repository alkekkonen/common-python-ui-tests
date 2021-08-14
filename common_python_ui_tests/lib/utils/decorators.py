import functools
import logging

log = logging.getLogger(__name__)

"""
Example of python decorators created with functools.py wrapper
"""


# Decorator for parameters formatting
# See usage in js_execute_steps.py
def format_params(func):
    @functools.wraps(func)
    def wrapper(context, *args, **kwargs):
        formatted_args = context.format(list(args))
        formatted_kwargs = {key: context.format(value)
                            for key, value in kwargs.items()}
        return func(context, *formatted_args, **formatted_kwargs)

    return wrapper


# Decorator for using separate context.client for function / step
def separate_client(func):
    @functools.wraps(func)
    def wrapper(context, *args, **kwargs):
        old_client = context.client
        old_resource = context.current
        res = func(context, *args, **kwargs)
        context.client = old_client
        context.current = old_resource
        return res

    return wrapper
