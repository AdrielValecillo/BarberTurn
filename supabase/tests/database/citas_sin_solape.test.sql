-- RNF-05 / RN-02: la base impide dos citas activas que se crucen para el mismo barbero.
begin;
select plan(3);

insert into barberias (id, nombre, slug, direccion) values
  ('00000000-0000-4000-8000-0000000000b1', 'Solape', 'solape', 'Calle 1');
insert into miembros (id, barberia_id, nombre) values
  ('00000000-0000-4000-8000-0000000000c1', '00000000-0000-4000-8000-0000000000b1', 'Barbero');
insert into servicios (id, barberia_id, nombre, duracion_min, precio_cop) values
  ('00000000-0000-4000-8000-0000000000d1', '00000000-0000-4000-8000-0000000000b1', 'Corte', 30, 25000);
insert into clientes (id, barberia_id, nombre, telefono_e164) values
  ('00000000-0000-4000-8000-0000000000e1', '00000000-0000-4000-8000-0000000000b1', 'Cliente', '+573001112233');

create function pg_temp.cita(p_inicio timestamptz, p_token text, p_estado estado_cita default 'pendiente') returns void
language sql as $$
  insert into citas (barberia_id, miembro_id, servicio_id, cliente_id, inicio, fin, servicio_nombre, duracion_min, precio_cop, token_hash, estado, cancelada_at)
  values ('00000000-0000-4000-8000-0000000000b1', '00000000-0000-4000-8000-0000000000c1', '00000000-0000-4000-8000-0000000000d1',
          '00000000-0000-4000-8000-0000000000e1', p_inicio, p_inicio + interval '30 minutes', 'Corte', 30, 25000, p_token, p_estado,
          case when p_estado = 'cancelada' then now() end)
$$;

select pg_temp.cita('2030-01-07 15:00+00', 'base');

select throws_ok(
  $$select pg_temp.cita('2030-01-07 15:15+00', 'cruzada')$$,
  '23P01',
  null,
  'una cita que se cruza con otra activa del mismo barbero se rechaza'
);

select lives_ok(
  $$select pg_temp.cita('2030-01-07 15:30+00', 'contigua')$$,
  'una cita que empieza justo cuando termina la otra es válida'
);

select lives_ok(
  $$select pg_temp.cita('2030-01-07 15:00+00', 'cancelada', 'cancelada')$$,
  'una cita cancelada no bloquea el turno'
);

select * from finish();
rollback;
