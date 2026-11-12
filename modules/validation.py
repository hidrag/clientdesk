"""Small input and formatting helpers for the CLI application."""

import re


def validate_phone_number(phone_number):
    """Validate a customer phone number.

    Args:
        phone_number: Value supplied by the user.

    Returns:
        Normalized phone number string.

    Raises:
        ValueError: If the value is not exactly ten digits.

    Side effects:
        None.
    """
    value = str(phone_number).strip()
    if not re.fullmatch(r"\d{10}", value):
        raise ValueError("Phone number must contain exactly 10 digits.")
    return value


def validate_customer_name(full_name):
    """Validate and normalize a customer name.

    Args:
        full_name: Customer's full name.

    Returns:
        Stripped name.

    Raises:
        ValueError: If the name is too short or too long.

    Side effects:
        None.
    """
    value = str(full_name).strip()
    if not 3 <= len(value) <= 200:
        raise ValueError("Customer name must contain 3 to 200 characters.")
    return value


def validate_address(address):
    """Validate and normalize a customer address.

    Args:
        address: Customer's address.

    Returns:
        Stripped address.

    Raises:
        ValueError: If the address is empty or exceeds the schema limit.

    Side effects:
        None.
    """
    value = str(address).strip()
    if not value:
        raise ValueError("Customer address cannot be empty.")
    if len(value) > 500:
        raise ValueError("Customer address cannot exceed 500 characters.")
    return value
