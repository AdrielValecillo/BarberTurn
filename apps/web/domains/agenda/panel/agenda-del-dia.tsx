import Link from "next/link";
import { Fragment } from "react";
import { Icono } from "@/components/ui/icono";
import { NavPanel } from "@/components/ui/nav-panel";
import { Chip, Pantalla } from "@/components/ui/piezas";
import { deClave, fechaConHoy, hora, partesHora, rangoHoras, sumarDias } from "@/lib/fechas";
import type { AgendaDia, CitaAgenda, Hueco } from "../api";
import { ESTADOS } from "./estados";
import estilos from "./panel.module.css";
import { SelectorMiembro } from "./selector-miembro";

type Props = {
  agenda: AgendaDia;
  dia: string;
  hoy: string;
  ahora: string;
  equipo: { id: string; nombre: string }[];
  miembro: string;
};

const plural = (n: number, uno: string, varios: string) => `${n} ${n === 1 ? uno : varios}`;

/** CU-07 (RF-23, RF-24): citas en orden con su estado, huecos libres y la línea de la hora actual. */
export function AgendaDelDia({ agenda, dia, hoy, ahora, equipo, miembro }: Props) {
  const ruta = (fecha: string) => `/panel/agenda?fecha=${fecha}&miembro=${miembro}`;
  const activas = agenda.citas.filter((c) => c.estado !== "cancelada");
  const confirmadas = activas.filter((c) => c.estado === "confirmada").length;
  const sinConfirmar = activas.filter((c) => c.estado === "pendiente").length;

  const filas: { inicio: string; cita?: CitaAgenda; hueco?: Hueco }[] = [
    ...agenda.citas.map((cita) => ({ inicio: cita.inicio, cita })),
    ...agenda.huecos.map((hueco) => ({ inicio: hueco.inicio, hueco })),
  ].sort((a, b) => a.inicio.localeCompare(b.inicio));
  // La línea de "ahora" va antes de lo primero que aún no empieza; si ya pasó todo, al final.
  const siguiente = filas.findIndex((f) => f.inicio > ahora);
  const posicionAhora = dia !== hoy ? -1 : siguiente === -1 ? filas.length : siguiente;
  const lineaAhora = (
    <p className={estilos.ahora}>
      <span />
      Ahora, {hora(ahora)}
    </p>
  );

  return (
    <Pantalla>
      <header className={estilos.cabecera}>
        <div className={estilos.titulo}>
          <h1>Mi agenda</h1>
          <SelectorMiembro equipo={equipo} actual={miembro} dia={dia} />
        </div>
        <nav className={estilos.fecha} aria-label="Día">
          <Link className={estilos.flecha} href={ruta(sumarDias(dia, -1))} aria-label="Día anterior">
            <Icono nombre="atras" />
          </Link>
          <strong>{fechaConHoy(deClave(dia), hoy, "UTC")}</strong>
          <Link className={estilos.flecha} href={ruta(sumarDias(dia, 1))} aria-label="Día siguiente">
            <Icono nombre="adelante" />
          </Link>
        </nav>
        <p className={estilos.conteo}>
          <Chip>{plural(activas.length, "cita", "citas")}</Chip>
          {confirmadas > 0 && <Chip tono="verde">{plural(confirmadas, "confirmada", "confirmadas")}</Chip>}
          {sinConfirmar > 0 && <Chip tono="ambar">{sinConfirmar} sin confirmar</Chip>}
        </p>
      </header>

      <main className={estilos.lista}>
        {agenda.citas.length === 0 && (
          <p className={estilos.vacio}>
            {agenda.huecos.length === 0 ? "No tienes horario este día." : "No hay citas este día."}
          </p>
        )}
        {filas.map((fila, i) => (
          <Fragment key={fila.inicio + (fila.cita?.id ?? "")}>
            {i === posicionAhora && lineaAhora}
            {fila.cita && <FilaCita cita={fila.cita} />}
            {fila.hueco && (
              <Link
                className={estilos.hueco}
                href={`/panel/citas/nueva?inicio=${encodeURIComponent(fila.hueco.inicio)}&miembro=${miembro}`}
              >
                <Icono nombre="mas" tamano={20} />
                Libre de {rangoHoras(fila.hueco.inicio, fila.hueco.fin)}
              </Link>
            )}
          </Fragment>
        ))}
        {filas.length > 0 && posicionAhora === filas.length && lineaAhora}
      </main>

      <Link className={estilos.nueva} href={`/panel/citas/nueva?miembro=${miembro}`} aria-label="Nueva cita">
        <Icono nombre="mas" tamano={28} />
      </Link>
      <NavPanel activa="agenda" />
    </Pantalla>
  );
}

function FilaCita({ cita }: { cita: CitaAgenda }) {
  const { reloj, periodo } = partesHora(cita.inicio);
  const estado = ESTADOS[cita.estado];
  return (
    <Link className={`${estilos.fila} ${estado.cerrada ? estilos.cerrada : ""}`} href={`/panel/citas/${cita.id}`}>
      <span className={estilos.hora}>
        <strong>{reloj}</strong>
        {periodo}
      </span>
      <span className={estilos.quien}>
        <strong>{cita.cliente}</strong>
        {cita.servicio}, {cita.duracionMin} min
      </span>
      <Chip tono={estado.tono}>{estado.etiqueta}</Chip>
    </Link>
  );
}
