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
DROP TABLE IF EXISTS public.address CASCADE;
DROP TABLE IF EXISTS public.proposal CASCADE;


DELETE from public.alembic_version;


DELETE FROM public.employee
WHERE id='07b04f2e-00fd-4b50-8acb-839ce7939665'::uuid;