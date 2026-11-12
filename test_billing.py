
from modules.db_connection import get_connection
from modules.customer import get_customer_by_phone
from modules.product import get_all_products
from modules.billing import finalize_bill, display_bill

conn = get_connection()

try:
    # Find our previously registered test customer
    customer = get_customer_by_phone(conn, "9876543210")

    if not customer:
        raise ValueError("Test customer not found. Register one first.")

    # Find a product with available stock
    products = get_all_products(conn)

    available_product = next(
        (p for p in products if p[3] >= 2),
        None
    )

    if not available_product:
        raise ValueError("No product has sufficient stock.")

    product_id = available_product[0]

    cart = [
        {
            "product_id": product_id,
            "quantity": 2
        }
    ]

    # Generate bill and update inventory
    bill = finalize_bill(conn, customer, cart)

    print("\nBilling successful!")
    display_bill(bill)

except Exception as error:
    print("Billing error:", error)

finally:
    conn.close()
