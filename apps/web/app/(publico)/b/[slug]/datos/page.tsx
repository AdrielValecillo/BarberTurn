import { redirect } from "next/navigation";
import { Suspense } from "react";
import { cargarReserva } from "@/domains/agenda/reserva/cargar";
import { FormularioDatos } from "@/domains/agenda/reserva/formulario-datos";
import { rutaReserva } from "@/domains/agenda/reserva/paso";

// CU-01 · Paso 4: nombre y WhatsApp
export default function Page(props: PageProps<"/b/[slug]/datos">) {
  return (
    <Suspense>
      <Paso4 {...props} />
    </Suspense>
  );
}

async function Paso4(props: PageProps<"/b/[slug]/datos">) {
  const { barberia, servicio, barbero, inicio, hoy, eligioPrimero } = await cargarReserva(props);
  if (!servicio || !barbero || !inicio || Number.isNaN(Date.parse(inicio))) redirect(rutaReserva(barberia.slug, ""));
  return (
    <FormularioDatos
      barberia={barberia}
      servicio={servicio}
      barbero={barbero}
      eligioPrimero={eligioPrimero}
      inicio={inicio}
      hoy={hoy}
    />
  );
}
