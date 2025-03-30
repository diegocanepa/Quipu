CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    description TEXT,
    amount FLOAT8,
    currency TEXT,
    category TEXT,
    date TIMESTAMPTZ,
    action TEXT
);