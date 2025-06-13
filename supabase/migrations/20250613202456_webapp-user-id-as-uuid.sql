-- Ensure webapp_user_id is UUID type in test tables
ALTER TABLE public.forex_test
ALTER COLUMN webapp_user_id TYPE UUID USING webapp_user_id::UUID;

ALTER TABLE public.investments_test
ALTER COLUMN webapp_user_id TYPE UUID USING webapp_user_id::UUID;

ALTER TABLE public.transactions_test
ALTER COLUMN webapp_user_id TYPE UUID USING webapp_user_id::UUID;

ALTER TABLE public.transfers_test
ALTER COLUMN webapp_user_id TYPE UUID USING webapp_user_id::UUID;

ALTER TABLE public.users_test
ALTER COLUMN webapp_user_id TYPE UUID USING webapp_user_id::UUID;

-- Ensure webapp_user_id is UUID type in production tables
ALTER TABLE public.forex
ALTER COLUMN webapp_user_id TYPE UUID USING webapp_user_id::UUID;

ALTER TABLE public.investments
ALTER COLUMN webapp_user_id TYPE UUID USING webapp_user_id::UUID;

ALTER TABLE public.transactions
ALTER COLUMN webapp_user_id TYPE UUID USING webapp_user_id::UUID;

ALTER TABLE public.transfers
ALTER COLUMN webapp_user_id TYPE UUID USING webapp_user_id::UUID;

ALTER TABLE public.users
ALTER COLUMN webapp_user_id TYPE UUID USING webapp_user_id::UUID;
