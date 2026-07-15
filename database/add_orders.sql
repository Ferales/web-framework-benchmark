-- Ustawienie ID dla nowych zamówień na początek
ALTER SEQUENCE orders_id_seq RESTART WITH 1;

-- Skrypt do generowania 100000 zamówień
INSERT INTO orders (user_id, order_date, status)
SELECT 
    (floor(random() * 10000) + 1),  -- Losowy user_id od 1 do 10000
    NOW() - (floor(random() * 365) || ' days')::interval,  -- Losowa data zamówienia w ciągu ostatnich 365 dni
    CASE
        WHEN random() < 0.6 THEN 'Pending'
        WHEN random() < 0.9 THEN 'Completed'
        ELSE 'Cancelled'
    END
FROM generate_series(1, 100000) AS gs;
