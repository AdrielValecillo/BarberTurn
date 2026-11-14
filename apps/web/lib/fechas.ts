// Formato es-CO en la zona de la barbería (RNF-12, RNF-13).
// Un día sin hora viaja como clave "AAAA-MM-DD" y se formatea con `deClave` y la zona "UTC".

export const ZONA = "America/Bogota";

type Fecha = Date | string;

function partes(fecha: Fecha, zona: string, opciones: Intl.DateTimeFormatOptions) {
  const lista = new Intl.DateTimeFormat("es-CO", { timeZone: zona, ...opciones }).formatToParts(new Date(fecha));
  // Intl separa con espacios duros ("5:15 p. m."): se normalizan para comparar y pintar igual en todas partes.
  return Object.fromEntries(lista.map((p) => [p.type, p.value.replace(/[\u00a0\u202f]/g, " ")]));
}

const mayuscula = (texto: string) => texto.charAt(0).toUpperCase() + texto.slice(1);

// Espacio duro: una hora nunca se parte en dos renglones ("5:15 p." / "m.").
const DURO = "\u00a0";

/** "5:15" y "p. m." por separado: el diseño los pinta con tamaños distintos. */
export function partesHora(fecha: Fecha, zona = ZONA) {
  const p = partes(fecha, zona, { hour: "numeric", minute: "2-digit", hour12: true });
  return { reloj: `${p.hour}:${p.minute}`, periodo: p.dayPeriod.replace(" ", DURO) };
}

/** "5:15 p. m.", con espacios duros. */
export function hora(fecha: Fecha, zona = ZONA) {
  const { reloj, periodo } = partesHora(fecha, zona);
  return reloj + DURO + periodo;
}

/** "3:45 a 5:15 p. m." o "11:00 a. m. a 1:00 p. m." */
export function rangoHoras(inicio: Fecha, fin: Fecha, zona = ZONA) {
  const a = partesHora(inicio, zona);
  return `${a.periodo === partesHora(fin, zona).periodo ? a.reloj : hora(inicio, zona)} a ${hora(fin, zona)}`;
}

/** "sábado 7 de noviembre" */
export function fechaLarga(fecha: Fecha, zona = ZONA) {
  const p = partes(fecha, zona, { weekday: "long", day: "numeric", month: "long" });
  return `${p.weekday} ${p.day} de ${p.month}`;
}

/** "3 de octubre" */
export function diaYMes(fecha: Fecha, zona = ZONA) {
  const p = partes(fecha, zona, { day: "numeric", month: "long" });
  return `${p.day} de ${p.month}`;
}

/** "sáb" */
export function diaSemanaCorto(fecha: Fecha, zona = ZONA) {
  return partes(fecha, zona, { weekday: "short" }).weekday.replace(".", "");
}

/** Día calendario en la zona: "2026-11-07". */
export function claveDia(fecha: Fecha, zona = ZONA) {
  const p = partes(fecha, zona, { year: "numeric", month: "2-digit", day: "2-digit" });
  return `${p.year}-${p.month}-${p.day}`;
}

export const esClaveDia = (texto: string | undefined): texto is string =>
  !!texto && /^\d{4}-\d{2}-\d{2}$/.test(texto) && !Number.isNaN(Date.parse(texto));

/** Mediodía UTC de una clave: se formatea con la zona "UTC" y no cambia de día. */
export const deClave = (clave: string) => new Date(`${clave}T12:00:00Z`);

export function sumarDias(clave: string, dias: number) {
  const fecha = deClave(clave);
  fecha.setUTCDate(fecha.getUTCDate() + dias);
  return fecha.toISOString().slice(0, 10);
}

/** Hora local 0–23, para agrupar los turnos en mañana, tarde y noche. */
export function franja(fecha: Fecha, zona = ZONA) {
  const h = Number(partes(fecha, zona, { hour: "numeric", hourCycle: "h23" }).hour);
  return h < 12 ? "Mañana" : h < 18 ? "Tarde" : "Noche";
}

/** "Hoy, sábado 7 de noviembre" o "Lunes 9 de noviembre". `hoy` es la clave del día actual. */
export function fechaConHoy(fecha: Fecha, hoy: string, zona = ZONA) {
  const larga = fechaLarga(fecha, zona);
  return claveDia(fecha, zona) === hoy ? `Hoy, ${larga}` : mayuscula(larga);
}

/** "hoy 3:45 p. m." o "lun 9:00 a. m." */
export function cuandoCorto(fecha: Fecha, hoy: string, zona = ZONA) {
  const dia = claveDia(fecha, zona) === hoy ? "hoy" : diaSemanaCorto(fecha, zona);
  return `${dia} ${hora(fecha, zona)}`;
}

/** "Hoy, 1:00 p. m." o "Miércoles 4 de nov., 8:12 p. m." */
export function fechaHoraCorta(fecha: Fecha, hoy: string, zona = ZONA) {
  if (claveDia(fecha, zona) === hoy) return `Hoy, ${hora(fecha, zona)}`;
  const p = partes(fecha, zona, { weekday: "long", day: "numeric", month: "short" });
  return `${mayuscula(p.weekday)} ${p.day} de ${p.month.replace(".", "")}., ${hora(fecha, zona)}`;
}

/** "$35.000" */
export function precio(cop: number) {
  return `$${new Intl.NumberFormat("es-CO", { maximumFractionDigits: 0 }).format(cop)}`;
}
