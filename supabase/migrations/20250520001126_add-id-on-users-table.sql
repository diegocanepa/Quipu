-- Add UUID column to users table
ALTER TABLE public.users 
ADD COLUMN id uuid DEFAULT gen_random_uuid() NOT NULL;

-- Add UUID column to users_test table
ALTER TABLE public.users_test 
ADD COLUMN id uuid DEFAULT gen_random_uuid() NOT NULL;

-- Add unique constraints
ALTER TABLE public.users 
ADD CONSTRAINT users_id_key UNIQUE (id);

ALTER TABLE public.users_test 
ADD CONSTRAINT users_test_id_key UNIQUE (id);

-- Add indexes for better query performance
CREATE INDEX idx_users_id ON public.users(id);
CREATE INDEX idx_users_test_id ON public.users_test(id);

COMMENT ON COLUMN public.users.id IS 'Unique identifier for users generated with random UUID';
COMMENT ON COLUMN public.users_test.id IS 'Unique identifier for test users generated with random UUID';
