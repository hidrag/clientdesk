from pathlib import Path

from modules.db_connection import get_connection
from modules.product import get_all_products
from modules.qr_generator import generate_product_qr_pdf


def main():
    conn = get_connection()

    try:
        products = get_all_products(conn)

        if not products:
            print("No products found.")
            return

        output_dir = Path("generated")
        output_dir.mkdir(exist_ok=True)

        output_path = output_dir / "product_qr_codes.pdf"

        result = generate_product_qr_pdf(
            products,
            str(output_path)
        )

        print("QR PDF generated successfully!")
        print("Products:", len(products))
        print("File:", result)
        print("File size:", output_path.stat().st_size, "bytes")

    except Exception as error:
        print("QR generation error:", error)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
