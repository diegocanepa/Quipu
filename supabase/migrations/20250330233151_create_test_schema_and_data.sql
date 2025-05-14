-- supabase/migrations/YYYYMMDDHHMMSS_create_test_schema_and_tables.sql

-- Crear las tablas con el sufijo _test en el esquema 'public'

-- Crear la tabla 'forex_test' en el esquema 'public'
CREATE TABLE IF NOT EXISTS public.forex_test (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    description TEXT,
    amount FLOAT8,
    currency_from TEXT,
    currency_to TEXT,
    price FLOAT8,
    date TIMESTAMPTZ,
    action TEXT
);

-- Crear la tabla 'investments_test' en el esquema 'public'
CREATE TABLE IF NOT EXISTS public.investments_test (
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

-- Crear la tabla 'transactions_test' en el esquema 'public'
CREATE TABLE IF NOT EXISTS public.transactions_test (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    description TEXT,
    amount FLOAT8,
    currency TEXT,
    category TEXT,
    date TIMESTAMPTZ,
    action TEXT
);

-- Crear la tabla 'transfers_test' en el esquema 'public'
CREATE TABLE IF NOT EXISTS public.transfers_test (
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

-- Insertar registros de prueba para public.forex_test
DO $$
DECLARE
    num_records INTEGER := floor(random() * 51 + 100); -- Número aleatorio entre 100 y 150
    start_date TIMESTAMP := '2025-01-01 00:00:00'::TIMESTAMP;
    end_date TIMESTAMP := NOW();
    time_diff INTERVAL := end_date - start_date;
BEGIN
    FOR i IN 1..num_records LOOP
        INSERT INTO public.forex_test (description, amount, currency_from, currency_to, price, date, action)
        VALUES (
            'Forex Trade ' || i,
            round((random() * 1000)::numeric, 2),
            CASE floor(random() * 3)
                WHEN 0 THEN 'USD'
                WHEN 1 THEN 'ARS'
                ELSE 'ARS'
            END,
            CASE floor(random() * 3)
                WHEN 0 THEN 'USD'
                WHEN 1 THEN 'ARS'
                ELSE 'ARS'
            END,
            round((random() * 1.5 + 0.5)::numeric, 4),
            start_date + time_diff * random(),
            CASE floor(random() * 2)
                WHEN 0 THEN 'Compra'
                ELSE 'Venta'
            END
        );
    END LOOP;
END $$;

-- Insertar registros de prueba para public.investments_test
DO $$
DECLARE
    num_records INTEGER := floor(random() * 51 + 100);
    start_date TIMESTAMP := '2025-01-01 00:00:00'::TIMESTAMP;
    end_date TIMESTAMP := NOW();
    time_diff INTERVAL := end_date - start_date;
    platforms TEXT[] := ARRAY['IOL', 'Cocos', 'Binance', 'Nexo'];
    categories TEXT[] := ARRAY['Stocks', 'Crypto', 'Bonds', 'Real Estate'];
    currencies TEXT[] := ARRAY['USD', 'ARS', 'BTC'];
BEGIN
    FOR i IN 1..num_records LOOP
        INSERT INTO public.investments_test (description, category, date, action, platform, amout, price, currency)
        VALUES (
            'Investment ' || i,
            categories[floor(random() * array_length(categories, 1)) + 1],
            start_date + time_diff * random(),
            CASE floor(random() * 2)
                WHEN 0 THEN 'buy'
                ELSE 'sell'
            END,
            platforms[floor(random() * array_length(platforms, 1)) + 1],
            round((random() * 100)::numeric, 4),
            round((random() * 5000)::numeric, 2),
            currencies[floor(random() * array_length(currencies, 1)) + 1]
        );
    END LOOP;
END $$;

-- Insertar registros de prueba para public.transactions_test
DO $$
DECLARE
    num_records INTEGER := floor(random() * 51 + 100);
    start_date TIMESTAMP := '2025-01-01 00:00:00'::TIMESTAMP;
    end_date TIMESTAMP := NOW();
    time_diff INTERVAL := end_date - start_date;
    currencies TEXT[] := ARRAY['ARS'];
    categories TEXT[] := ARRAY['Food', 'Utilities', 'Entertainment', 'Salary', 'Freelance Income', 'Rent', 'Travel'];
    actions TEXT[] := ARRAY['gasto', 'ingreso'];
BEGIN
    FOR i IN 1..num_records LOOP
        INSERT INTO public.transactions_test (description, amount, currency, category, date, action)
        VALUES (
            'Transaction ' || i,
            round((random() * 500)::numeric, 2),
            currencies[floor(random() * array_length(currencies, 1)) + 1],
            categories[floor(random() * array_length(categories, 1)) + 1],
            start_date + time_diff * random(),
            actions[floor(random() * array_length(actions, 1)) + 1]
        );
    END LOOP;
END $$;

-- Insertar registros de prueba para public.transfers_test
DO $$
DECLARE
    num_records INTEGER := floor(random() * 51 + 100);
    start_date TIMESTAMP := '2025-01-01 00:00:00'::TIMESTAMP;
    end_date TIMESTAMP := NOW();
    time_diff INTERVAL := end_date - start_date;
    wallets TEXT[] := ARRAY['Wise', 'Deel', 'Takenos', 'Revolut', 'Binance', 'Efectivo', 'Nexo', 'Banco'];
    currencies TEXT[] := ARRAY['USD', 'ARS'];
    categories TEXT[] := ARRAY['Personal', 'Business', 'Investment'];
BEGIN
    FOR i IN 1..num_records LOOP
        DECLARE
            wallet1 TEXT := wallets[floor(random() * array_length(wallets, 1)) + 1];
            wallet2 TEXT := wallets[floor(random() * array_length(wallets, 1)) + 1];
            initial_amount_val FLOAT := round((random() * 1000)::numeric, 2);
            fee FLOAT := round((random() * 10)::numeric, 2);
            final_amount_val FLOAT := initial_amount_val - fee;
        BEGIN
            -- Asegurarse de que wallet_from y wallet_to sean diferentes
            WHILE wallet1 = wallet2 LOOP
                wallet2 := wallets[floor(random() * array_length(wallets, 1)) + 1];
            END LOOP;

            INSERT INTO public.transfers_test (description, category, date, action, wallet_from, wallet_to, initial_amount, final_amount, currency)
            VALUES (
                'Transfer ' || i,
                categories[floor(random() * array_length(categories, 1)) + 1],
                start_date + time_diff * random(),
                'Transfer',
                wallet1,
                wallet2,
                initial_amount_val,
                final_amount_val,
                currencies[floor(random() * array_length(currencies, 1)) + 1]
            );
        END;
    END LOOP;
END $$;
