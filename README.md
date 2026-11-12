# More Supermarket Mega

A complete CLI-based supermarket billing application built with Python and PostgreSQL.

---

## Project Overview

More Supermarket Mega is a QR-code-based supermarket billing system designed as a Python learning and portfolio project. It covers database connectivity, customer management, product inventory, QR code generation and scanning, transactional billing, and receipt generation — all from the terminal.

### Objectives

- Apply Python programming fundamentals (functions, modules, error handling, Decimal arithmetic).
- Work with PostgreSQL for persistent data storage.
- Use parameterized queries and transactions for data integrity.
- Integrate QR code generation and webcam scanning.
- Build a complete CLI workflow from customer identification through bill finalisation.

---

## Key Features

| Feature | Description |
|---|---|
| Customer registration | Collect name, address and phone; validate; prevent duplicate phone numbers |
| Customer lookup | Find customers by phone number |
| Product catalogue | View all products with ID, name, price and stock |
| QR code PDF generation | Generate a printable A4 PDF with QR codes for every product |
| QR code scanning | Scan product QR codes via webcam (OpenCV); manual ID fallback |
| Billing | Build a cart, lock inventory, save bill summary + details atomically |
| Receipt generation | Display a formatted receipt and save it as a `.txt` file |
| Inventory deduction | Stock is decremented only after a successful bill |
| Transaction safety | Failed bills roll back completely — no partial inserts or stock changes |

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.14 | Application logic |
| PostgreSQL 18 | Database (hosted on Neon) |
| Psycopg 3 | Python → PostgreSQL driver |
| OpenCV (`opencv-python`) | Webcam QR scanning |
| `qrcode[pil]` | QR code image generation |
| ReportLab (`reportlab`) | PDF generation for product labels |
| `python-dotenv` | Environment variable management |

---

## Architecture

```
User
  ↓
CLI Menu (main.py)
  ↓
┌─── modules/ ──────────────────┐
│  db_connection.py  → PostgreSQL │
│  customer.py       → CRUD ops   │
│  product.py        → queries    │
│  billing.py        → tx logic   │
│  receipt.py        → formatting │
│  qr_generator.py   → PDF        │
│  qr_scanner.py     → webcam     │
│  validation.py     → input      │
└─────────────────────────────────┘
```

### Folder Structure

```
ClientDesk/
├── main.py                   # CLI entry point
├── modules/
│   ├── __init__.py
│   ├── billing.py
│   ├── customer.py
│   ├── db_connection.py
│   ├── product.py
│   ├── qr_generator.py
│   ├── qr_scanner.py
│   ├── receipt.py
│   └── validation.py
├── database/
│   ├── 01_create_tables.sql
│   └── 02_insert_products.sql
├── generated/                # Output directory (PDFs, receipts)
├── tests/                    # Test scripts
├── .env                      # (your local credentials, not committed)
├── .env.example
├── requirements.txt
└── README.md
```

---

## Database Schema

Four tables:

### `cust_details`

| Column | Type | Notes |
|---|---|---|
| `cust_id` | INTEGER (PK) | `GENERATED ALWAYS AS IDENTITY`, starts at 1000 |
| `full_name` | VARCHAR(200) | NOT NULL, min 3 chars |
| `address` | VARCHAR(500) | NOT NULL |
| `phone_number` | VARCHAR(15) | UNIQUE, NOT NULL |

### `product_details`

| Column | Type | Notes |
|---|---|---|
| `p_id` | INTEGER (PK) | `GENERATED ALWAYS AS IDENTITY` |
| `p_name` | VARCHAR(200) | UNIQUE, NOT NULL |
| `p_price` | NUMERIC(10,2) | NOT NULL, >= 0 |
| `stock_on_hand` | INTEGER | NOT NULL DEFAULT 0, >= 0 |

### `bill_summary_tb`

| Column | Type | Notes |
|---|---|---|
| `bill_id` | INTEGER (PK) | `GENERATED ALWAYS AS IDENTITY` |
| `c_id` | INTEGER | FK → `cust_details.cust_id` |
| `full_name` | VARCHAR(200) | Denormalised customer name |
| `total_bill_value` | NUMERIC(10,2) | NOT NULL, >= 0 |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

### `bill_details`

| Column | Type | Notes |
|---|---|---|
| `sl_no` | INTEGER (PK) | `GENERATED ALWAYS AS IDENTITY` |
| `bill_id` | INTEGER | FK → `bill_summary_tb.bill_id` |
| `c_id` | INTEGER | FK → `cust_details.cust_id` |
| `c_name` | VARCHAR(200) | Denormalised |
| `p_id` | INTEGER | FK → `product_details.p_id` |
| `p_name` | VARCHAR(200) | Denormalised |
| `p_price` | NUMERIC(10,2) | Snapshot at sale time |
| `quantity` | INTEGER | > 0 |
| `total_bill_amount` | NUMERIC(10,2) | >= 0 |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

Indexes exist on `bill_summary_tb(c_id)`, `bill_details(bill_id)` and `bill_details(p_id)`.

---

## Setup

### Prerequisites

- Python 3.12+
- A PostgreSQL database (local or [Neon](https://neon.tech))
- Webcam (optional — manual product ID entry works without it)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ClientDesk
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it:

- **Windows:** `.venv\Scripts\activate`
- **macOS/Linux:** `source .venv/bin/activate`

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Neon PostgreSQL

Create a free database at [Neon](https://neon.tech). Copy your connection string.

### 5. Environment Variables

Create `.env` in the project root:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
```

**Never commit `.env`.**

### 6. Run SQL Scripts

Run the schema script against your Neon database:

```bash
psql -d "postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require" -f database/01_create_tables.sql
```

Then seed the products:

```bash
psql -d "postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require" -f database/02_insert_products.sql
```

---

## Usage

Launch the CLI application:

```bash
python main.py
```

### Main Menu

```
MORE SUPERMARKET MEGA
=======================
1. Register Customer
2. Start New Billing
3. View Products
4. Generate Product QR PDF
5. Exit
```

### Register a Customer

1. Select option **1**.
2. Enter the customer's full name, address, and 10-digit phone number.
3. Duplicate phone numbers are rejected.
4. On success, the customer ID is displayed.

### Start New Billing

1. Select option **2**.
2. Enter the customer's 10-digit phone number.
   - Existing customer → greeting shown.
   - Not found → prompted to register.
3. **Add products:**
   - Choose `s` to scan a QR code via webcam, or `m` to enter a product ID manually.
   - Enter the quantity.
   - Repeat until finished.
4. The bill is finalised atomically:
   - Bill summary and details are saved.
   - Inventory is deducted.
   - If any step fails, **everything** rolls back.
5. A formatted receipt is displayed and saved to `generated/receipt_{BILL_ID}.txt`.

### View Products

Select option **3** to see a table of all products with ID, name, price and stock.

### Generate QR PDF

Select option **4** to generate a printable A4 PDF (`generated/product_qr_codes.pdf`) with QR codes for every product. Each label shows the product ID, name, price and stock. Layout: 3 columns × 5 rows per page.

---

## QR Scanning

The scanner uses OpenCV to access the webcam. It returns the decoded QR content (the product ID) and does **not** perform any database operations.

If OpenCV is not installed or the webcam is unavailable, the application falls back to manual product-ID entry — the billing workflow works fully without a camera.

---

## Receipt Generation

After a successful bill, a formatted receipt is:

1. Displayed in the terminal.
2. Saved to `generated/receipt_{BILL_ID}.txt`.

The receipt includes: store name, bill ID, customer ID, customer name, date/time, product lines (name, price, qty, total), grand total, and a thank-you message.

Receipts are **only** generated for successful transactions.

---

## Inventory Management

- Stock is checked before finalising a bill.
- Stock is deducted only **after** the bill summary and details are saved.
- The entire billing operation runs inside a PostgreSQL transaction.
- If any part fails (e.g., insufficient stock, database error), the transaction rolls back — no partial inserts, no phantom deductions.
- Product rows are locked with `FOR UPDATE` during billing to prevent race conditions.

---

## Error Handling

- Invalid menu choices → friendly message, menu redisplayed.
- Invalid input (empty name, non-numeric ID, etc.) → caught and explained.
- Database connection failure → caught, application exits gracefully.
- KeyboardInterrupt (`Ctrl+C`) → clean resource release.
- Billing errors → full rollback, user notified, no data loss.

---

## Testing

### Static Checks

```bash
python -m compileall modules/ main.py
```

### Connection Test

```bash
python test_connection.py
```

### Customer Test

```bash
python test_customer.py
```

### Product Test

```bash
python test_product.py
```

### Billing Test

```bash
python test_billing.py
```

### QR PDF Generation Test

```bash
python test_qr_generator.py
```

### Transaction Rollback

The billing test (`test_billing.py`) verifies that a failed billing operation does **not** create bill records or deduct inventory.

---

## Known Limitations

- Webcam scanning requires a physical camera and OpenCV GUI support. In headless environments, use manual product ID entry.
- The PDF QR label layout (3 columns × 5 rows) may require slight adjustment depending on the paper margins of your printer.
- Customer lookup is by phone number only (no name search).

---

## Future Scope

- Streamlit web interface (when the CLI is fully stable).
- Email receipt delivery.
- Customer purchase history.
- Barcode support alongside QR codes.
- Sales reporting and analytics.
- Multi-user / staff login.

---

## License

Personal learning and portfolio project.
