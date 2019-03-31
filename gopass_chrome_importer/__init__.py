"""
gopass-chrome-importer
"""


def coerce(value: int or float, min_value: int or float, max_value: int or float) -> int or float:
    """
    Forces a value to be within the given min and max value.

    :param value: the value to coerce
    :param min_value: minimum allowed value
    :param max_value: maximum allowed value
    :return: a value within the given range
    """
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value
