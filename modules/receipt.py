"""Terminal receipt formatting and persistence."""

from datetime import datetime
from pathlib import Path


def format_receipt(bill):
    """Format a finalized bill as a readable terminal receipt.

    Args:
        bill: Finalized bill dictionary returned by ``finalize_bill``.

    Returns:
        Receipt text containing customer, timestamp, line items and total.

    Side effects:
        None.
    """
    created_at = bill.get("created_at") or datetime.now()
    if hasattr(created_at, "strftime"):
        created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "",
        "=" * 64,
        "                 MORE SUPERMARKET MEGA",
        "=" * 64,
        f"Bill ID: {bill['bill_id']}",
        f"Customer ID: {bill['customer_id']}",
        f"Customer: {bill['customer_name']}",
        f"Date and time: {created_at}",
        "-" * 64,
        f"{'Product':30} {'Price':>10} {'Qty':>5} {'Total':>12}",
        "-" * 64,
    ]
    for item in bill["items"]:
        lines.append(
            f"{item['product_name'][:30]:30} "
            f"{item['price']:>10.2f} "
            f"{item['quantity']:>5} "
            f"{item['total']:>12.2f}"
        )
    lines.extend([
        "-" * 64,
        f"{'GRAND TOTAL':>52} Rs. {bill['total']:.2f}",
        "=" * 64,
        "Thank you for shopping with us!",
    ])
    return "\n".join(lines)


def save_receipt(bill, output_path):
    """Save a finalized bill receipt as a UTF-8 text file.

    Args:
        bill: Finalized bill dictionary returned by ``finalize_bill``.
        output_path: Destination path for the receipt text file.

    Returns:
        A ``Path`` pointing to the saved receipt.

    Side effects:
        Creates the destination directory and writes the receipt file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_receipt(bill) + "\n", encoding="utf-8")
    return path
