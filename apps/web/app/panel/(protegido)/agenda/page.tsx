import { Suspense } from "react";
import { obtenerAgenda, obtenerEquipo } from "@/domains/agenda/api";
import { AgendaDelDia } from "@/domains/agenda/panel/agenda-del-dia";
import { claveDia, esClaveDia } from "@/lib/fechas";

// CU-07 · Agenda del día
// shortcut: sin sesión todavía; el layout que la verifica llega con F0.10 y hoy solo hay datos de demostración.
export default function Page(props: PageProps<"/panel/agenda">) {
  return (
    <Suspense>
      <Agenda {...props} />
    </Suspense>
  );
}

async function Agenda({ searchParams }: PageProps<"/panel/agenda">) {
  const { fecha, miembro } = await searchParams;
  const ahora = new Date();
  const hoy = claveDia(ahora);
  const dia = typeof fecha === "string" && esClaveDia(fecha) ? fecha : hoy;
  const equipo = await obtenerEquipo();
  const actual = equipo.find((m) => m.id === miembro) ?? equipo[0];
  const agenda = await obtenerAgenda(dia, actual.id);
  return (
    <AgendaDelDia agenda={agenda} dia={dia} hoy={hoy} ahora={ahora.toISOString()} equipo={equipo} miembro={actual.id} />
  );
}
