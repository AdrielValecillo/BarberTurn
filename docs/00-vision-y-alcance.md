# 00 · Visión y alcance

| | |
|---|---|
| **Producto** | Turnero (nombre provisional) |
| **Versión del documento** | 0.1 (borrador) |
| **Fecha** | 7 de noviembre de 2026 |
| **Autor** | Adriel |
| **Documentos relacionados** | [01 · Requerimientos](01-requerimientos.md), [04 · Modelo de datos](04-modelo-de-datos.md) |

---

## 1. Problema

Las barberías pequeñas y medianas en Colombia agendan casi todo por mensajes de WhatsApp y llamadas que el barbero responde a mano, muchas veces mientras está atendiendo. Esto genera tres problemas:

1. **Tiempo perdido:** el barbero interrumpe su trabajo para responder "¿tienes turno a las 5?" y negociar horarios por chat.
2. **Inasistencias:** el cliente olvida la cita o no avisa que no va. El turno queda vacío y se pierde el ingreso.
3. **Falta de visibilidad:** el cliente no sabe qué horarios hay libres y el barbero no tiene una agenda clara del día; muchas veces está en un cuaderno o en su memoria.

## 2. Propuesta de valor

- **Para el cliente:** reservar en menos de un minuto desde un enlace, sin descargar nada ni crear cuenta, y recibir por WhatsApp la confirmación y los recordatorios, con botones para confirmar, reagendar o cancelar en un toque.
- **Para el barbero:** ver su agenda del día en el celular, en tiempo real, con el estado de cada cita, y recibir avisos cuando alguien reserva, cancela o no confirma.
- **Para el dueño de la barbería:** menos inasistencias, menos tiempo respondiendo mensajes y una vista de la agenda de todo su equipo.

## 3. Usuarios y actores

| Actor | Descripción | Cómo accede |
|---|---|---|
| **Cliente** | Persona que reserva un servicio. | Enlace público de la barbería. Sin cuenta: se identifica con su número de WhatsApp. |
| **Barbero** | Miembro del equipo que atiende citas. | Panel web (PWA) con inicio de sesión. Ve solo su agenda. |
| **Dueño** | Administra la barbería. Puede ser también barbero. | Panel web con permisos de administración. Ve la agenda de todos. |
| **Administrador de la plataforma** | Quien opera el SaaS (alta de barberías, soporte). | Acceso interno. |
| **Sistema** | Procesos automáticos: envío de notificaciones (cron) y recepción de eventos de WhatsApp (webhook). | — |

## 4. Objetivos del MVP y métricas de éxito

Las metas numéricas son propuestas iniciales y se ajustan con los datos del piloto.

| Objetivo | Métrica | Meta propuesta |
|---|---|---|
| Reservar es rápido | Tiempo desde abrir el enlace hasta confirmar | Mediana < 60 s |
| Los recordatorios llegan | Recordatorios entregados a tiempo | ≥ 95 % |
| Bajan las inasistencias | Citas marcadas como "No vino" | Medir línea base en las 2 primeras semanas del piloto y reducirla |
| Los barberos lo adoptan | Barberías activas en el piloto | 2–3 barberías usándolo al menos 4 semanas seguidas |
| La operación es barata | Costo mensual de infraestructura y mensajes | Dentro del presupuesto definido (ver decisiones pendientes) |

## 5. Alcance del MVP

### Incluido

**Reserva pública (cliente)**
- Página pública por barbería con su propia URL.
- Flujo de 4 pasos: servicio → barbero (o "el primero disponible") → día y hora → nombre y WhatsApp.
- Atajo "Repetir mi último corte" en el mismo dispositivo.
- Pantalla de confirmación con "Agregar a mi calendario" (archivo .ics) y "Cómo llegar".

**Gestión de la cita por el cliente**
- Enlace privado por cita para ver, reagendar o cancelar, sin iniciar sesión.

**Notificaciones por WhatsApp (API oficial de Meta, número central)**
- Al cliente: confirmación, recordatorio del día anterior y recordatorio de 2 horas antes, con botones de respuesta rápida.
- Al barbero: nueva reserva, cancelación, cliente sin confirmar y resumen diario.

**Panel del barbero (PWA)**
- Agenda del día con estados, huecos libres y hora actual.
- Detalle de la cita: datos e historial del cliente, historial de avisos, botones para escribirle o llamarlo.
- Acciones: marcar atendida, "No vino", reagendar, cancelar, crear cita manual y bloquear horarios.

**Administración de la barbería (dueño)**
- Datos de la barbería, servicios, barberos, horarios semanales y reglas de reserva.
- Agenda de todos los barberos.

**Plataforma**
- Varias barberías en la misma instalación, con los datos de cada una aislados.
- Alta manual de barberías durante el piloto.

### Fuera del alcance del MVP

| Funcionalidad | Motivo | Cuándo |
|---|---|---|
| Sincronización con Google Calendar por API | Requiere OAuth y verificación de Google; el .ics cubre al cliente. | Fase 2, si los barberos lo piden |
| Pagos y anticipos | Complejidad legal y de integración. | Fase 2 (útil para clientes que fallan seguido) |
| Mensajes de "ya te toca el próximo corte" | Son mensajes de marketing: más caros y requieren consentimiento. **El consentimiento sí se registra desde el MVP.** | Fase 2 |
| Número de WhatsApp propio por barbería | Requiere ser Tech Provider de Meta (Embedded Signup). | Plan premium futuro |
| Marketplace, directorio o reseñas públicas | No es el foco: es una herramienta de gestión, no un marketplace. | Sin fecha |
| App nativa (App Store / Play Store) | La PWA cubre la necesidad. | Sin fecha |
| Varias sedes por barbería, inventario, comisiones, reportes avanzados | Fuera del problema principal. | Sin fecha |
| SMS o correo como canal de recordatorio | WhatsApp es el canal que usan los clientes. | Sin fecha |

## 6. Supuestos y restricciones

- **Mercado:** Colombia. Zona horaria `America/Bogota`, moneda COP sin decimales, idioma español.
- **Canal:** los clientes usan WhatsApp como canal principal.
- **WhatsApp:** un solo número central de la plataforma, con la API oficial (WhatsApp Cloud API). Sin verificar el negocio, el límite es de 250 clientes distintos cada 24 horas, suficiente para el piloto.
- **Equipo:** un solo desarrollador.
- **Presupuesto:** bajo; se prioriza lo gratuito o barato mientras no haya clientes que paguen.
- **Legal:** cumplimiento de la Ley 1581 de 2012 (habeas data): política de tratamiento de datos y autorización registrada.

## 7. Decisiones tomadas

Cada una se documentará como ADR en `docs/adr/`.

| # | Decisión | Razón principal |
|---|---|---|
| D-01 | WhatsApp con la API oficial de Meta y un número central de la plataforma. | Sin riesgo de bloqueo, costo bajo en Colombia, una sola integración para todas las barberías. |
| D-02 | Reserva sin cuenta: el cliente se identifica con su número y gestiona la cita con un enlace privado. | Menos fricción para el cliente. |
| D-03 | La base de datos es la fuente de verdad de la agenda. Sin API de Google Calendar en el MVP; al cliente se le ofrece un .ics. | Evita OAuth, tokens y verificación de Google. |
| D-04 | Panel del barbero como PWA (web instalable). | Sin tiendas de apps, un solo código. |
| D-05 | PostgreSQL (propuesto: Supabase) con aislamiento por barbería mediante RLS. | Restricciones fuertes en la base (anti-doble reserva), auth y tiempo real incluidos. |
| D-06 | El envío de notificaciones pasa por una interfaz propia (`NotificationService`). | Permite desarrollar sin WhatsApp y cambiar de proveedor sin reescribir. |

## 8. Decisiones pendientes

| # | Pregunta | Fecha límite sugerida |
|---|---|---|
| P-01 | Nombre comercial definitivo y dominio. | Antes de registrar el número en Meta (el nombre visible debe coincidir con la web). |
| P-02 | Framework y lenguaje del backend y frontend. | Antes de la fase 1. |
| P-03 | Hosting de producción (plan pago o VPS). | Antes del piloto. |
| P-04 | Modelo de precios para las barberías. | Antes del piloto. |
| P-05 | Valores por defecto de las reglas de reserva (anticipación, límite de cancelación). | Validar con las barberías del piloto. |
| P-06 | Presupuesto mensual máximo de operación. | Antes del piloto. |

## 9. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Meta demora la aprobación de plantillas o la verificación del negocio. | Retrasa los recordatorios. | Iniciar el trámite desde el primer día; desarrollar con la interfaz D-06 y el número de prueba. |
| Una plantilla se reclasifica como marketing. | Cada mensaje cuesta más. | Redactar las plantillas como avisos de servicio puros, sin lenguaje promocional. |
| Las capas gratuitas pausan el proyecto o el cron. | Recordatorios que no salen. | Pasar a plan pago antes del piloto; monitorear el cron. |
| Reservas falsas o abuso del formulario público. | Agenda llena de citas basura. | Límite de citas futuras por teléfono y de reservas por IP; botón de confirmación. |
| Los barberos no adoptan el panel. | El producto no se usa. | Piloto acompañado; avisos por WhatsApp para que no dependan de abrir el panel. |
| Dependencia de Meta (precios o políticas). | Costos o restricciones nuevas. | Interfaz D-06; enlaces wa.me como respaldo manual. |

## 10. Fases (resumen)

El detalle va en `06-plan-de-implementacion.md`.

| Fase | Contenido | Criterio de terminado |
|---|---|---|
| F0 · Base | Repo, entornos, esquema de base de datos, autenticación del personal, trámite con Meta iniciado. | Migración aplicada; un dueño puede iniciar sesión. |
| F1 · Reservas | Página pública, cálculo de disponibilidad, creación de citas, enlace de gestión. | Un cliente reserva, reagenda y cancela sin errores; no hay doble reserva posible. |
| F2 · Panel | Agenda, detalle de cita, acciones, citas manuales, bloqueos, configuración. | Un barbero maneja un día completo solo desde el panel. |
| F3 · WhatsApp | Plantillas, envío programado, webhook, avisos al barbero. | Ciclo completo de recordatorios con el número real. |
| F4 · Piloto | 2–3 barberías en vivo, monitoreo y ajustes. | 4 semanas de uso continuo. |

## 11. Glosario

| Término | Definición |
|---|---|
| **Barbería** | Negocio que usa la plataforma. Es la unidad de aislamiento de datos (tenant). |
| **Miembro** | Persona del equipo de una barbería con acceso al panel. Su rol es dueño o barbero. |
| **Barbero** | Miembro que atiende citas y aparece como opción al reservar. |
| **Servicio** | Lo que se reserva (por ejemplo, "Corte + barba"), con duración y precio. |
| **Cita** | Reserva de un servicio con un barbero, para un cliente, en un rango de tiempo. |
| **Turno** | Hora de inicio disponible que se le ofrece al cliente. |
| **Horario** | Franjas semanales en las que trabaja un barbero (por ejemplo, lunes de 9:00 a 13:00 y de 14:00 a 19:00). |
| **Bloqueo** | Rango de tiempo en que un barbero o la barbería entera no recibe citas (almuerzo, permiso, festivo). |
| **Enlace de gestión** | URL privada de una cita que le permite al cliente verla, reagendarla o cancelarla. |
| **Notificación** | Mensaje de WhatsApp programado o enviado por el sistema. |
| **Plantilla** | Mensaje aprobado por Meta con variables, obligatorio para escribirle primero a alguien. |
| **Ventana de 24 horas** | Periodo que abre un mensaje del cliente, durante el cual se pueden enviar mensajes de texto libre. |
| **No vino** | Estado de una cita a la que el cliente no asistió sin cancelar (inasistencia). |

## 12. Referencias

- Mockups del flujo de reserva, recordatorios y panel del barbero: https://claude.ai/artifact/YMxQdTSmNtRJAkVokRUZ1A
- WhatsApp Cloud API: https://developers.facebook.com/docs/whatsapp/cloud-api/get-started/
- Ley 1581 de 2012 (protección de datos personales, Colombia).
