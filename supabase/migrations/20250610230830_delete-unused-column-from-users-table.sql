-- Remove telegram name columns from users table
ALTER TABLE public.users
    DROP COLUMN IF EXISTS telegram_username,
    DROP COLUMN IF EXISTS telegram_first_name,
    DROP COLUMN IF EXISTS telegram_last_name;

-- Remove telegram name columns from users_test table
ALTER TABLE public.users_test
    DROP COLUMN IF EXISTS telegram_username,
    DROP COLUMN IF EXISTS telegram_first_name,
    DROP COLUMN IF EXISTS telegram_last_name; 