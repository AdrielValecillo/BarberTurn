import { Suspense } from "react";
import { cargarReserva } from "@/domains/agenda/reserva/cargar";
import { ListaServicios } from "@/domains/agenda/reserva/lista-servicios";

// CU-01 · Paso 1: servicio
export default function Page(props: PageProps<"/b/[slug]">) {
  return (
    <Suspense>
      <Paso1 {...props} />
    </Suspense>
  );
}

async function Paso1(props: PageProps<"/b/[slug]">) {
  const { barberia, servicio } = await cargarReserva(props);
  return <ListaServicios barberia={barberia} inicial={servicio?.id} />;
}
