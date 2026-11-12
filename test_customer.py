from modules.db_connection import get_connection
from modules.customer import (
    create_customer,
    get_customer_by_phone
)

conn = get_connection()

try:
    phone = "9876543210"

    existing = get_customer_by_phone(conn, phone)

    if existing:
        print("Customer already exists:", existing)
    else:
        customer = create_customer(
            conn,
            "Test Customer",
            "Kolkata, West Bengal",
            phone
        )
        print("Customer created:", customer)

    customer = get_customer_by_phone(conn, phone)
    print("Customer lookup:", customer)

except Exception as error:
    print("Error:", error)

finally:
    conn.close()