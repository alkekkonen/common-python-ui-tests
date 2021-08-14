"""
Example of inner functions usage.
Demonstration of the point 'The shortest code is not always the best code'.
Works fine but looks not too readable. Be careful with inner functions.
"""


def get_formatted_datetime(regex, date):
    def suffix(date):
        return 'th' if 11 <= date <= 13 \
            else {1: 'st', 2: 'nd', 3: 'rd'}.get(date % 10, 'th')

    return date.strftime(regex).replace('{S}', str(date.day) + suffix(date.day))
