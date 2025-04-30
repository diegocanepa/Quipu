CREATE TABLE IF NOT EXISTS investments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    description TEXT,
    category TEXT,
    date TIMESTAMPTZ,
    action TEXT,
    platform TEXT,
    amout FLOAT8,
    price FLOAT8,
    currency TEXT
);