import qrcode
from io import BytesIO
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader


def generate_product_qr_pdf(products, output_path=None):
    """Generate a PDF containing product QR codes.

    Args:
        products: Sequence of tuples
            ``(product_id, product_name, price, stock)``.
        output_path: Optional filesystem path (str or ``pathlib.Path``).
            When provided, the PDF is saved to disk and the path is returned.
            When ``None``, the PDF is generated in memory.

    Returns:
        ``pathlib.Path`` when ``output_path`` is provided; otherwise ``bytes``
        containing the PDF content.

    Side effects:
        When saving to disk, creates parent directories and writes the PDF.
        No database access and no temporary files are created.
    """

    if not products:
        raise ValueError("No products available for QR generation.")

    # Normalize output target: disk path or in-memory buffer.
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_target = str(output_path)
    else:
        pdf_buffer = BytesIO()
        pdf_target = pdf_buffer

    # ReportLab accepts a string filename or a file-like object.
    pdf = canvas.Canvas(pdf_target, pagesize=A4)
    pdf.setTitle("More Supermarket Mega Product QR Labels")

    page_width, page_height = A4

    qr_size = 110
    columns = 3
    rows = 5

    cell_width = page_width / columns
    cell_height = 150

    top_margin = 55

    for index, product in enumerate(products):

        product_id, product_name, price, stock = product

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4
        )

        qr.add_data(str(product_id))
        qr.make(fit=True)

        qr_image = qr.make_image(
            fill_color="black",
            back_color="white"
        )

        image_buffer = BytesIO()
        qr_image.save(image_buffer, format="PNG")
        image_buffer.seek(0)

        position = index % (columns * rows)

        col = position % columns
        row = position // columns

        x = col * cell_width + (cell_width - qr_size) / 2

        y = (
            page_height
            - top_margin
            - (row * cell_height)
            - qr_size
        )

        pdf.drawImage(
            ImageReader(image_buffer),
            x,
            y,
            width=qr_size,
            height=qr_size
        )

        text_x = col * cell_width + cell_width / 2

        pdf.setFont("Helvetica-Bold", 10)

        pdf.drawCentredString(
            text_x,
            y - 12,
            f"ID: {product_id}"
        )

        pdf.setFont("Helvetica", 9)

        pdf.drawCentredString(
            text_x,
            y - 25,
            str(product_name)[:28]
        )

        pdf.drawCentredString(
            text_x,
            y - 38,
            f"Price: Rs. {price}"
        )

        pdf.drawCentredString(
            text_x,
            y - 51,
            f"Stock: {stock}"
        )

        if (
            (index + 1) % (columns * rows) == 0
            and (index + 1) < len(products)
        ):
            pdf.showPage()

    # Finalize the document before reading bytes or returning.
    pdf.save()

    if output_path is not None:
        return output_path

    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()
