-- =====================================================
-- MORE SUPERMARKET MEGA
-- PRODUCT SEED DATA
-- =====================================================

INSERT INTO product_details
    (p_name, p_price, stock_on_hand)
VALUES
    ('RICE 1 KG', 46.00, 75),
    ('BASMATI RICE 1 KG', 110.00, 45),
    ('ATTA 1 KG', 38.00, 80),
    ('MAIDA 1 KG', 43.00, 50),
    ('SUJI 1 KG', 47.00, 55),
    ('BESAN 1 KG', 97.00, 40),
    ('MOONG DAL 1 KG', 112.00, 50),
    ('MASOOR DAL 1 KG', 90.00, 55),
    ('ARHAR DAL 1 KG', 126.00, 45),
    ('CHANA DAL 1 KG', 89.00, 60),
    ('URAD DAL 1 KG', 123.00, 40),
    ('RAJMA 1 KG', 145.00, 35),
    ('KABULI CHANA 1 KG', 120.00, 40),
    ('DRIED GREEN PEAS 1 KG', 85.00, 35),
    ('SUGAR 1 KG', 55.00, 70),
    ('JAGGERY 1 KG', 66.00, 40),
    ('IODISED SALT 1 KG', 22.00, 85),
    ('MUSTARD OIL 1 LITRE', 203.00, 55),
    ('SUNFLOWER OIL 1 LITRE', 192.00, 50),
    ('SOYABEAN OIL 1 LITRE', 167.00, 60),
    ('GROUNDNUT OIL 1 LITRE', 208.00, 35),
    ('DESI GHEE 500 GM', 360.00, 30),
    ('BUTTER 100 GM', 62.00, 40),
    ('MILK 1 LITRE', 62.00, 65),
    ('CURD 400 GM', 45.00, 35),
    ('PANEER 200 GM', 95.00, 30),
    ('EGGS 12 PCS', 84.00, 50),
    ('TEA 250 GM', 75.00, 45),
    ('COFFEE 100 GM', 95.00, 35),
    ('TURMERIC POWDER 200 GM', 45.00, 45),
    ('RED CHILLI POWDER 200 GM', 65.00, 40),
    ('CORIANDER POWDER 200 GM', 50.00, 45),
    ('CUMIN SEEDS 100 GM', 48.00, 35),
    ('BLACK PEPPER 100 GM', 95.00, 30),
    ('GARAM MASALA 100 GM', 78.00, 35),
    ('JEERA POWDER 100 GM', 55.00, 40),
    ('POTATO 1 KG', 23.00, 90),
    ('ONION 1 KG', 54.00, 85),
    ('TOMATO 1 KG', 42.00, 65),
    ('BRINJAL 1 KG', 43.00, 40),
    ('CAULIFLOWER 1 PC', 45.00, 35),
    ('CABBAGE 1 KG', 38.00, 40),
    ('LADY FINGER 1 KG', 55.00, 35),
    ('BOTTLE GOURD 1 KG', 40.00, 30),
    ('GINGER 500 GM', 70.00, 35),
    ('GARLIC 500 GM', 90.00, 40),
    ('BANANA 1 DOZEN', 65.00, 40),
    ('APPLE 1 KG', 180.00, 35),
    ('ORANGE 1 KG', 110.00, 30),
    ('BISCUIT PACK 100 GM', 20.00, 85),
    ('MARIE BISCUIT 250 GM', 35.00, 70),
    ('INSTANT NOODLES 70 GM', 15.00, 100),
    ('VERMICELLI 500 GM', 55.00, 45),
    ('POHA 500 GM', 38.00, 50),
    ('MURI PUFFED RICE 500 GM', 40.00, 50),
    ('CORN FLAKES 500 GM', 190.00, 30),
    ('TOMATO KETCHUP 500 GM', 115.00, 35),
    ('SOYA SAUCE 200 ML', 65.00, 30),
    ('GREEN CHILLI SAUCE 200 GM', 70.00, 30),
    ('PICKLE 500 GM', 140.00, 35)

ON CONFLICT (p_name) DO NOTHING;


-- Verify product insertion

SELECT COUNT(*) AS total_products
FROM product_details;

SELECT *
FROM product_details
ORDER BY p_id;
