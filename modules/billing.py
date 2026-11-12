from decimal import Decimal

def calculate_item_total(price, quantity):
    """Calculate the total price for one product.

    Args:
        price: Unit price, converted through Decimal for exact currency math.
        quantity: Positive item quantity.

    Returns:
        Decimal item total.

    Side effects:
        None.
    """

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    return Decimal(str(price)) * quantity


def calculate_bill_total(items):
    """Calculate the grand total of a billing cart.

    Args:
        items: Iterable of dictionaries containing price and quantity.

    Returns:
        Decimal grand total.

    Side effects:
        None.
    """

    return sum(
        (
            calculate_item_total(item["price"], item["quantity"])
            for item in items
        ),
        Decimal("0.00")
    )


def finalize_bill(conn, customer, cart):
    """
    Finalize a supermarket bill.

    customer:
        Tuple containing customer details.

    cart:
        List of dictionaries:
        [
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 3}
        ]

    Returns:
        Dictionary containing bill ID, timestamp, line items and total amount.

    Side effects:
        Inserts bill rows and decrements inventory in one transaction. Any
        exception rolls the complete operation back.
    """

    if not cart:
        raise ValueError("Billing cart is empty.")

    customer_id, customer_name = customer[0], customer[1]

    # Combine repeated products in the cart.
    combined_cart = {}

    for item in cart:
        product_id = int(item["product_id"])
        quantity = int(item["quantity"])

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        combined_cart[product_id] = (
            combined_cart.get(product_id, 0) + quantity
        )

    bill_items = []
    total_bill_value = Decimal("0.00")

    # All billing changes must succeed together.
    with conn.transaction():

        with conn.cursor() as cursor:

            # Lock product rows to avoid conflicting stock updates.
            for product_id, quantity in sorted(combined_cart.items()):

                cursor.execute(
                    """
                    SELECT P_ID, P_NAME, P_PRICE, STOCK_ON_HAND
                    FROM PRODUCT_DETAILS
                    WHERE P_ID = %s
                    FOR UPDATE
                    """,
                    (product_id,)
                )

                product = cursor.fetchone()

                if not product:
                    raise ValueError(
                        f"Product ID {product_id} not found."
                    )

                p_id, p_name, p_price, stock = product

                if quantity > stock:
                    raise ValueError(
                        f"Insufficient stock for {p_name}. "
                        f"Available: {stock}"
                    )

                item_total = calculate_item_total(
                    p_price,
                    quantity
                )

                total_bill_value += item_total

                bill_items.append({
                    "product_id": p_id,
                    "product_name": p_name,
                    "price": Decimal(str(p_price)),
                    "quantity": quantity,
                    "total": item_total
                })

            # Create bill summary and retrieve actual generated ID.
            cursor.execute(
                """
                INSERT INTO BILL_SUMMARY_TB
                (C_ID, FULL_NAME, TOTAL_BILL_VALUE)
                VALUES (%s, %s, %s)
                RETURNING BILL_ID, CREATED_AT
                """,
                (
                    customer_id,
                    customer_name,
                    total_bill_value
                )
            )

            bill_id, created_at = cursor.fetchone()

            # Save bill details and deduct stock.
            for item in bill_items:

                cursor.execute(
                    """
                    INSERT INTO BILL_DETAILS
                    (
                        BILL_ID,
                        C_ID,
                        C_NAME,
                        P_ID,
                        P_NAME,
                        P_PRICE,
                        QUANTITY,
                        TOTAL_BILL_AMOUNT
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        bill_id,
                        customer_id,
                        customer_name,
                        item["product_id"],
                        item["product_name"],
                        item["price"],
                        item["quantity"],
                        item["total"]
                    )
                )

                cursor.execute(
                    """
                    UPDATE PRODUCT_DETAILS
                    SET STOCK_ON_HAND = STOCK_ON_HAND - %s
                    WHERE P_ID = %s
                    """,
                    (
                        item["quantity"],
                        item["product_id"]
                    )
                )
                if cursor.rowcount != 1:
                    raise RuntimeError(
                        f"Inventory update failed for product "
                        f"{item['product_id']}."
                    )

    return {
            "bill_id": bill_id,
            "customer_id": customer_id,
            "customer_name": customer_name,
            "created_at": created_at,
            "items": bill_items,
            "total": total_bill_value
        }


def display_bill(bill):
    """Display a completed bill in the terminal.

    Args:
        bill: Finalized bill dictionary.

    Returns:
        None.

    Side effects:
        Writes a legacy compact receipt view to stdout.
    """

    print("\n" + "=" * 55)
    print("             MORE SUPERMARKET MEGA")
    print("=" * 55)

    print("Bill ID:", bill["bill_id"])
    print("Customer:", bill["customer_name"])

    print("-" * 55)

    print(
        f"{'Product':25} {'Qty':>5} "
        f"{'Price':>10} {'Total':>12}"
    )

    print("-" * 55)

    for item in bill["items"]:

        print(
            f"{item['product_name'][:25]:25} "
            f"{item['quantity']:>5} "
            f"{item['price']:>10.2f} "
            f"{item['total']:>12.2f}"
        )

    print("-" * 55)

    print(f"GRAND TOTAL: Rs. {bill['total']:.2f}")

    print("=" * 55)
    print("Thank you for shopping with us!")
