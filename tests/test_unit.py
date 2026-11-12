"""Unit tests for More Supermarket Mega — pure functions only.

These tests verify calculation, validation and formatting logic without
a live database connection. Database-dependent tests (customer, product,
billing) are in the root test_*.py scripts.
"""

from decimal import Decimal
from pathlib import Path
import tempfile
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.validation import (
    validate_customer_name,
    validate_address,
    validate_phone_number,
)
from modules.billing import calculate_item_total, calculate_bill_total
from modules.receipt import format_receipt, save_receipt


def test_validate_customer_name():
    """Valid names pass; empty/too-short names raise ValueError."""
    assert validate_customer_name("  Alice  ") == "Alice"
    assert validate_customer_name("Bob") == "Bob"
    assert validate_customer_name("A" * 200) == "A" * 200
    try:
        validate_customer_name("")
        assert False
    except ValueError:
        pass
    try:
        validate_customer_name("AB")
        assert False
    except ValueError:
        pass


def test_validate_address():
    """Non-empty addresses up to 500 chars pass."""
    assert validate_address("  Some St  ") == "Some St"
    try:
        validate_address("")
        assert False
    except ValueError:
        pass
    try:
        validate_address("X" * 501)
        assert False
    except ValueError:
        pass


def test_validate_phone_number():
    """Exactly ten digits pass; everything else is rejected."""
    assert validate_phone_number("9876543210") == "9876543210"
    try:
        validate_phone_number("987654321")
        assert False
    except ValueError:
        pass
    try:
        validate_phone_number("98765432101")
        assert False
    except ValueError:
        pass
    try:
        validate_phone_number("abcd123456")
        assert False
    except ValueError:
        pass


def test_calculate_item_total():
    """Item total is Decimal(price) * quantity."""
    assert calculate_item_total("46.50", 2) == Decimal("93.00")
    assert calculate_item_total(100, 3) == Decimal("300")
    try:
        calculate_item_total("10", 0)
        assert False
    except ValueError:
        pass


def test_calculate_bill_total():
    """Sum of all item totals, empty cart = 0."""
    items = [
        {"price": "50", "quantity": 3},
        {"price": "25.50", "quantity": 2},
    ]
    assert calculate_bill_total(items) == Decimal("201.00")
    assert calculate_bill_total([]) == Decimal("0.00")


def test_format_receipt():
    """Receipt contains expected sections."""
    bill = {
        "bill_id": 42,
        "customer_id": 1001,
        "customer_name": "Test User",
        "created_at": "2026-11-12 10:30:00",
        "items": [
            {"product_name": "Rice 1 KG", "price": Decimal("46.00"),
             "quantity": 2, "total": Decimal("92.00")},
            {"product_name": "Milk 1 L", "price": Decimal("62.00"),
             "quantity": 1, "total": Decimal("62.00")},
        ],
        "total": Decimal("154.00"),
    }
    text = format_receipt(bill)
    assert "MORE SUPERMARKET MEGA" in text
    assert "Bill ID: 42" in text
    assert "Customer ID: 1001" in text
    assert "Test User" in text
    assert "2026-11-12 10:30:00" in text
    assert "Rice 1 KG" in text
    assert "Milk 1 L" in text
    assert "154.00" in text
    assert "Thank you for shopping" in text


def test_save_receipt():
    """Saved receipt file matches formatted text."""
    bill = {
        "bill_id": 99,
        "customer_id": 1002,
        "customer_name": "Receipt Test",
        "created_at": "2026-11-12 12:00:00",
        "items": [
            {"product_name": "Test Item", "price": Decimal("10.00"),
             "quantity": 5, "total": Decimal("50.00")},
        ],
        "total": Decimal("50.00"),
    }
    with tempfile.TemporaryDirectory() as tmp:
        path = save_receipt(bill, Path(tmp) / "receipt_99.txt")
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "Bill ID: 99" in content
        assert "Receipt Test" in content
        assert "50.00" in content


if __name__ == "__main__":
    test_validate_customer_name()
    test_validate_address()
    test_validate_phone_number()
    test_calculate_item_total()
    test_calculate_bill_total()
    test_format_receipt()
    test_save_receipt()
    print("All tests passed!")
