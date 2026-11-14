import { redirect } from "next/navigation";
import { Suspense } from "react";
import { cargarReserva } from "@/domains/agenda/reserva/cargar";
import { Confirmacion } from "@/domains/agenda/reserva/confirmacion";
import { rutaReserva } from "@/domains/agenda/reserva/paso";

// CU-01 · Confirmación
export default function Page(props: PageProps<"/b/[slug]/listo">) {
  return (
    <Suspense>
      <Listo {...props} />
    </Suspense>
  );
}

async function Listo(props: PageProps<"/b/[slug]/listo">) {
  const { barberia, servicio, barbero, inicio, token, hoy } = await cargarReserva(props);
  if (!servicio || !barbero || !inicio || !token || Number.isNaN(Date.parse(inicio))) {
    redirect(rutaReserva(barberia.slug, ""));
  }
  return <Confirmacion barberia={barberia} servicio={servicio} barbero={barbero} inicio={inicio} token={token} hoy={hoy} />;
}
