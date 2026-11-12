-- =====================================================
-- MORE SUPERMARKET MEGA
-- PostgreSQL Database Schema
-- =====================================================

-- -----------------------------------------------------
-- 1. CUSTOMER DETAILS
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS cust_details (
    cust_id INTEGER GENERATED ALWAYS AS IDENTITY
        (START WITH 1000 INCREMENT BY 1) PRIMARY KEY,

    full_name VARCHAR(200) NOT NULL,

    address VARCHAR(500) NOT NULL,

    phone_number VARCHAR(15) NOT NULL UNIQUE,

    CONSTRAINT chk_customer_name
        CHECK (LENGTH(TRIM(full_name)) >= 3)
);


-- -----------------------------------------------------
-- 2. PRODUCT DETAILS
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS product_details (
    p_id INTEGER GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    p_name VARCHAR(200) NOT NULL UNIQUE,

    p_price NUMERIC(10,2) NOT NULL,

    stock_on_hand INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT chk_product_price
        CHECK (p_price >= 0),

    CONSTRAINT chk_product_stock
        CHECK (stock_on_hand >= 0)
);


-- -----------------------------------------------------
-- 3. BILL SUMMARY
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS bill_summary_tb (
    bill_id INTEGER GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    c_id INTEGER NOT NULL,

    full_name VARCHAR(200) NOT NULL,

    total_bill_value NUMERIC(10,2) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_bill_customer
        FOREIGN KEY (c_id)
        REFERENCES cust_details(cust_id),

    CONSTRAINT chk_bill_total
        CHECK (total_bill_value >= 0)
);


-- -----------------------------------------------------
-- 4. BILL DETAILS
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS bill_details (
    sl_no INTEGER GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    bill_id INTEGER NOT NULL,

    c_id INTEGER NOT NULL,

    c_name VARCHAR(200) NOT NULL,

    p_id INTEGER NOT NULL,

    p_name VARCHAR(200) NOT NULL,

    p_price NUMERIC(10,2) NOT NULL,

    quantity INTEGER NOT NULL,

    total_bill_amount NUMERIC(10,2) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_bill_detail_summary
        FOREIGN KEY (bill_id)
        REFERENCES bill_summary_tb(bill_id),

    CONSTRAINT fk_bill_detail_customer
        FOREIGN KEY (c_id)
        REFERENCES cust_details(cust_id),

    CONSTRAINT fk_bill_detail_product
        FOREIGN KEY (p_id)
        REFERENCES product_details(p_id),

    CONSTRAINT chk_bill_detail_price
        CHECK (p_price >= 0),

    CONSTRAINT chk_bill_detail_quantity
        CHECK (quantity > 0),

    CONSTRAINT chk_bill_detail_total
        CHECK (total_bill_amount >= 0)
);


-- -----------------------------------------------------
-- 5. INDEXES
-- -----------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_bill_customer
    ON bill_summary_tb(c_id);

CREATE INDEX IF NOT EXISTS idx_bill_detail_bill
    ON bill_details(bill_id);

CREATE INDEX IF NOT EXISTS idx_bill_detail_product
    ON bill_details(p_id);


-- -----------------------------------------------------
-- SCHEMA CREATION COMPLETE
-- -----------------------------------------------------

