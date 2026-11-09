-- RLS de citas (RNF-08): el barbero solo ve las suyas, el dueño ve todas y otra barbería no ve nada.
begin;
select plan(5);

insert into auth.users (id) values
  ('00000000-0000-4000-8000-0000000000a1'),  -- barbero A
  ('00000000-0000-4000-8000-0000000000a2'),  -- barbero B
  ('00000000-0000-4000-8000-0000000000a3'),  -- dueño
  ('00000000-0000-4000-8000-0000000000a4');  -- dueño de otra barbería

insert into barberias (id, nombre, slug, direccion) values
  ('00000000-0000-4000-8000-0000000000b1', 'RLS Uno', 'rls-uno', 'Calle 1'),
  ('00000000-0000-4000-8000-0000000000b2', 'RLS Dos', 'rls-dos', 'Calle 2');

insert into miembros (id, barberia_id, user_id, nombre, rol) values
  ('00000000-0000-4000-8000-0000000000c1', '00000000-0000-4000-8000-0000000000b1', '00000000-0000-4000-8000-0000000000a1', 'Barbero A', 'barbero'),
  ('00000000-0000-4000-8000-0000000000c2', '00000000-0000-4000-8000-0000000000b1', '00000000-0000-4000-8000-0000000000a2', 'Barbero B', 'barbero'),
  ('00000000-0000-4000-8000-0000000000c3', '00000000-0000-4000-8000-0000000000b1', '00000000-0000-4000-8000-0000000000a3', 'Dueño', 'dueno'),
  ('00000000-0000-4000-8000-0000000000c4', '00000000-0000-4000-8000-0000000000b2', '00000000-0000-4000-8000-0000000000a4', 'Otro dueño', 'dueno');

insert into servicios (id, barberia_id, nombre, duracion_min, precio_cop) values
  ('00000000-0000-4000-8000-0000000000d1', '00000000-0000-4000-8000-0000000000b1', 'Corte', 30, 25000);

insert into clientes (id, barberia_id, nombre, telefono_e164) values
  ('00000000-0000-4000-8000-0000000000e1', '00000000-0000-4000-8000-0000000000b1', 'Cliente', '+573001112233');

insert into citas (id, barberia_id, miembro_id, servicio_id, cliente_id, inicio, fin, servicio_nombre, duracion_min, precio_cop, token_hash) values
  ('00000000-0000-4000-8000-0000000000f1', '00000000-0000-4000-8000-0000000000b1', '00000000-0000-4000-8000-0000000000c1', '00000000-0000-4000-8000-0000000000d1', '00000000-0000-4000-8000-0000000000e1', '2030-01-07 15:00+00', '2030-01-07 15:30+00', 'Corte', 30, 25000, 'hash-a'),
  ('00000000-0000-4000-8000-0000000000f2', '00000000-0000-4000-8000-0000000000b1', '00000000-0000-4000-8000-0000000000c2', '00000000-0000-4000-8000-0000000000d1', '00000000-0000-4000-8000-0000000000e1', '2030-01-07 15:00+00', '2030-01-07 15:30+00', 'Corte', 30, 25000, 'hash-b');

set local role authenticated;

set local "request.jwt.claims" to '{"sub": "00000000-0000-4000-8000-0000000000a1"}';
select is((select count(*) from citas)::int, 1, 'el barbero A ve una sola cita');
select is((select id from citas), '00000000-0000-4000-8000-0000000000f1'::uuid, 'y es la suya');

set local "request.jwt.claims" to '{"sub": "00000000-0000-4000-8000-0000000000a2"}';
select is((select id from citas), '00000000-0000-4000-8000-0000000000f2'::uuid, 'el barbero B ve solo la suya');

set local "request.jwt.claims" to '{"sub": "00000000-0000-4000-8000-0000000000a3"}';
select is((select count(*) from citas)::int, 2, 'el dueño ve todas las citas de su barbería');

set local "request.jwt.claims" to '{"sub": "00000000-0000-4000-8000-0000000000a4"}';
select is((select count(*) from citas)::int, 0, 'el dueño de otra barbería no ve ninguna');

select * from finish();
rollback;
