import { redirect } from "next/navigation";
import { Suspense } from "react";
import { PRIMERO } from "@/domains/agenda/api";
import { cargarReserva } from "@/domains/agenda/reserva/cargar";
import { rutaReserva } from "@/domains/agenda/reserva/paso";
import { SelectorBarbero } from "@/domains/agenda/reserva/selector-barbero";

// CU-01 · Paso 2: barbero
export default function Page(props: PageProps<"/b/[slug]/barbero">) {
  return (
    <Suspense>
      <Paso2 {...props} />
    </Suspense>
  );
}

async function Paso2(props: PageProps<"/b/[slug]/barbero">) {
  const { barberia, servicio, barbero, primero, hoy } = await cargarReserva(props);
  if (!servicio) redirect(rutaReserva(barberia.slug, ""));
  return (
    <SelectorBarbero
      barberia={barberia}
      servicio={servicio}
      inicial={primero ? PRIMERO : barbero?.id}
      hoy={hoy}
    />
  );
}
