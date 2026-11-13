"""Streamlit web interface for More Supermarket Mega."""

import os
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st
import psycopg
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool, PoolTimeout

from modules.billing import finalize_bill
from modules.customer import create_customer, get_customer_by_phone
from modules.product import get_all_products, get_product_by_id
from modules.qr_generator import generate_product_qr_pdf
from modules.receipt import format_receipt, save_receipt
from modules.validation import (
    validate_address,
    validate_customer_name,
    validate_phone_number,
)

# Load .env from the project directory (absolute path) so Streamlit finds it
# regardless of the current working directory.
_PROJECT_ROOT = Path(__file__).resolve().parent
_ENV_PATH = _PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=False)

st.set_page_config(
    page_title="More Supermarket Mega",
    page_icon="🛒",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Database configuration and connection pool
# ---------------------------------------------------------------------------

def _get_database_url():
    """Return the validated PostgreSQL connection string from the environment.

    Returns:
        The DATABASE_URL string.

    Raises:
        ValueError: If the variable is missing or malformed.

    Side effects:
        Reads environment variables (no secrets are exposed).
    """
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        raise ValueError(
            f"DATABASE_URL is missing. Expected it in {_ENV_PATH} "
            "or in the environment."
        )

    # Basic scheme validation without reconstructing or exposing the URL.
    if not (
        database_url.startswith("postgresql://")
        or database_url.startswith("postgres://")
    ):
        raise ValueError(
            "DATABASE_URL must start with 'postgresql://' or 'postgres://'."
        )

    try:
        parsed = urlparse(database_url)
    except Exception as exc:
        raise ValueError(f"DATABASE_URL could not be parsed: {type(exc).__name__}") from exc

    # Verify required components are present without logging their values.
    if not parsed.hostname:
        raise ValueError("DATABASE_URL is missing a database host.")
    if not parsed.username:
        raise ValueError("DATABASE_URL is missing a username.")
    if parsed.password is None or parsed.password == "":
        raise ValueError("DATABASE_URL is missing a password.")
    if not parsed.path or parsed.path == "/":
        raise ValueError("DATABASE_URL is missing a database name.")

    return database_url


@st.cache_resource
def _get_connection_pool():
    """Create and cache a Psycopg 3 connection pool.

    Returns:
        A ``psycopg_pool.ConnectionPool`` instance.

    Side effects:
        Opens the pool and validates configuration. Connections are created on
        demand (min_size=0) to avoid repeated retries on authentication failure.

    Raises:
        ValueError: If DATABASE_URL is missing or malformed.
    """
    database_url = _get_database_url()

    # min_size=0 avoids background reconnect loops when auth/config is wrong.
    # Connections are created lazily on first acquisition.
    pool = ConnectionPool(
        conninfo=database_url,
        min_size=0,
        max_size=4,
        open=False,
        timeout=10,
        reconnect_timeout=30,
        num_workers=1,
    )
    try:
        pool.open(wait=True, timeout=10)
    except Exception as exc:
        try:
            pool.close()
        except Exception:
            pass
        raise ConnectionError(
            "Failed to initialize the database connection pool. "
            "Check DATABASE_URL, network access, and Neon credentials."
        ) from exc

    return pool


def get_conn():
    """Acquire a connection from the pool.

    Returns:
        A psycopg connection from the pool.

    Side effects:
        Blocks until a connection is available.
    """
    return _get_connection_pool().getconn()


def put_conn(conn):
    """Return a connection to the pool.

    Args:
        conn: A psycopg connection previously acquired via ``get_conn``.

    Side effects:
        Returns the connection to the pool for reuse.
    """
    _get_connection_pool().putconn(conn)


def get_customer_count():
    """Return the total number of registered customers."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM cust_details")
            return cur.fetchone()[0]
    finally:
        put_conn(conn)


def get_product_count():
    """Return the total number of products."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM product_details")
            return cur.fetchone()[0]
    finally:
        put_conn(conn)


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

for key, default in [
    ("customer", None),
    ("customer_phone", ""),
    ("cart", []),
    ("receipt", None),
    ("checkout_done", False),
    ("receipt_saved", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ---------------------------------------------------------------------------
# Page: Dashboard
# ---------------------------------------------------------------------------

def page_dashboard():
    """Render the dashboard overview."""
    st.title("More Supermarket Mega")
    st.markdown("A supermarket billing system — web interface.")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Products", get_product_count())
    with col2:
        st.metric("Total Customers", get_customer_count())

    st.markdown("---")
    st.markdown(
        "Use the sidebar navigation to access"
        " **Customer Management**, **Billing**, **Products**, **QR Code Generation**."
    )


# ---------------------------------------------------------------------------
# Page: Customer Management
# ---------------------------------------------------------------------------

def page_customers():
    """Render the customer lookup and registration page."""
    st.title("Customer Management")

    tab1, tab2 = st.tabs(["Lookup / Register", "All Customers"])

    with tab1:
        st.subheader("Find Customer by Phone")
        phone = st.text_input(
            "Phone number (10 digits)",
            max_chars=10,
            key="cust_phone_lookup",
        )

        if st.button("Search Customer", type="primary"):
            if not phone or not phone.strip().isdigit() or len(phone.strip()) != 10:
                st.error("Enter a valid 10-digit phone number.")
            else:
                conn = get_conn()
                try:
                    customer = get_customer_by_phone(conn, phone.strip())
                    if customer:
                        st.session_state.customer = customer
                        st.success(
                            f"**Customer found:** {customer[1]} (ID: {customer[0]})"
                        )
                        st.write(f"**Address:** {customer[2]}")
                        st.write(f"**Phone:** {customer[3]}")
                    else:
                        st.warning("No customer found with that phone number.")
                        st.session_state.customer = None
                finally:
                    put_conn(conn)

        st.markdown("---")
        st.subheader("Register New Customer")
        with st.form("register_form", clear_on_submit=True):
            name = st.text_input("Full name *")
            addr = st.text_area("Address *")
            phone_r = st.text_input("Phone number (10 digits) *", max_chars=10)
            submitted = st.form_submit_button("Register", type="primary")
            if submitted:
                try:
                    name = validate_customer_name(name)
                    addr = validate_address(addr)
                    phone_r = validate_phone_number(phone_r)
                    conn = get_conn()
                    try:
                        customer = create_customer(conn, name, addr, phone_r)
                    finally:
                        put_conn(conn)
                    st.session_state.customer = customer
                    st.success(
                        f"Customer registered successfully! "
                        f"ID: {customer[0]}, Name: {customer[1]}"
                    )
                except ValueError as e:
                    st.error(str(e))

    with tab2:
        st.subheader("All Registered Customers")
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT cust_id, full_name, address, phone_number "
                    "FROM cust_details ORDER BY cust_id"
                )
                rows = cur.fetchall()
        finally:
            put_conn(conn)
        if rows:
            st.dataframe(
                [
                    {"ID": r[0], "Name": r[1], "Address": r[2], "Phone": r[3]}
                    for r in rows
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No customers registered yet.")


# ---------------------------------------------------------------------------
# Page: Products
# ---------------------------------------------------------------------------

def page_products():
    """Render the product catalogue page."""
    st.title("Products")

    conn = get_conn()
    try:
        products = get_all_products(conn)
    finally:
        put_conn(conn)

    if not products:
        st.info("No products available.")
        return

    search = st.text_input("Search by name", key="prod_search").strip().lower()
    if search:
        products = [p for p in products if search in p[1].lower()]

    st.write(f"Showing {len(products)} product(s)")

    st.dataframe(
        [
            {"ID": p[0], "Name": p[1], "Price (Rs.)": float(p[2]), "Stock": p[3]}
            for p in products
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")
    st.subheader("Lookup by Product ID")
    pid = st.number_input("Product ID", min_value=1, step=1, key="prod_lookup")
    if st.button("Get Details"):
        conn = get_conn()
        try:
            product = get_product_by_id(conn, pid)
        finally:
            put_conn(conn)
        if product:
            st.write(f"**Name:** {product[1]}")
            st.write(f"**Price:** Rs. {product[2]:.2f}")
            st.write(f"**Stock:** {product[3]}")
        else:
            st.error(f"Product ID {pid} not found.")


# ---------------------------------------------------------------------------
# Page: Billing
# ---------------------------------------------------------------------------

def _add_to_cart(product_id, quantity):
    """Add a product to the cart or merge with an existing entry.

    Args:
        product_id: Integer product ID.
        quantity: Positive integer quantity.

    Side effects:
        Mutates st.session_state.cart.
    """
    conn = get_conn()
    try:
        product = get_product_by_id(conn, product_id)
    finally:
        put_conn(conn)
    if not product:
        st.error(f"Product ID {product_id} not found.")
        return

    p_id, p_name, p_price, stock = product

    if quantity > stock:
        st.error(f"Insufficient stock for {p_name}. Available: {stock}.")
        return

    item_total = Decimal(str(p_price)) * quantity

    for item in st.session_state.cart:
        if item["product_id"] == p_id:
            new_qty = item["quantity"] + quantity
            if new_qty > stock:
                st.error(
                    f"Insufficient stock for {p_name}. "
                    f"Cart already has {item['quantity']}, "
                    f"available: {stock}."
                )
                return
            item["quantity"] = new_qty
            item["total"] = Decimal(str(p_price)) * new_qty
            st.success(f"Updated {p_name} quantity to {new_qty}.")
            return

    st.session_state.cart.append({
        "product_id": p_id,
        "product_name": p_name,
        "price": Decimal(str(p_price)),
        "quantity": quantity,
        "total": item_total,
    })
    st.success(f"Added {p_name} (qty: {quantity}) to cart.")


def _update_cart_quantity(index, new_quantity):
    """Update the quantity of a cart item and recalculate its total.

    Args:
        index: Index of the item in the cart list.
        new_quantity: The new positive quantity.

    Side effects:
        Mutates st.session_state.cart.
    """
    if not (0 <= index < len(st.session_state.cart)):
        return
    item = st.session_state.cart[index]
    conn = get_conn()
    try:
        product = get_product_by_id(conn, item["product_id"])
    finally:
        put_conn(conn)

    if not product:
        st.error(f"Product ID {item['product_id']} no longer exists.")
        return

    _pid, _pname, p_price, stock = product

    if new_quantity < 1:
        st.error("Quantity must be at least 1.")
        return
    if new_quantity > stock:
        st.error(
            f"Insufficient stock for {item['product_name']}. "
            f"Available: {stock}."
        )
        return

    item["quantity"] = new_quantity
    item["total"] = Decimal(str(p_price)) * new_quantity


def _remove_from_cart(index):
    """Remove a cart item by its list index.

    Side effects:
        Mutates st.session_state.cart.
    """
    if 0 <= index < len(st.session_state.cart):
        st.session_state.cart.pop(index)


def _clear_cart():
    """Empty the cart and reset checkout state."""
    st.session_state.cart = []
    st.session_state.receipt = None
    st.session_state.checkout_done = False
    st.session_state.receipt_saved = False


def _do_checkout(customer, cart):
    """Finalize a bill and store the receipt in session state.

    Args:
        customer: Customer tuple.
        cart: List of cart item dicts.

    Returns:
        True on success, False on failure.

    Side effects:
        Writes bill records and deducts inventory via finalize_bill.
        Stores the receipt in session state on success.
    """
    conn = get_conn()
    try:
        bill = finalize_bill(conn, customer, cart)
    except (ValueError, RuntimeError, psycopg.Error) as exc:
        st.error(f"Checkout failed: {exc}")
        return False
    finally:
        put_conn(conn)

    st.session_state.receipt = bill
    st.session_state.checkout_done = True
    st.session_state.receipt_saved = False
    return True


def page_billing():
    """Render the billing page with cart and checkout."""
    st.title("Billing")

    # ---- Customer selection ----
    st.subheader("1. Customer")
    phone = st.text_input(
        "Customer phone number (10 digits)",
        max_chars=10,
        key="bill_phone",
    )

    col_find, col_clear = st.columns([1, 1])
    with col_find:
        if st.button("Find / Register Customer", key="find_cust_btn"):
            if not phone or not phone.strip().isdigit() or len(phone.strip()) != 10:
                st.error("Enter a valid 10-digit phone number.")
            else:
                conn = get_conn()
                try:
                    customer = get_customer_by_phone(conn, phone.strip())
                finally:
                    put_conn(conn)
                if customer:
                    st.session_state.customer = customer
                    st.session_state.customer_phone = phone.strip()
                    st.success(
                        f"Welcome back, **{customer[1]}** (ID: {customer[0]})"
                    )
                else:
                    st.warning("Customer not found. Register below.")
                    st.session_state.customer = None
                    st.session_state.customer_phone = phone.strip()
    with col_clear:
        if st.button("Clear Customer", key="clear_cust_btn"):
            st.session_state.customer = None
            st.session_state.customer_phone = ""
            st.rerun()

    if st.session_state.customer is None:
        with st.expander("Register New Customer", expanded=False):
            with st.form("bill_register_form", clear_on_submit=True):
                rname = st.text_input("Full name *")
                raddr = st.text_area("Address *")
                rphone = st.text_input(
                    "Phone number (10 digits) *",
                    max_chars=10,
                    value=st.session_state.customer_phone,
                )
                rsubmitted = st.form_submit_button("Register")
                if rsubmitted:
                    try:
                        rname = validate_customer_name(rname)
                        raddr = validate_address(raddr)
                        rphone = validate_phone_number(rphone)
                        conn = get_conn()
                        try:
                            cust = create_customer(conn, rname, raddr, rphone)
                        finally:
                            put_conn(conn)
                        st.session_state.customer = cust
                        st.session_state.customer_phone = rphone
                        st.success(
                            f"Registered **{cust[1]}** (ID: {cust[0]})"
                        )
                    except ValueError as e:
                        st.error(str(e))

    # ---- Product entry ----
    st.subheader("2. Add Products")
    if st.session_state.customer:
        c1, c2 = st.columns([3, 1])
        with c1:
            pid = st.number_input(
                "Product ID",
                min_value=1,
                step=1,
                key="bill_pid",
            )
        with c2:
            qty = st.number_input(
                "Quantity",
                min_value=1,
                step=1,
                value=1,
                key="bill_qty",
            )
        if st.button("Add to Cart", type="primary", key="add_cart_btn"):
            _add_to_cart(pid, qty)
    else:
        st.info("Search or register a customer first.")

    # ---- Cart display with inline quantity editing ----
    st.subheader("3. Cart")
    if st.session_state.cart:
        cart_changed = False
        for i, item in enumerate(st.session_state.cart):
            cols = st.columns([3, 2, 1, 2, 1])
            with cols[0]:
                st.markdown(f"**{item['product_name']}**")
            with cols[1]:
                st.markdown(f"Rs. {item['price']:.2f}")
            with cols[2]:
                new_qty = st.number_input(
                    "Qty",
                    min_value=1,
                    step=1,
                    value=item["quantity"],
                    key=f"cart_qty_{i}",
                    label_visibility="collapsed",
                )
                if new_qty != item["quantity"]:
                    _update_cart_quantity(i, new_qty)
                    cart_changed = True
            with cols[3]:
                st.markdown(f"Rs. {item['total']:.2f}")
            with cols[4]:
                if st.button("🗑", key=f"cart_rm_{i}"):
                    _remove_from_cart(i)
                    cart_changed = True
        if cart_changed:
            st.rerun()

        # Totals
        grand_total = sum(
            Decimal(str(item["total"])) for item in st.session_state.cart
        )
        st.markdown(f"### Grand Total: Rs. {grand_total:.2f}")

        # Clear cart
        if st.button("Clear Cart", key="clear_cart_btn"):
            _clear_cart()
            st.rerun()

        # Checkout
        st.subheader("4. Checkout")
        if st.button("Finalize Bill", type="primary", key="checkout_btn"):
            if _do_checkout(st.session_state.customer, st.session_state.cart):
                st.session_state.cart = []
                st.rerun()
    else:
        st.info("Cart is empty.")

    # ---- Receipt ----
    if st.session_state.checkout_done and st.session_state.receipt:
        bill = st.session_state.receipt
        st.subheader("✅ Receipt")
        receipt_text = format_receipt(bill)
        st.text(receipt_text)

        receipt_bytes = (receipt_text + "\n").encode("utf-8")
        st.download_button(
            label="📥 Download Receipt (.txt)",
            data=receipt_bytes,
            file_name=f"receipt_{bill['bill_id']}.txt",
            mime="text/plain",
        )

        # Persist receipt to disk only once, after successful checkout.
        if not st.session_state.receipt_saved:
            save_receipt(bill, Path("generated") / f"receipt_{bill['bill_id']}.txt")
            st.session_state.receipt_saved = True

        if st.button("Start New Bill", key="new_bill_btn"):
            _clear_cart()
            st.session_state.customer = None
            st.session_state.customer_phone = ""
            st.rerun()


# ---------------------------------------------------------------------------
# Page: QR Code Generation
# ---------------------------------------------------------------------------

def page_qr():
    """Render the QR PDF generation page."""
    st.title("Generate Product QR PDF")

    conn = get_conn()
    try:
        products = get_all_products(conn)
    finally:
        put_conn(conn)

    if not products:
        st.info("No products found.")
        return

    st.write(f"**{len(products)} products** will be included in the PDF.")

    if st.button("Generate QR PDF", type="primary"):
        # Generate in memory to avoid temporary files for the download.
        pdf_bytes = generate_product_qr_pdf(products)
        st.success("QR PDF generated successfully.")
        st.download_button(
            label="📥 Download QR PDF",
            data=pdf_bytes,
            file_name="product_qr_codes.pdf",
            mime="application/pdf",
        )


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

def main():
    """Route to the selected page based on sidebar navigation."""
    page = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Customer Management",
            "Products",
            "Billing",
            "QR Code Generation",
        ],
        key="nav",
    )

    if page == "Dashboard":
        page_dashboard()
    elif page == "Customer Management":
        page_customers()
    elif page == "Products":
        page_products()
    elif page == "Billing":
        page_billing()
    elif page == "QR Code Generation":
        page_qr()


if __name__ == "__main__":
    main()
