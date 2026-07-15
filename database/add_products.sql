-- Ustawienie ID dla nowych produktów na początek
ALTER SEQUENCE products_id_seq RESTART WITH 1;

-- Skrypt do generowania 1000 produktów
INSERT INTO products (name, price, stock)
SELECT 
    'Product_' || gs,  -- Generowanie unikalnych nazw produktów
    round((random() * (500 - 10) + 10)::numeric, 2),  -- Losowa cena w przedziale 10-500, zaokrąglona do 2 miejsc po przecinku
    floor(random() * (100 - 1 + 1) + 1)  -- Losowa liczba produktów na stanie w przedziale od 1 do 100
FROM generate_series(1, 1000) AS gs;

