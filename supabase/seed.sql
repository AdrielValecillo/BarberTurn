-- Datos de desarrollo (se cargan con `make db-reset`): una barbería, dos barberos, servicios y horarios.
-- Los miembros quedan sin user_id: se vinculan al primer inicio de sesión (CU-06).

insert into barberias (id, nombre, slug, direccion, telefono_contacto) values
  ('00000000-0000-4000-8000-00000000b001', 'Barbería Norte', 'barberia-norte', 'Calle 85 #15-20, Bogotá', '+573001112233');

insert into miembros (id, barberia_id, nombre, email, telefono_whatsapp, rol, orden) values
  ('00000000-0000-4000-8000-00000000a001', '00000000-0000-4000-8000-00000000b001', 'Carlos', 'carlos@example.com', '+573001230001', 'dueno', 1),
  ('00000000-0000-4000-8000-00000000a002', '00000000-0000-4000-8000-00000000b001', 'Andrés', 'andres@example.com', '+573001230002', 'barbero', 2);

insert into servicios (id, barberia_id, nombre, duracion_min, precio_cop, orden) values
  ('00000000-0000-4000-8000-00000000c001', '00000000-0000-4000-8000-00000000b001', 'Corte', 30, 25000, 1),
  ('00000000-0000-4000-8000-00000000c002', '00000000-0000-4000-8000-00000000b001', 'Barba', 20, 15000, 2),
  ('00000000-0000-4000-8000-00000000c003', '00000000-0000-4000-8000-00000000b001', 'Corte + barba', 45, 35000, 3);

-- Los dos barberos prestan todos los servicios
insert into miembro_servicios (barberia_id, miembro_id, servicio_id)
select m.barberia_id, m.id, s.id
from miembros m
join servicios s on s.barberia_id = m.barberia_id;

-- Lunes a viernes 9:00-13:00 y 14:00-19:00; sábado 9:00-15:00
insert into horarios (barberia_id, miembro_id, dia_semana, hora_inicio, hora_fin)
select m.barberia_id, m.id, d, f.inicio, f.fin
from miembros m
cross join generate_series(1, 5) as d
cross join (values ('09:00'::time, '13:00'::time), ('14:00'::time, '19:00'::time)) as f(inicio, fin)
union all
select m.barberia_id, m.id, 6, '09:00'::time, '15:00'::time
from miembros m;
