// Llamadas de la agenda. Las pantallas solo conocen estas funciones y estos tipos.
// shortcut: devuelven datos de demostración (demo.ts) porque la API aún no tiene estos endpoints;
// al llegar F1.01, F1.04, F1.05, F2.01 y F2.02 cada función pasa a usar `api` de lib/api-client.
import * as demo from "./demo";

export type Servicio = { id: string; nombre: string; duracionMin: number; precioCop: number };
export type Barbero = { id: string; nombre: string; proximoTurno: string | null };

export type Barberia = {
  slug: string;
  nombre: string;
  direccion: string;
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
  avisosProximoCorte: boolean;
};

/** Valor de `?barbero=` cuando el cliente elige "El primero disponible". */
export const PRIMERO = "primero";

/** null si la barbería no existe o está suspendida (CU-01 1a). */
export async function obtenerBarberia(slug: string): Promise<Barberia | null> {
  return demo.barberia(slug);
}

/** Turnos libres de un día ("AAAA-MM-DD") para un servicio y un barbero (o PRIMERO). */
export async function obtenerTurnos(slug: string, servicioId: string, barbero: string, dia: string): Promise<Turno[]> {
  return demo.turnos(barbero, dia);
}

/** Devuelve el token del enlace de gestión (/c/{token}); solo se entrega esta vez. */
export async function crearCita(cita: NuevaCita): Promise<{ token: string }> {
  return demo.crearCita(cita);
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
