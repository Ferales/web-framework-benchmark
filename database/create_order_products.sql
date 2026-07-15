CREATE TABLE order_products (
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,  -- Ilość zamówionych produktów
    PRIMARY KEY (order_id, product_id),  -- Klucz główny złożony
    FOREIGN KEY (order_id) REFERENCES orders(id),  -- Klucz obcy do tabeli orders
    FOREIGN KEY (product_id) REFERENCES products(id)  -- Klucz obcy do tabeli products
);
