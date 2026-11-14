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
  const barberia = await obtenerBarberia(slug);
  if (!barberia) notFound();
  const idBarbero = uno(q.barbero);
  return {
    barberia,
    servicio: barberia.servicios.find((s) => s.id === uno(q.servicio)),
    barbero: barberia.barberos.find((b) => b.id === idBarbero),
    primero: idBarbero === PRIMERO,
    fecha: uno(q.fecha),
    inicio: uno(q.inicio),
    token: uno(q.token),
    hoy: claveDia(new Date(), barberia.zona),
  };
}
