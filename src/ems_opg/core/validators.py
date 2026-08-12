"""
Shared format validation for order numbres and serial numbers.
"""

import re

# 4-5 digits, a decimal point, then exactly one digit, e.g. 1234.5 / 12345.6
ORDER_NUMBER_PATTERNS = re.compile(r"^\d{4,5}\.\d$")

# EM + 4-digit year + 2-digit ISO week + 4-digit sequence, e.g. EM2026310001
SERIAL_NUMBER_PATTERNS = re.compile(r"^em\d{10}$")

def is_valid_order_number(value):
    return bool(ORDER_NUMBER_PATTERNS.match(value or ""))

def is_valid_serial_number(value):
    return bool(SERIAL_NUMBER_PATTERNS.match(value or ""))