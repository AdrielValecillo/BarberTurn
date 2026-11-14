import type { ReactNode } from "react";
import { EnlaceBoton } from "@/components/ui/boton";
import { Icono } from "@/components/ui/icono";
import { Avatar, Chip, Contenido, Encabezado, Pantalla, Pie } from "@/components/ui/piezas";
import { diaYMes, fechaConHoy, partesHora, precio } from "@/lib/fechas";
import { formatoTelefono } from "@/lib/telefono";
import type { CitaDetalle } from "../api";
import { AccionesCita } from "./acciones-cita";
import { ESTADOS } from "./estados";
import estilos from "./panel.module.css";

const ORDINALES = ["Primera", "Segunda", "Tercera", "Cuarta", "Quinta", "Sexta", "Séptima", "Octava", "Novena", "Décima"];

type Props = {
  cita: CitaDetalle;
  hoy: string;
  /** Historial de avisos: lo arma la página con el dominio de notificaciones (doc 11). */
  avisos: ReactNode;
};

/** CU-08 (RF-26): datos de la cita y del cliente, con WhatsApp y llamada si hay teléfono. */
export function DetalleCita({ cita, hoy, avisos }: Props) {
  const { reloj, periodo } = partesHora(cita.inicio);
  const estado = ESTADOS[cita.estado];
  const ordinal = ORDINALES[cita.visitas - 1];

  return (
    <Pantalla>
      <Encabezado titulo="Cita" atras="/panel/agenda" />
      <Contenido>
        <Chip tono={estado.tono}>{estado.etiqueta}</Chip>
        <h1 className={estilos.horaGrande}>
          {reloj} <span>{periodo}</span>
        </h1>
        <strong>{fechaConHoy(cita.inicio, hoy)}</strong>
        <p className={estilos.tenue}>
          {cita.servicio}, {cita.duracionMin} min, {precio(cita.precioCop)}
        </p>

        <section className={estilos.cliente} aria-label="Cliente">
          <div className={estilos.persona}>
            <Avatar nombre={cita.cliente} claro />
            <p className={estilos.quien}>
              <strong>{cita.cliente}</strong>
              {cita.telefono && formatoTelefono(cita.telefono)}
            </p>
          </div>
          <p>
            {ordinal ? `${ordinal} visita.` : `Visita número ${cita.visitas}.`}
            {cita.ultimoCorte && ` Su último corte fue el ${diaYMes(cita.ultimoCorte)}.`}
          </p>
          {cita.telefono && (
            <div className={estilos.contacto}>
              <EnlaceBoton
                variante="secundario"
                compacto
                href={`https://wa.me/${cita.telefono.replace("+", "")}`}
                target="_blank"
                rel="noopener"
              >
                <Icono nombre="mensaje" />
                WhatsApp
              </EnlaceBoton>
              <EnlaceBoton variante="secundario" compacto href={`tel:${cita.telefono}`}>
                <Icono nombre="telefono" />
                Llamar
              </EnlaceBoton>
            </div>
          )}
        </section>

        {avisos}
      </Contenido>
      {!estado.cerrada && (
        <Pie>
          <AccionesCita />
        </Pie>
      )}
    </Pantalla>
  );
}
