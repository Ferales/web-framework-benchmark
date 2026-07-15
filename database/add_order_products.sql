INSERT INTO order_products (order_id, product_id, quantity)
SELECT 
    (floor(random() * 100000) + 1)::BIGINT,  -- Losowy order_id (od 1 do 100000)
    (floor(random() * 100) + 1)::BIGINT,  -- Losowy product_id (od 1 do 100)
    floor(random() * 10 + 1)  -- Losowa ilość zamówionych produktów (od 1 do 10)
FROM generate_series(1, 300000)
ON CONFLICT (order_id, product_id) DO NOTHING;  -- Ignorowanie duplikatów
