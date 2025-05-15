-- Add user ID columns to forex_test table
ALTER TABLE public.forex_test
ADD COLUMN IF NOT EXISTS webapp_user_id UUID,
ADD COLUMN IF NOT EXISTS telegram_user_id BIGINT,
ADD COLUMN IF NOT EXISTS whatsapp_user_id TEXT;

-- Add column comments to forex_test
COMMENT ON COLUMN public.forex_test.webapp_user_id IS 'User ID from the web application';
COMMENT ON COLUMN public.forex_test.telegram_user_id IS 'User ID from Telegram messenger';
COMMENT ON COLUMN public.forex_test.whatsapp_user_id IS 'User ID from WhatsApp messenger';

-- Add indexes to forex_test table
CREATE INDEX IF NOT EXISTS idx_forex_test_webapp_user_id ON public.forex_test(webapp_user_id);
CREATE INDEX IF NOT EXISTS idx_forex_test_telegram_user_id ON public.forex_test(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_forex_test_whatsapp_user_id ON public.forex_test(whatsapp_user_id);

-- Add user ID columns to investments_test table
ALTER TABLE public.investments_test
ADD COLUMN IF NOT EXISTS webapp_user_id UUID,
ADD COLUMN IF NOT EXISTS telegram_user_id BIGINT,
ADD COLUMN IF NOT EXISTS whatsapp_user_id TEXT;

-- Add column comments to investments_test
COMMENT ON COLUMN public.investments_test.webapp_user_id IS 'User ID from the web application';
COMMENT ON COLUMN public.investments_test.telegram_user_id IS 'User ID from Telegram messenger';
COMMENT ON COLUMN public.investments_test.whatsapp_user_id IS 'User ID from WhatsApp messenger';

-- Add indexes to investments_test table
CREATE INDEX IF NOT EXISTS idx_investments_test_webapp_user_id ON public.investments_test(webapp_user_id);
CREATE INDEX IF NOT EXISTS idx_investments_test_telegram_user_id ON public.investments_test(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_investments_test_whatsapp_user_id ON public.investments_test(whatsapp_user_id);

-- Add user ID columns to transactions_test table
ALTER TABLE public.transactions_test
ADD COLUMN IF NOT EXISTS webapp_user_id UUID,
ADD COLUMN IF NOT EXISTS telegram_user_id BIGINT,
ADD COLUMN IF NOT EXISTS whatsapp_user_id TEXT;

-- Add column comments to transactions_test
COMMENT ON COLUMN public.transactions_test.webapp_user_id IS 'User ID from the web application';
COMMENT ON COLUMN public.transactions_test.telegram_user_id IS 'User ID from Telegram messenger';
COMMENT ON COLUMN public.transactions_test.whatsapp_user_id IS 'User ID from WhatsApp messenger';

-- Add indexes to transactions_test table
CREATE INDEX IF NOT EXISTS idx_transactions_test_webapp_user_id ON public.transactions_test(webapp_user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_test_telegram_user_id ON public.transactions_test(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_test_whatsapp_user_id ON public.transactions_test(whatsapp_user_id);

-- Add user ID columns to transfers_test table
ALTER TABLE public.transfers_test
ADD COLUMN IF NOT EXISTS webapp_user_id UUID,
ADD COLUMN IF NOT EXISTS telegram_user_id BIGINT,
ADD COLUMN IF NOT EXISTS whatsapp_user_id TEXT;

-- Add column comments to transfers_test
COMMENT ON COLUMN public.transfers_test.webapp_user_id IS 'User ID from the web application';
COMMENT ON COLUMN public.transfers_test.telegram_user_id IS 'User ID from Telegram messenger';
COMMENT ON COLUMN public.transfers_test.whatsapp_user_id IS 'User ID from WhatsApp messenger';

-- Add indexes to transfers_test table
CREATE INDEX IF NOT EXISTS idx_transfers_test_webapp_user_id ON public.transfers_test(webapp_user_id);
CREATE INDEX IF NOT EXISTS idx_transfers_test_telegram_user_id ON public.transfers_test(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_transfers_test_whatsapp_user_id ON public.transfers_test(whatsapp_user_id);

-- Add user ID columns to forex table (production)
ALTER TABLE public.forex
ADD COLUMN IF NOT EXISTS webapp_user_id UUID,
ADD COLUMN IF NOT EXISTS telegram_user_id BIGINT,
ADD COLUMN IF NOT EXISTS whatsapp_user_id TEXT;

-- Add column comments to forex
COMMENT ON COLUMN public.forex.webapp_user_id IS 'User ID from the web application';
COMMENT ON COLUMN public.forex.telegram_user_id IS 'User ID from Telegram messenger';
COMMENT ON COLUMN public.forex.whatsapp_user_id IS 'User ID from WhatsApp messenger';

-- Add indexes to forex table (production)
CREATE INDEX IF NOT EXISTS idx_forex_webapp_user_id ON public.forex(webapp_user_id);
CREATE INDEX IF NOT EXISTS idx_forex_telegram_user_id ON public.forex(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_forex_whatsapp_user_id ON public.forex(whatsapp_user_id);

-- Add user ID columns to investments table (production)
ALTER TABLE public.investments
ADD COLUMN IF NOT EXISTS webapp_user_id UUID,
ADD COLUMN IF NOT EXISTS telegram_user_id BIGINT,
ADD COLUMN IF NOT EXISTS whatsapp_user_id TEXT;

-- Add column comments to investments
COMMENT ON COLUMN public.investments.webapp_user_id IS 'User ID from the web application';
COMMENT ON COLUMN public.investments.telegram_user_id IS 'User ID from Telegram messenger';
COMMENT ON COLUMN public.investments.whatsapp_user_id IS 'User ID from WhatsApp messenger';

-- Add indexes to investments table (production)
CREATE INDEX IF NOT EXISTS idx_investments_webapp_user_id ON public.investments(webapp_user_id);
CREATE INDEX IF NOT EXISTS idx_investments_telegram_user_id ON public.investments(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_investments_whatsapp_user_id ON public.investments(whatsapp_user_id);

-- Add user ID columns to transactions table (production)
ALTER TABLE public.transactions
ADD COLUMN IF NOT EXISTS webapp_user_id UUID,
ADD COLUMN IF NOT EXISTS telegram_user_id BIGINT,
ADD COLUMN IF NOT EXISTS whatsapp_user_id TEXT;

-- Add column comments to transactions
COMMENT ON COLUMN public.transactions.webapp_user_id IS 'User ID from the web application';
COMMENT ON COLUMN public.transactions.telegram_user_id IS 'User ID from Telegram messenger';
COMMENT ON COLUMN public.transactions.whatsapp_user_id IS 'User ID from WhatsApp messenger';

-- Add indexes to transactions table (production)
CREATE INDEX IF NOT EXISTS idx_transactions_webapp_user_id ON public.transactions(webapp_user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_telegram_user_id ON public.transactions(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_whatsapp_user_id ON public.transactions(whatsapp_user_id);

-- Add user ID columns to transfers table (production)
ALTER TABLE public.transfers
ADD COLUMN IF NOT EXISTS webapp_user_id UUID,
ADD COLUMN IF NOT EXISTS telegram_user_id BIGINT,
ADD COLUMN IF NOT EXISTS whatsapp_user_id TEXT;

-- Add column comments to transfers
COMMENT ON COLUMN public.transfers.webapp_user_id IS 'User ID from the web application';
COMMENT ON COLUMN public.transfers.telegram_user_id IS 'User ID from Telegram messenger';
COMMENT ON COLUMN public.transfers.whatsapp_user_id IS 'User ID from WhatsApp messenger';

-- Add indexes to transfers table (production)
CREATE INDEX IF NOT EXISTS idx_transfers_webapp_user_id ON public.transfers(webapp_user_id);
CREATE INDEX IF NOT EXISTS idx_transfers_telegram_user_id ON public.transfers(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_transfers_whatsapp_user_id ON public.transfers(whatsapp_user_id);