// Datos de demostración con el contenido del diseño (front-interface/). Se borra cuando api.ts use la API real.
import { claveDia, sumarDias } from "@/lib/fechas";
import type { AgendaDia, Barberia, CitaAgenda, CitaDetalle, EstadoCita, NuevaCita, Servicio, Turno } from "./api";

const SLUG = "barberia-norte";

const SERVICIOS: Servicio[] = [
  { id: "corte", nombre: "Corte clásico", duracionMin: 30, precioCop: 25000 },
  { id: "corte-barba", nombre: "Corte + barba", duracionMin: 45, precioCop: 35000 },
  { id: "barba", nombre: "Arreglo de barba", duracionMin: 20, precioCop: 15000 },
  { id: "nino", nombre: "Corte para niño", duracionMin: 25, precioCop: 20000 },
  { id: "cejas", nombre: "Cejas", duracionMin: 10, precioCop: 8000 },
];

export const BARBEROS = [
  { id: "carlos", nombre: "Carlos" },
  { id: "andres", nombre: "Andrés" },
  { id: "mateo", nombre: "Mateo" },
  { id: "julian", nombre: "Julián" },
];

// La demo asume Bogotá (UTC-5, sin horario de verano); la API real convierte con la zona de la barbería.
const en = (dia: string, hhmm: string) => new Date(`${dia}T${hhmm}:00-05:00`).toISOString();
const hoy = () => claveDia(new Date());

/** Grilla fija cada 45 min de 9:00 a. m. a 7:30 p. m., con huecos ocupados que no cambian al recargar. */
export function turnos(barbero: string, dia: string, ahora = new Date()): Turno[] {
  const fecha = new Date(`${dia}T12:00:00Z`);
  if (fecha.getUTCDay() === 0) return []; // domingo cerrado
  const candidatos = BARBEROS.filter((b) => barbero === "primero" || b.id === barbero);
  const libres: Turno[] = [];
  for (let k = 0; k < 15; k++) {
    const minutos = 9 * 60 + k * 45;
    const hhmm = `${String(Math.floor(minutos / 60)).padStart(2, "0")}:${String(minutos % 60).padStart(2, "0")}`;
    const inicio = en(dia, hhmm);
    if (new Date(inicio).getTime() < ahora.getTime() + 30 * 60_000) continue;
    const libre = candidatos.find((b) => (k + BARBEROS.indexOf(b) * 2 + fecha.getUTCDate()) % 4 !== 0);
    if (libre) libres.push({ inicio, barberoId: libre.id });
  }
  return libres;
}

export function barberia(slug: string): Barberia | null {
  if (slug !== SLUG) return null;
  const dias = Array.from({ length: 7 }, (_, i) => sumarDias(hoy(), i));
  return {
    slug,
    nombre: "Barbería Norte",
    direccion: "Calle 10 # 5-23",
    zona: "America/Bogota",
    servicios: SERVICIOS,
    barberos: BARBEROS.map((b) => ({
      ...b,
      proximoTurno: dias.flatMap((dia) => turnos(b.id, dia))[0]?.inicio ?? null,
    })),
  };
}

export function crearCita(cita: NuevaCita) {
  void cita;
  return { token: "demo" };
}

// Agenda de Carlos para hoy, como en el diseño.
const CITAS: [hora: string, cliente: string, servicio: string, estado: EstadoCita][] = [
  ["09:00", "Miguel Torres", "corte", "atendida"],
  ["09:45", "Sebastián Ruiz", "corte-barba", "no_asistio"],
  ["11:00", "Felipe Castro", "corte-barba", "atendida"],
  ["14:15", "Laura Gómez", "corte", "confirmada"],
  ["15:00", "Andrea Martínez", "corte-barba", "pendiente"],
  ["17:15", "Juan Pérez", "corte-barba", "confirmada"],
];

function citasDeHoy(): (CitaAgenda & { precioCop: number })[] {
  return CITAS.map(([hora, cliente, servicioId, estado]) => {
    const servicio = SERVICIOS.find((s) => s.id === servicioId)!;
    return {
      id: `demo-${hora.replace(":", "")}`,
      inicio: en(hoy(), hora),
      cliente,
      servicio: servicio.nombre,
      duracionMin: servicio.duracionMin,
      precioCop: servicio.precioCop,
      estado,
    };
  });
}

export function agenda(dia: string, miembroId: string): AgendaDia {
  if (new Date(`${dia}T12:00:00Z`).getUTCDay() === 0) return { citas: [], huecos: [] };
  if (dia !== hoy() || miembroId !== "carlos") {
    return { citas: [], huecos: [{ inicio: en(dia, "09:00"), fin: en(dia, "20:00") }] };
  }
  return {
    citas: citasDeHoy(),
    huecos: [
      { inicio: en(dia, "15:45"), fin: en(dia, "17:15") },
      { inicio: en(dia, "18:00"), fin: en(dia, "20:00") },
    ],
  };
}

export function cita(id: string): CitaDetalle | null {
  const encontrada = citasDeHoy().find((c) => c.id === id);
  if (!encontrada) return null;
  return { ...encontrada, telefono: "+573105550182", visitas: 4, ultimoCorte: en(sumarDias(hoy(), -35), "16:00") };
}
