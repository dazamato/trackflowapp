-- Active: 1727617613805@@127.0.0.1@5432@app
DROP TABLE IF EXISTS public.user CASCADE;
DROP TABLE IF EXISTS public.employee CASCADE;
DROP TABLE IF EXISTS public.business CASCADE;
DROP TABLE IF EXISTS public.businessindustry CASCADE;
DROP TABLE IF EXISTS public.businessstage CASCADE;
DROP TABLE IF EXISTS public.product CASCADE;
DROP TABLE IF EXISTS public.productgroup CASCADE;
DROP TABLE IF EXISTS public.producttag CASCADE;
DROP TABLE IF EXISTS public.producttaglink CASCADE;
DROP TABLE IF EXISTS public.sale CASCADE;
DROP TABLE IF EXISTS public.item CASCADE;
DROP TABLE IF EXISTS public.stage CASCADE;
DROP TABLE IF EXISTS public.lead CASCADE;

DELETE from public.alembic_version;