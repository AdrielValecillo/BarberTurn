import { notFound } from "next/navigation";
import { Suspense } from "react";
import { obtenerCita } from "@/domains/agenda/api";
import { DetalleCita } from "@/domains/agenda/panel/detalle-cita";
import { obtenerAvisos } from "@/domains/notificaciones/api";
import { HistorialAvisos } from "@/domains/notificaciones/historial-avisos";
import { claveDia } from "@/lib/fechas";

// CU-08 · Detalle de la cita
export default function Page(props: PageProps<"/panel/citas/[id]">) {
  return (
    <Suspense>
      <Detalle {...props} />
    </Suspense>
  );
}

async function Detalle({ params }: PageProps<"/panel/citas/[id]">) {
  const { id } = await params;
  const [cita, avisos] = await Promise.all([obtenerCita(id), obtenerAvisos(id)]);
  if (!cita) notFound();
  const hoy = claveDia(new Date());
  return <DetalleCita cita={cita} hoy={hoy} avisos={<HistorialAvisos avisos={avisos} hoy={hoy} />} />;
}
