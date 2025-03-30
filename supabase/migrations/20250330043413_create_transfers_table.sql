CREATE TABLE IF NOT EXISTS transfers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    description TEXT,
    category TEXT,
    date TIMESTAMPTZ,
    action TEXT,
    wallet_from TEXT,
    wallet_to TEXT,
    initial_amount FLOAT8,
    final_amount FLOAT8,
    currency TEXT
);