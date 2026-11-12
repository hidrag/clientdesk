from modules.db_connection import get_connection
from modules.product import get_all_products, get_product_by_id

conn = get_connection()

try:
    products = get_all_products(conn)
    print("Total products:", len(products))

    product = get_product_by_id(conn, 1)
    print("Product ID 1:", product)

finally:
    conn.close()