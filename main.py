"""Command-line entry point for More Supermarket Mega."""

from pathlib import Path

from modules.billing import finalize_bill
from modules.customer import create_customer, get_customer_by_phone
from modules.db_connection import get_connection
from modules.product import get_all_products, get_product_by_id
from modules.qr_generator import generate_product_qr_pdf
from modules.qr_scanner import qr_code_scanner
from modules.receipt import format_receipt, save_receipt


OUTPUT_DIR = Path("generated")


def read_non_empty(prompt):
    """Read a required text value from the terminal.

    Args:
        prompt: Prompt displayed to the user.

    Returns:
        A stripped, non-empty string.

    Side effects:
        Reads terminal input and repeats until a value is supplied.
    """
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This value cannot be empty.")


def read_positive_integer(prompt):
    """Read a positive integer from the terminal.

    Args:
        prompt: Prompt displayed to the user.

    Returns:
        A positive integer entered by the user.

    Side effects:
        Reads terminal input and handles invalid values without crashing.
    """
    while True:
        try:
            value = int(input(prompt).strip())
            if value > 0:
                return value
        except ValueError:
            pass
        print("Enter a whole number greater than zero.")


def register_customer(conn):
    """Collect and save one customer registration.

    Args:
        conn: Active PostgreSQL connection.

    Returns:
        The created customer tuple, or None when registration is cancelled.

    Side effects:
        Inserts a customer into PostgreSQL after validation.
    """
    print("\n--- Register Customer ---")
    full_name = read_non_empty("Full name: ")
    address = read_non_empty("Address: ")
    phone_number = read_non_empty("Phone number (10 digits): ")
    try:
        customer = create_customer(conn, full_name, address, phone_number)
    except ValueError as error:
        print(f"Registration failed: {error}")
        return None
    print(f"Customer registered with ID {customer[0]}.")
    return customer


def identify_customer(conn):
    """Find a customer by phone or register a new one.

    Args:
        conn: Active PostgreSQL connection.

    Returns:
        A customer tuple, or None if the workflow is cancelled.

    Side effects:
        Reads terminal input and may insert a new customer.
    """
    phone_number = read_non_empty("Customer phone number (10 digits): ")
    customer = get_customer_by_phone(conn, phone_number)
    if customer:
        print(f"Welcome back, {customer[1]} (customer ID {customer[0]}).")
        return customer

    print("No customer was found for that phone number.")
    if input("Register this customer now? [y/N]: ").strip().lower() != "y":
        return None
    return create_customer(
        conn,
        read_non_empty("Full name: "),
        read_non_empty("Address: "),
        phone_number,
    )


def choose_product_id(conn):
    """Obtain a product ID using a webcam or manual fallback.

    Args:
        conn: Active PostgreSQL connection used for validating scanned IDs.

    Returns:
        An integer product ID, or None when the user cancels.

    Side effects:
        May open a webcam window and reads terminal input.
    """
    method = input("Scan QR code or enter ID manually? [s/m]: ").strip().lower()
    if method == "s":
        decoded = qr_code_scanner()
        if decoded is None:
            print("Scanning cancelled or unavailable; use manual entry instead.")
            return None
        try:
            product_id = int(decoded.strip())
        except ValueError:
            print("The QR code does not contain a numeric product ID.")
            return None
    else:
        try:
            product_id = int(input("Product ID (blank to finish): ").strip())
        except ValueError:
            print("Enter a numeric product ID.")
            return None

    product = get_product_by_id(conn, product_id)
    if not product:
        print("Product not found.")
        return None
    print(f"{product[1]} | Rs. {product[2]:.2f} | Stock: {product[3]}")
    return product_id


def run_billing(conn):
    """Run the interactive cart and finalize one bill atomically.

    Args:
        conn: Active PostgreSQL connection.

    Returns:
        The finalized bill dictionary, or None if no bill was created.

    Side effects:
        May register a customer, update inventory, save bill records, and write
        a receipt file after successful finalization.
    """
    print("\n--- New Billing ---")
    try:
        customer = identify_customer(conn)
    except ValueError as error:
        print(f"Customer workflow failed: {error}")
        return None
    if not customer:
        print("Billing cancelled.")
        return None

    cart = []
    while True:
        product_id = choose_product_id(conn)
        if product_id is not None:
            quantity = read_positive_integer("Quantity: ")
            cart.append({"product_id": product_id, "quantity": quantity})
            print("Item added to cart.")
        if input("Add another product? [y/N]: ").strip().lower() != "y":
            break

    if not cart:
        print("No products were added. Billing cancelled.")
        return None
    try:
        bill = finalize_bill(conn, customer, cart)
    except (ValueError, RuntimeError) as error:
        print(f"Billing failed; no bill or inventory change was saved: {error}")
        return None

    receipt_text = format_receipt(bill)
    receipt_path = save_receipt(bill, OUTPUT_DIR / f"receipt_{bill['bill_id']}.txt")
    print(receipt_text)
    print(f"Receipt saved to {receipt_path}")
    return bill


def view_products(conn):
    """Display all products and their current inventory.

    Args:
        conn: Active PostgreSQL connection.

    Returns:
        None.

    Side effects:
        Executes a read-only product query and prints its results.
    """
    products = get_all_products(conn)
    if not products:
        print("No products found.")
        return
    print(f"\n{'ID':>5} {'Product':35} {'Price':>10} {'Stock':>8}")
    print("-" * 65)
    for product_id, name, price, stock in products:
        print(f"{product_id:>5} {name[:35]:35} {price:>10.2f} {stock:>8}")


def generate_qr_pdf(conn):
    """Generate the product QR label PDF in the output directory.

    Args:
        conn: Active PostgreSQL connection.

    Returns:
        The generated PDF path, or None when generation is not possible.

    Side effects:
        Reads products and writes a multi-page PDF file.
    """
    products = get_all_products(conn)
    if not products:
        print("No products found.")
        return None
    path = generate_product_qr_pdf(products, OUTPUT_DIR / "product_qr_codes.pdf")
    print(f"Generated QR PDF for {len(products)} products: {path}")
    return path


def display_menu():
    """Print the main application menu.

    Returns:
        None.

    Side effects:
        Writes menu text to the terminal.
    """
    print("\nMORE SUPERMARKET MEGA")
    print("=" * 23)
    print("1. Register Customer")
    print("2. Start New Billing")
    print("3. View Products")
    print("4. Generate Product QR PDF")
    print("5. Exit")


def main():
    """Run the CLI menu until the user exits.

    Returns:
        None.

    Side effects:
        Opens and closes the PostgreSQL connection and runs selected workflows.
    """
    conn = None
    try:
        conn = get_connection()
        while True:
            display_menu()
            choice = input("Select an option: ").strip()
            if choice == "1":
                register_customer(conn)
            elif choice == "2":
                run_billing(conn)
            elif choice == "3":
                view_products(conn)
            elif choice == "4":
                generate_qr_pdf(conn)
            elif choice == "5":
                print("Goodbye.")
                break
            else:
                print("Invalid choice. Select an option from 1 to 5.")
    except (ConnectionError, ValueError) as error:
        print(f"Application error: {error}")
    except KeyboardInterrupt:
        print("\nApplication cancelled.")
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    main()