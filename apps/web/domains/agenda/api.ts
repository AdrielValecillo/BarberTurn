// Llamadas de la agenda. Las pantallas solo conocen estas funciones y estos tipos.
// shortcut: las del panel (equipo, agenda y cita) devuelven datos de demostración (demo.ts)
// hasta que existan F2.01 y F2.02; entonces pasan a usar `api` como las de la reserva.
import { api } from "@/lib/api-client";
import * as demo from "./demo";

export type Servicio = { id: string; nombre: string; duracionMin: number; precioCop: number };
export type Barbero = { id: string; nombre: string; proximoTurno: string | null };

export type Barberia = {
  slug: string;
  nombre: string;
  direccion: string;
  /** E.164; null si la barbería no lo registró. */
  telefono: string | null;
  zona: string;
  servicios: Servicio[];
  barberos: Barbero[];
};

/** `barberoId` es quien atiende: con "el primero disponible" lo asigna la API (RN-05). */
export type Turno = { inicio: string; barberoId: string };

export type EstadoCita = "pendiente" | "confirmada" | "atendida" | "no_asistio" | "cancelada";

export type CitaAgenda = {
  id: string;
  inicio: string;
  cliente: string;
  servicio: string;
  duracionMin: number;
  estado: EstadoCita;
};

export type Hueco = { inicio: string; fin: string };
export type AgendaDia = { citas: CitaAgenda[]; huecos: Hueco[] };

export type CitaDetalle = CitaAgenda & {
  precioCop: number;
  telefono: string | null;
  visitas: number;
  ultimoCorte: string | null;
};

export type NuevaCita = {
  slug: string;
  servicioId: string;
  barberoId: string;
  inicio: string;
  nombre: string;
  telefono: string;
  /** RF-06: sin la casilla marcada no se puede reservar. */
  aceptaPolitica: true;
  avisosProximoCorte: boolean;
};

/**
 * `codigo` dice qué pasó: "turno_ocupado" (CU-01 9a), "maximo_citas" (9b), "demasiadas_solicitudes" (9c),
 * "telefono_invalido", "seleccion_no_disponible"… `mensaje` se puede mostrar tal cual.
 */
export type ErrorReserva = { codigo: string; mensaje: string };

/** Valor de `?barbero=` cuando el cliente elige "El primero disponible". */
export const PRIMERO = "primero";

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/**
 * null si la barbería no existe o está suspendida (CU-01 1a). Con `servicioId`, solo los barberos que lo
 * prestan y su próximo turno para ese servicio (RF-03). Un servicio que no es UUID se ignora (la API daría 422).
 */
export async function obtenerBarberia(slug: string, servicioId?: string): Promise<Barberia | null> {
  const servicio = servicioId && UUID.test(servicioId) ? servicioId : undefined;
  const { data, response } = await api.GET("/public/barberias/{slug}", {
    params: { path: { slug }, query: { servicio } },
  });
  if (response.status === 404) return null;
  if (!data) throw new Error(`GET /public/barberias/${slug} respondió ${response.status}`);
  return {
    slug: data.slug,
    nombre: data.nombre,
    direccion: data.direccion,
    telefono: data.telefono_contacto,
    zona: data.zona,
    servicios: data.servicios.map((s) => ({
      id: s.id,
      nombre: s.nombre,
      duracionMin: s.duracion_min,
      precioCop: s.precio_cop,
    })),
    barberos: data.barberos.map((b) => ({ id: b.id, nombre: b.nombre, proximoTurno: b.proximo_turno })),
  };
}

/** Turnos libres de un día ("AAAA-MM-DD") para un servicio y un barbero (o PRIMERO). */
export async function obtenerTurnos(slug: string, servicioId: string, barbero: string, dia: string): Promise<Turno[]> {
  const { data, response } = await api.GET("/public/barberias/{slug}/turnos", {
    params: {
      path: { slug },
      query: { servicio: servicioId, fecha: dia, miembro: barbero === PRIMERO ? undefined : barbero },
    },
  });
  if (!data) throw new Error(`GET /public/barberias/${slug}/turnos respondió ${response.status}`);
  return data.map((t) => ({ inicio: t.inicio, barberoId: t.miembro_id }));
}

/** El token del enlace de gestión (/c/{token}) solo se entrega esta vez. */
export async function crearCita(cita: NuevaCita): Promise<{ token: string } | ErrorReserva> {
  const { data, error } = await api.POST("/public/citas", {
    body: {
      slug: cita.slug,
      servicio_id: cita.servicioId,
      miembro_id: cita.barberoId,
      inicio: cita.inicio,
      nombre: cita.nombre,
      telefono: cita.telefono,
      acepta_politica: cita.aceptaPolitica,
      acepta_marketing: cita.avisosProximoCorte,
    },
  });
  if (data) return { token: data.token };
  // Los errores de dominio traen {codigo, mensaje}; los 422 de validación, el formato de FastAPI.
  if (error && "codigo" in error) return { codigo: String(error.codigo), mensaje: String(error.mensaje) };
  return { codigo: "error", mensaje: "No pudimos guardar tu reserva. Inténtalo de nuevo." };
}

export async function obtenerEquipo(): Promise<{ id: string; nombre: string }[]> {
  return demo.BARBEROS;
}

export async function obtenerAgenda(dia: string, miembroId: string): Promise<AgendaDia> {
  return demo.agenda(dia, miembroId);
}

export async function obtenerCita(id: string): Promise<CitaDetalle | null> {
  return demo.cita(id);
}
