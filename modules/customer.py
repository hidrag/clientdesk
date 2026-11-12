from modules.validation import (
    validate_address,
    validate_customer_name,
    validate_phone_number,
)


def get_customer_by_phone(conn, phone_number):
    """
    Retrieve a customer using their phone number.

    Args:
        conn: Active PostgreSQL database connection.
        phone_number: Phone number to search for.

    Returns:
        Customer record as a tuple, or None when not found.

    Side effects:
        Executes a read-only SELECT query.
    """

    query = """
        SELECT CUST_ID, FULL_NAME, ADDRESS, PHONE_NUMBER
        FROM CUST_DETAILS
        WHERE PHONE_NUMBER = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (phone_number,))
        return cursor.fetchone()


def create_customer(conn, full_name, address, phone_number):
    """Validate and register a new customer.

    Args:
        conn: Active PostgreSQL database connection.
        full_name: Customer's full name.
        address: Customer's postal address.
        phone_number: Customer's ten-digit phone number.

    Returns:
        The inserted customer tuple.

    Raises:
        ValueError: If input is invalid or the phone number is registered.

    Side effects:
        Inserts one customer and commits it in a transaction.
    """
    full_name = validate_customer_name(full_name)
    address = validate_address(address)
    phone_number = validate_phone_number(phone_number)

    # Explicit transaction: duplicate check and insert are grouped together.
    with conn.transaction():
        if get_customer_by_phone(conn, phone_number):
            raise ValueError("A customer with this phone number already exists.")

        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cust_details
                    (full_name, address, phone_number)
                VALUES (%s, %s, %s)
                RETURNING cust_id, full_name, address, phone_number;
                """,
                (full_name, address, phone_number)
            )
            return cursor.fetchone()


