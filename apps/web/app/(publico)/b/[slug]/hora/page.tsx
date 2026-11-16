import { redirect } from "next/navigation";
import { Suspense } from "react";
import { obtenerTurnos, PRIMERO } from "@/domains/agenda/api";
import { cargarReserva } from "@/domains/agenda/reserva/cargar";
import { GrillaTurnos } from "@/domains/agenda/reserva/grilla-turnos";
import { rutaReserva } from "@/domains/agenda/reserva/paso";
import { esClaveDia } from "@/lib/fechas";

// CU-01 · Paso 3: día y hora
export default function Page(props: PageProps<"/b/[slug]/hora">) {
  return (
    <Suspense>
      <Paso3 {...props} />
    </Suspense>
  );
}

async function Paso3(props: PageProps<"/b/[slug]/hora">) {
  const { barberia, servicio, barbero, primero, fecha, hoy, ocupado } = await cargarReserva(props);
  if (!servicio) redirect(rutaReserva(barberia.slug, ""));
  if (!barbero && !primero) redirect(rutaReserva(barberia.slug, "barbero", { servicio: servicio.id }));

  const dia = esClaveDia(fecha) && fecha >= hoy ? fecha : hoy;
  const turnos = await obtenerTurnos(barberia.slug, servicio.id, barbero?.id ?? PRIMERO, dia);
  // La clave reinicia la hora elegida al cambiar de día.
  return (
    <GrillaTurnos
      key={dia}
      barberia={barberia}
      servicio={servicio}
      barbero={barbero}
      dia={dia}
      hoy={hoy}
      turnos={turnos}
      ocupado={ocupado}
    />
  );
}
