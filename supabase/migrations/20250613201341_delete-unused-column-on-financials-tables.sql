-- Drop unused columns from test tables
ALTER TABLE public.forex_test
DROP COLUMN IF EXISTS telegram_user_id,
DROP COLUMN IF EXISTS whatsapp_user_id;

ALTER TABLE public.investments_test
DROP COLUMN IF EXISTS telegram_user_id,
DROP COLUMN IF EXISTS whatsapp_user_id;

ALTER TABLE public.transactions_test
DROP COLUMN IF EXISTS telegram_user_id,
DROP COLUMN IF EXISTS whatsapp_user_id;

ALTER TABLE public.transfers_test
DROP COLUMN IF EXISTS telegram_user_id,
DROP COLUMN IF EXISTS whatsapp_user_id;

-- Drop unused columns from production tables
ALTER TABLE public.forex
DROP COLUMN IF EXISTS telegram_user_id,
DROP COLUMN IF EXISTS whatsapp_user_id;

ALTER TABLE public.investments
DROP COLUMN IF EXISTS telegram_user_id,
DROP COLUMN IF EXISTS whatsapp_user_id;

ALTER TABLE public.transactions
DROP COLUMN IF EXISTS telegram_user_id,
DROP COLUMN IF EXISTS whatsapp_user_id;

ALTER TABLE public.transfers
DROP COLUMN IF EXISTS telegram_user_id,
DROP COLUMN IF EXISTS whatsapp_user_id;

-- Drop unused indexes
DROP INDEX IF EXISTS idx_forex_test_telegram_user_id;
DROP INDEX IF EXISTS idx_forex_test_whatsapp_user_id;
DROP INDEX IF EXISTS idx_investments_test_telegram_user_id;
DROP INDEX IF EXISTS idx_investments_test_whatsapp_user_id;
DROP INDEX IF EXISTS idx_transactions_test_telegram_user_id;
DROP INDEX IF EXISTS idx_transactions_test_whatsapp_user_id;
DROP INDEX IF EXISTS idx_transfers_test_telegram_user_id;
DROP INDEX IF EXISTS idx_transfers_test_whatsapp_user_id;

DROP INDEX IF EXISTS idx_forex_telegram_user_id;
DROP INDEX IF EXISTS idx_forex_whatsapp_user_id;
DROP INDEX IF EXISTS idx_investments_telegram_user_id;
DROP INDEX IF EXISTS idx_investments_whatsapp_user_id;
DROP INDEX IF EXISTS idx_transactions_telegram_user_id;
DROP INDEX IF EXISTS idx_transactions_whatsapp_user_id;
DROP INDEX IF EXISTS idx_transfers_telegram_user_id;
DROP INDEX IF EXISTS idx_transfers_whatsapp_user_id;
