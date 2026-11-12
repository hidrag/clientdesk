def get_product_by_id(conn, product_id):
    """
    Retrieve a product using its product ID.

    Args:
        conn: Active PostgreSQL database connection.
        product_id: Product identity value to search for.

    Returns:
        Product record as a tuple, or None when not found.

    Side effects:
        Executes a read-only SELECT query.
    """

    query = """
        SELECT P_ID, P_NAME, P_PRICE, STOCK_ON_HAND
        FROM PRODUCT_DETAILS
        WHERE P_ID = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (product_id,))
        return cursor.fetchone()


def get_all_products(conn):
    """
    Retrieve all available products.

    Args:
        conn: Active PostgreSQL database connection.

    Returns:
        Products ordered by product ID.

    Side effects:
        Executes a read-only SELECT query.
    """

    query = """
        SELECT P_ID, P_NAME, P_PRICE, STOCK_ON_HAND
        FROM PRODUCT_DETAILS
        ORDER BY P_ID
    """

    with conn.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def check_product_stock(conn, product_id, quantity):
    """
    Check whether sufficient stock is available.

    Args:
        conn: Active PostgreSQL database connection.
        product_id: Product identity value to check.
        quantity: Required positive quantity.

    Returns:
        True when enough stock is available.

    Side effects:
        Executes a read-only product lookup.
    """

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    product = get_product_by_id(conn, product_id)

    if not product:
        raise ValueError("Product not found.")

    available_stock = product[3]

    if quantity > available_stock:
        raise ValueError(
            f"Insufficient stock. Available: {available_stock}"
        )

    return True
