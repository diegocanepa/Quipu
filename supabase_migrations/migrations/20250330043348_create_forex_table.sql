CREATE TABLE IF NOT EXISTS forex (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    description TEXT,
    amount FLOAT8,
    currency_from TEXT,
    currency_to TEXT,
    price FLOAT8,
    date TIMESTAMPTZ,
    action TEXT
);