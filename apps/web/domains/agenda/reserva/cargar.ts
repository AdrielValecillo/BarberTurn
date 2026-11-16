import { notFound } from "next/navigation";
import { claveDia } from "@/lib/fechas";
import { obtenerBarberia, PRIMERO } from "../api";

type Entrada = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

const uno = (valor: string | string[] | undefined) => (Array.isArray(valor) ? valor[0] : valor);

/** Lee la barbería del slug y lo ya elegido en la URL. Si la barbería no existe muestra "no disponible" (CU-01 1a). */
export async function cargarReserva({ params, searchParams }: Entrada) {
  const [{ slug }, q] = await Promise.all([params, searchParams]);
  const idServicio = uno(q.servicio);
  // Con el servicio, la API solo devuelve a los barberos que lo prestan (RF-03).
  const barberia = await obtenerBarberia(slug, idServicio);
  if (!barberia) notFound();
  const idBarbero = uno(q.barbero);
  return {
    barberia,
    servicio: barberia.servicios.find((s) => s.id === idServicio),
    barbero: barberia.barberos.find((b) => b.id === idBarbero),
    primero: idBarbero === PRIMERO,
    /** En el paso 4 `barbero` es el asignado; esto dice si el cliente había elegido "el primero disponible". */
    eligioPrimero: idBarbero === PRIMERO || uno(q.eleccion) === PRIMERO,
    fecha: uno(q.fecha),
    inicio: uno(q.inicio),
    token: uno(q.token),
    /** CU-01 9a: se vuelve a la hora porque el turno elegido se acaba de ocupar. */
    ocupado: uno(q.ocupado) === "1",
    hoy: claveDia(new Date(), barberia.zona),
  };
}
