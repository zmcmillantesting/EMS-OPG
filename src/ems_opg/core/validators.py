"""
Shared format validation for order numbers and serial numbers.
"""

import re

# 4-5 digits, a decimal point, then exactly one digit. e.g. 1234.5 / 12345.6
ORDER_NUMBER_PATTERN = re.compile(r"^\d{4,5}\.\d$")

# "EM" + 2-digit year + 2-digit ISO week + 4-digit sequence, e.g. EM2026320001
SERIAL_NUMBER_PATTERN = re.compile(r"^EM\d{8}$")


def is_valid_order_number(value):
    return bool(ORDER_NUMBER_PATTERN.match(value or ""))


def is_valid_serial_number(value):
    return bool(SERIAL_NUMBER_PATTERN.match(value or ""))
