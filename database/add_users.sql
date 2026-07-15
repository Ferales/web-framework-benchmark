ALTER SEQUENCE users_id_seq RESTART WITH 1;

INSERT INTO users (name, email, password, age)
SELECT 
    'User_' || gs,
    'user' || gs || '@example.com',
    '$2a$10$t351Ox6sYleHN9GHRzmIXOUDrzMWt/TZrbwJdoAGveUEqENlllwxu',
    floor(random() * (60 - 18 + 1) + 18)
FROM generate_series(1, 10000) AS gs;
