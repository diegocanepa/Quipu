-- Fix webapp_user_id column type mismatch
-- The users table has webapp_user_id as TEXT, but financial tables have it as UUID
-- This causes errors when trying to insert non-UUID values like "123456"

-- Fix forex_test table
ALTER TABLE public.forex_test ALTER COLUMN webapp_user_id TYPE TEXT;

-- Fix investments_test table  
ALTER TABLE public.investments_test ALTER COLUMN webapp_user_id TYPE TEXT;

-- Fix transactions_test table
ALTER TABLE public.transactions_test ALTER COLUMN webapp_user_id TYPE TEXT;

-- Fix transfers_test table
ALTER TABLE public.transfers_test ALTER COLUMN webapp_user_id TYPE TEXT;

-- Fix production tables too
ALTER TABLE public.forex ALTER COLUMN webapp_user_id TYPE TEXT;
ALTER TABLE public.investments ALTER COLUMN webapp_user_id TYPE TEXT;
ALTER TABLE public.transactions ALTER COLUMN webapp_user_id TYPE TEXT;
ALTER TABLE public.transfers ALTER COLUMN webapp_user_id TYPE TEXT;

-- Update comments to reflect the correct type
COMMENT ON COLUMN public.forex_test.webapp_user_id IS 'User ID from the web application (TEXT to match users table)';
COMMENT ON COLUMN public.investments_test.webapp_user_id IS 'User ID from the web application (TEXT to match users table)';
COMMENT ON COLUMN public.transactions_test.webapp_user_id IS 'User ID from the web application (TEXT to match users table)';
COMMENT ON COLUMN public.transfers_test.webapp_user_id IS 'User ID from the web application (TEXT to match users table)';

COMMENT ON COLUMN public.forex.webapp_user_id IS 'User ID from the web application (TEXT to match users table)';
COMMENT ON COLUMN public.investments.webapp_user_id IS 'User ID from the web application (TEXT to match users table)';
COMMENT ON COLUMN public.transactions.webapp_user_id IS 'User ID from the web application (TEXT to match users table)';
COMMENT ON COLUMN public.transfers.webapp_user_id IS 'User ID from the web application (TEXT to match users table)';