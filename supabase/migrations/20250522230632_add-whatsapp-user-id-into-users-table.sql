ALTER TABLE public.users_test
ADD COLUMN IF NOT EXISTS whatsapp_user_id TEXT;

COMMENT ON COLUMN public.users_test.whatsapp_user_id IS 'User ID from WhatsApp messenger';
CREATE INDEX IF NOT EXISTS idx_users_test_whatsapp_user_id ON public.users_test(whatsapp_user_id);

ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS whatsapp_user_id TEXT;

COMMENT ON COLUMN public.users.whatsapp_user_id IS 'User ID from WhatsApp messenger';
CREATE INDEX IF NOT EXISTS idx_users_whatsapp_user_id ON public.users(whatsapp_user_id);